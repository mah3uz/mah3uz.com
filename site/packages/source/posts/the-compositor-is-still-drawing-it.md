---
title: The compositor is still drawing it
published_at: 2026-11-10T09:00:00+06:00
topics: [linux, engineering, rust]
excerpt: Building easyshot taught me that the hard part of a Wayland screenshot tool isn't the capture protocol. It's the state you can't see, like a bar that's closed but still fading, a cursor painted into every frame, or a service started just by asking it a question.
art: /art/posts/compositor-drawing.svg
---
Taking a screenshot on Wayland is, at the protocol level, a solved problem. You bind a global, ask the compositor to copy an
output into a buffer you've allocated, wait for it to say it's done, and you have pixels. `grim` has done it in a few
hundred lines for years.

Building [easyshot](/projects/easyshot), a screenshot, annotation and recording tool for Hyprland, sway and niri, I spent
very little time on that part. The time went into things that weren't on the screen when I looked, or that I couldn't see
in a test: a bar that had closed but was still being drawn, a pointer painted into every frame, a desktop service that
started because I asked it a question. Most of them were found the same way, by using the tool on my own desktop and
noticing that something was off.

This is about the capture side. I've written separately about [recording a window you can't
see](/blog/recording-a-window-you-cannot-see).

## Freeze first, always

The first decision shaped everything after it. When you press the capture key, easyshot grabs a frame of every output
*before* it shows anything, and the area picker draws on that frozen frame. You're choosing a region of a still picture,
not of the live screen.

Many screenshot tools make this an option. easyshot doesn't. The decisions log is blunt about it:

> Freeze is always on; there is no native-selector option and no config key.

The alternative is to show a transparent overlay over the live screen, let the user drag, close the overlay, and then take
the picture. On Wayland that second step is unreliable. Closing your overlay and taking the shot is a race against the
compositor redrawing what was under it, and against whatever the user was trying to capture changing in the meantime. A
tooltip disappears because the pointer moved to drag. A menu closes because focus changed. Freezing first removes the race
instead of tuning a delay for it.

It also made other features honest:

- **Timed capture** is *pick, then count down, then take a fresh frame of what you picked.* I considered it the other way
  round, count down and then pick, and rejected it because it can't catch a menu that closes when you click. With pick
  first, you choose the area, open the menu during the countdown, and the menu is in the shot.
- **Capture previous** repeats the last *target*, not the last rectangle of pixels. If the target was a window and the
  window has since closed, you get a toast saying so, not a picture of whatever is now in that spot.
- **One capture at a time, nothing queued.** Capture keys get pressed twice, or pressed in the wrong order. While you're
  picking, another capture key switches the picker to that mode on the same frozen frame, and the same key closes it. Once a
  capture is committed, a new request is refused with a message. A queue would run a stale capture of a screen that has
  moved on.

The same reasoning applies to recording. A second press of the record key while a recording is starting or running is
refused. I considered making it stop the running recording, and the log records why not: it "turns a mistaken press into
a lost take."

## The bar that was still there

easyshot has a small capture bar: a row of buttons for area, window, screen, scroll and so on. You click Area, the bar
closes, the screen freezes, and you pick.

Except in the second round of testing on my desktop, the frozen frame had the bar in it. Faded, half there. One screenshot
came out with it squashed mid-animation.

The bar is a Wayland layer-shell surface, and I'd destroyed it before taking the frame. But destroying a surface doesn't mean
the compositor has stopped drawing it. Hyprland animates layer surfaces out. On my configuration the fade is 270 ms, and I
measured the surface still visible for about 250 ms after it had gone from my side.

![Waiting for a bar that's already gone: a fixed delay caught the fade, waiting for the fade plus 50 ms didn't](/art/posts/the-compositor-is-still-drawing-it/settle.svg)

The first fix was a fixed 150 ms wait before grabbing the frame. That's the kind of number that works on the developer's
machine and on nobody else's, and it didn't even work on mine. The real fix is a single *settle* step inside the capture
coordinator. On Hyprland, a small provider reads the compositor's animation settings (whether animations are on, and the
longer of the two layer-out animations), and waits that long plus 50 ms for the frame to be repainted. On other compositors,
which don't animate layers away, it waits 150 ms.

There was a second version of the same bug in the tray. When you start a capture from the tray menu, the click reaches
easyshot *before* the panel hides its menu. My panel, DankMaterialShell, hides it 80 ms after the click and fades it over
150 ms, so a capture from the tray waits 230 ms.

The test that proved the fix is the part I'll remember. It grabbed a frame through the real capture path and counted pixels
of the bar's colour in the area where the bar had been. Its first run failed: plenty of "bar" pixels. I spent a while
convinced the fix didn't work before realising the test was counting the area picker's own 30% dim overlay as bar. With
that corrected, it counted 0 of 96,883 pixels with the settle step and 96,837 with it removed. The product had been right
and the test had been wrong, and the only way to tell was to look at the actual pixels.

## Pixels on a fractional scale

Fractional scaling shook out two more bugs early, in the spikes before the real code.

**Rounding.** At a scale of 1.5, a region of logical points becomes a region of physical pixels with fractions in it. The
first version rounded the origin and the size separately, and lost a pixel on the right edge. The rule now written in the
plan is to round the *edges*: the left edge and the right edge each become a pixel position, and the width is the
difference. A 304 × 151 drag at 1.5 now produces exactly the crop you'd expect.

**Which display is which.** GPUI, the UI framework easyshot is built on, reports displays with bounds. On fractional
outputs those bounds are divided by the *integer* scale, so matching a GPUI display to a Wayland output by its rectangle
fails exactly where it matters. easyshot matches them by output name instead, through the stable ID GPUI derives from it.

## Scroll capture, and three bugs with one symptom

Scrolling capture takes a tall image of something longer than the screen: you pick an area, scroll (or let easyshot
scroll), and frames are stitched into one picture. It works on plain pixels, with no access to the application, so it
finds how far the content moved between two frames by matching them.

It broke three times with the same symptom: only the first frame kept, the preview stuck.

**Moving content.** In the second round, a page with an animation in it never stitched. The match between two frames is a
normalised cross-correlation with a threshold of 0.9, and a region of the page that animates in place drags the score of
the whole frame below it. Every tick reported "no overlap", and the preview only redraws when something is appended. The
fix masks out rows that change without scrolling before matching. A page that scrolled itself went from 600 pixels stitched
to 1,137.

**The pointer.** In the fifth round, manual scroll capture failed again on my desktop while passing in a headless sway. I
built a replay tool that feeds recorded frames through the stitching loop on a virtual clock, and it stitched them fine,
which meant the bug was upstream of the stitcher. Watching the live desktop with the pointer moved by script found it: the
loop only accepted wheel scrolls while the pointer was *inside* the region. After you draw a region, the pointer rests on
its bottom-right corner, and the region's edge is exclusive, so the pointer was one pixel outside. The check was removed;
fifteen notches of the wheel then stitched a page from 1,290 to 2,977 pixels cleanly.

**The cursor.** In the same session, auto scroll had arrows and hover effects stitched into the image. Hyprland was
drawing a software cursor on my machine, which means the pointer is part of the frame no matter what you ask the capture
protocol to leave out. Auto scroll now parks the pointer on its own caption after each step, so nothing under it
highlights, and a whole page came out at 10,974 pixels tall without a single arrow in it.

There was a fourth, smaller one: Chromium scrolls smoothly, so two frames taken right after a scroll can be identical
because the scroll hasn't *started* yet. Auto scroll now waits up to 400 ms for motion before it waits for things to
settle. After that, nineteen steps in a row were appended, in 13 seconds.

A scrollbar thumb also showed up repeated down the whole image, because to the stitcher it looked like a static strip at
the side that happened to move. It's cropped from the saved image now.

Pixel stitching has limits that no amount of tuning will fix, and I'd written an instruction to myself in the plan for
exactly this case: *if you can't make it work, say so.* So the manual says so. It works for one scrolling column with static
decoration. It's never reliable for headers that stick or appear partway down, for video, for rows that repeat exactly, or
for pages that load more content as you scroll. A browser extension can do better because it can read the page's real
scroll position and hide fixed headers. A Wayland screen tool can't, and pretending otherwise would just move the failure
to the user.

## Don't wake a service by asking it a question

Some bugs only happen at login.

easyshot's daemon starts with the session, and it shows notifications. At login, there's a moment where it can start
before your notification daemon has claimed its name on the session bus. On D-Bus, sending a message to a name nobody owns
can *activate* a service for that name: the bus looks for an installed service file and starts it. So a single "what can
you do?" call at start-up could launch whichever notification server happened to be installed, which would then hold the
name, and your real one would fail to start.

The fix is to ask the bus, not the service. easyshot lists the names and their owners, sends nothing to the notification
name until it has an owner (or a notification actually has to be shown), and learns the server's capabilities when it
appears. It's a few lines, and it follows a rule I'd apply to any program on a shared machine: looking shouldn't change
anything.

Two more came out of the first real session on my desktop:

- **The tray icon was invisible.** Qt-based panels draw a themed symbolic icon in the text colour, which made mine black
  on a black bar. easyshot now sends a full-colour pixmap and an empty icon name.
- **Autostart didn't.** Plain Hyprland, sway and niri ignore XDG autostart files. The package enables a systemd user
  service globally instead, with `ConditionUser=!@system` so it doesn't start inside the display manager's login screen.

## Compositors behind a wall

easyshot supports three compositors, each with its own IPC and its own gaps in the protocols. The temptation in that
situation is an `if hyprland { … }` wherever it's needed. Six months later, nobody can say what the program does on any one
of them.

![The app sees capabilities, not compositors: providers per capability, gathered into one set of Caps](/art/posts/the-compositor-is-still-drawing-it/providers.svg)

Instead, each capability (capture, the window list, pointer position, recording, clipboard, tray, notifications) has an
ordered list of *providers*, probed at start-up. Generic Wayland providers are chosen by which protocol globals the
compositor offers, not by its name. The compositor modules add only what protocols can't give, such as a window's position
and stacking order or the pointer's position. The rest of the app sees a set of capabilities and nothing else. Where one is
missing, the feature degrades in a written-down way. With no window list, window capture crops from the frozen frame;
with no virtual input, auto scroll is hidden.

A check in the build enforces it: it fails if `hyprctl`, `HYPRLAND_INSTANCE_SIGNATURE`, `SWAYSOCK` or `NIRI_SOCKET`
appears anywhere outside the three compositor folders. `easyshot doctor` prints which provider was chosen for each
capability and why the others were rejected, which is the first thing I'd want when someone reports a bug from a
compositor I don't run.

Two dependency choices came from the same place. easyshot has its own small Wayland client instead of using `libwayshot`,
which can't share a connection, drops the output's transform and returns RGBA where everything else works in BGRA. And it talks to niri with
its own types instead of the `niri-ipc` crate, because that crate is GPL-3.0 and would have made the MIT binary a GPL work.

## Tested where it runs

easyshot has around 2,100 tests, and they run in four places: headless GPUI windows for the editor and settings, a separate
headless output on Hyprland, a headless sway with virtual input, and niri nested inside a window. A standing rule was that
no test ever opens a window, grabs a frame, injects input or touches the clipboard on the session I'm actually using.

Those environments caught a lot. They didn't catch any of the bugs above. Each of those needed a real compositor, a real
panel, a real pointer, real animations, and a person noticing something was wrong. So before release, easyshot went through
five rounds of hand-testing on my own Hyprland desktop, between 3 and 11 November, each with a checklist and each producing
a list of fixes. The second round found the fading bar and the animated page. The fourth found the silent recordings and a
toast that stayed open forever after you hovered it. The fifth found the scroll pointer, the software cursor and a window
recording that ended when the window moved.

The architecture document opens with a table of what has been run where, followed by this sentence:

> Only what the table lists has been observed; everything else in this document is design that has not been run on that
> compositor.

niri is listed as supported but not run on a real session, and it says so. After seventeen years of reading other
people's documentation at three in the morning, the thing I value most in it is that it tells me what it doesn't know.

## What carries over

- **Remove races instead of tuning delays.** Freezing the screen first made a whole class of timing bugs disappear.
- **When you must wait, wait for the real thing.** Read the compositor's animation settings rather than guessing a
  number.
- **When a test fails, look at the pixels** before you decide which side is wrong.
- **Don't ask a question that has side effects.** On D-Bus, a call can start a service.
- **Keep platform differences behind one wall,** and make the build enforce where the wall is.
- **Say what you haven't tested,** and what can't be made to work.

None of these are about screenshots really. They're about writing software that has to behave on machines you don't control,
in conditions you didn't think of, which is most software.
