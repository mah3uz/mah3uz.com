---
title: Recording a window you can't see
published_at: 2026-11-11T09:00:00+06:00
topics: [linux, rust, engineering]
excerpt: "\"Record this window\" sounds like the easiest feature in a screen recorder. On Wayland it took my own capture pipeline, a recorder I couldn't hide from, an audio server with a long memory, and a parent-death signal the kernel quietly drops."
featured_image: art/posts/recording-window.svg
---
"Record this window" is the feature everyone assumes is easy. You point at a window, you press a key, you get a video of
that window. On X11 it more or less was: every client could see every other client's windows, so a recorder just asked the
X server for a window's pixels and got them.

Wayland deliberately took that away. One application can't see another's windows, can't read the screen, and can't
inject input, unless the compositor provides a protocol for it and decides to allow it. As someone who has spent seventeen
years tightening what processes on a server are allowed to see, I think that's the right design. It also means a
screen recorder on Wayland has to ask the compositor for everything, and the answers differ between compositors.

This is the story of how window recording works in [easyshot](/projects/easyshot), the screenshot and recording app I
released this week, and of four things that went wrong on the way. Most of them weren't in the protocol. They were in the
layers around it.

## The obvious routes, and why I didn't take them

easyshot doesn't encode area and full-screen video itself. It drives **gpu-screen-recorder** where it's installed and
**wf-recorder** where it isn't, both as child processes. gpu-screen-recorder is very good: it captures straight from the
GPU and encodes on the GPU, so recording a 1440p display costs almost nothing.

Its window mode, though, is X11 only. On Wayland the manual offers one route for a window, `-w portal`, which goes through
the desktop's screen-cast portal. The portal shows its own dialog and asks the user to choose a window. In easyshot the
user has already chosen one: they picked it in easyshot's own picker, with its title and icon and workspace, a second ago.
Asking again in a different dialog, with a different list, is a bad experience and an opportunity to record the wrong
window.

You can skip that dialog on Hyprland by setting a custom picker program in xdg-desktop-portal-hyprland's configuration. I
wrote that option down and rejected it in the same line of the decisions log:

> It changes screen sharing for every app and works only on Hyprland.

A tool shouldn't change how your video calls share the screen as a side effect of being installed. That's the kind of
change I'd be annoyed to find on a machine I administer.

So the first version did the simple thing: it recorded the window's *rectangle*. That's fine until something covers the
window, at which point the cover is in your video. Move the window to another workspace and the recording carries on
filming whatever is now in that part of the screen. During my fourth round of testing on my own desktop I did exactly
that, and got a video of my editor instead of the browser I meant to record.

## Asking the compositor for one window's frames

Wayland now has a proper answer. `ext-image-copy-capture` is a protocol for copying frames out of the compositor, and
`ext-foreign-toplevel-image-capture-source` lets you name a *window* as the thing to copy from rather than an output.
The compositor hands you that window's own buffers whether it's covered, partly off screen or on a workspace nobody is
looking at. Hyprland supports both.

easyshot already spoke this protocol for screenshots, through its own small Wayland client crate (the only crate in the
project allowed to contain `unsafe`). What it didn't have was a video pipeline. So I built one.

![Recording one window: the capture thread, a one-slot mailbox, a pacer on the GStreamer clock and the encoder](art/posts/recording-a-window-you-cannot-see/pipeline.svg)

A window recording runs three threads:

1. **Capture.** A thread with its own Wayland connection requests frames of the window, throttled to the target frame rate.
   Asking for every frame the compositor would give and throwing most of them away cost about three times as much as only
   asking when a frame is due.
2. **A one-slot mailbox.** Each new frame replaces the one waiting, if any. The newest frame always wins. If the encoder
   falls behind for a moment, the recording drops a frame rather than building a queue, so the video never drifts
   further and further behind real time. I've debugged enough log shippers with unbounded buffers to never want another.
3. **A pacer** on the GStreamer pipeline's clock takes whatever is in the mailbox at each tick and feeds it to the
   encoder.

The pacer exists because of a property of Wayland that surprises people: a window that doesn't redraw doesn't produce
frames. Record a terminal sitting at a prompt and you might get two frames in ten seconds. Plenty of players and editors
handle variable frame rate badly, so the pacer repeats the last frame on every tick and the file comes out at a constant
rate. If the window is resized mid-recording, its frames are letterboxed into the size of the first one, because an H.264
stream can't change size halfway through.

Encoders are tried in order: NVIDIA's `nvh264enc`, then VA-API's `vah264enc`, then `x264enc` in software. Each is
*pre-rolled* before the recording clock starts. That one detail matters more than it looks. A hardware encoder that fails
because of a driver problem fails when it gets its first buffer. Without the pre-roll, that's three seconds into your
recording, and the user has already done the thing they wanted to show. With it, easyshot finds out before the clock
starts and moves on to the next encoder. In the prototype, `nvh264enc` encoded 1080p at 30 frames a second for 6.4% of one
core; `x264enc` on its fastest preset took 51%.

On Hyprland, a window on a hidden workspace recorded at 114 frames a second, and a window underneath a fullscreen one at
60. System sound and the microphone are recorded as separate Opus tracks in the same file, so either can be muted or
dropped later without touching the other.

Not every compositor offers a window source. niri 26.04 doesn't, so on niri easyshot still records the window's rectangle.
That's a capability the app checks at run time rather than a special case, and the recording panel says what it's going
to do.

## The window that moved and ended the recording

With the new recorder in place, the fifth round of testing found the next problem within minutes. I started recording a
window, moved it to another workspace, and got "Something went wrong" and no file. The log said:

```
capture failed: Value(BufferConstraints)
```

`ext-image-copy-capture` tells the client what kind of buffer to allocate: size, format, stride. When a window changes
size, the compositor sends new *buffer constraints* and fails the frame in flight, and the client allocates new buffers and
carries on. My code treated a failed frame as a failure and retried a few times before giving up.

What I hadn't accounted for was Hyprland animating the move. Each step of the window's resize animation sends new
constraints. A probe I wrote afterwards on Hyprland 0.57.2 found that each animated resize fails *a few hundred frames*,
none of which actually end the stream. "Retry N times" was always going to lose.

The fix replaced the retry counter with a small state machine. New constraints are expected and are never counted as
errors; the recording holds its last good picture while the window settles. A window that really has gone, because it was
closed, ends the recording, keeps the file and shows a notice. I care a lot about that last part. Throwing away a recording
because of a transient error is the worst thing a recorder can do: the moment you were filming won't happen again.

One small limit is still written in the manual: during a move animation the video holds the last frame instead of showing
the window sliding. I can live with that.

## The control bar you can't hide

Recording a whole display raises an older question: where does the recorder's own interface go? easyshot shows a small
control bar while recording, with a timer, pause, mute buttons and stop. Nobody wants that bar in their video.

Hyprland has a layer rule, `no_screen_share`, for exactly this. I tried it, and the bar came out in the video as a black
rectangle. That turned out to be the rule working as designed (the compositor paints over such surfaces in screen copies,
it doesn't cut them out), but it also didn't matter much. As far as I can tell from its source, gpu-screen-recorder
doesn't capture monitors and regions through the compositor at all: it reads the framebuffer being scanned out to the
display, through a small helper that holds `CAP_SYS_ADMIN`. A compositor rule can't apply to a request the compositor
never sees. niri's equivalent
rule doesn't cover it either, and sway has no such rule.

I could have shipped hide rules for the compositors and recorders where they work. The decisions log rejects that:

> Shipping rules for some compositors only, which would make the same recording differ by compositor.

Instead there are no hide rules anywhere, and the bar is *placed* rather than hidden. With a second monitor, the bar goes
to the monitor you aren't recording. With one monitor, it sits in the bottom-right corner, is recorded, and can be cropped
in the trim viewer. For an area or a window, the bar goes outside the rectangle. It's less magical, and it behaves the same
everywhere, which is the property I'd pick every time.

While I was in there, gpu-screen-recorder exited with code 51 ("capture target invalid") when I recorded an area on my
second monitor. It wants a region in global logical coordinates, and easyshot had sent coordinates relative to the
output. On a single monitor at position 0,0 those are the same number, which is why it took a two-monitor desk to notice.
easyshot now runs `gpu-screen-recorder` once with a tiny region and `-o /dev/null`, reads the monitor list it prints, and
matches its names and positions to the outputs the compositor reports. Asking the program what it thinks is cheaper than
assuming you agree with it.

## The recording that was silent forever

In the fourth round every new recording was silent. Not quiet: ffmpeg measured the audio track at -91 dB, which is
digital silence. The microphone was fine, the system sound was playing, and gpu-screen-recorder was capturing.

The cause was a mute button I'd pressed in an earlier recording. gpu-screen-recorder has no mute command. Version 6.1.6
has no signal, flag or control for it. So easyshot mutes a track by muting the recorder's *PipeWire stream*, which works
instantly and touches nothing else on the system. What I hadn't known is that WirePlumber, the session manager on top of
PipeWire, remembers per-stream settings by stream name in its `stream-properties` state. gpu-screen-recorder's streams
always have the same names. One press of Mute in one recording was being restored to every recording after it.

The fix is two lines of behaviour: easyshot unmutes its own streams when a recording starts, and again just before it
stops. I'd looked at the alternatives when designing the mute button and they're both worse:

- **Muting with an ffmpeg volume filter after the recording stops.** That isn't live, and the raw file on disk still holds
  the voice you muted until the filter runs. If easyshot crashes in between, the thing you muted is in a file. That's a
  privacy bug waiting for a bad day.
- **Routing through a null sink and a loopback.** Around 200 ms of extra latency and PipeWire nodes left behind when
  something exits badly.

As a sysadmin I recognise the shape of this bug. It's the service that picks up a setting from a state file you didn't know
existed. The fix is rarely to stop the state from being kept; it's to state explicitly what you want every time you start.

The same round changed a default. Recordings now capture system sound unless you turn it off, and the microphone stays off
unless you turn it on, because the first silent recording surprised me, and I wrote the thing.

## Making sure the recorder dies with you

The last part of this story is about processes, and it's the part I'm happiest with.

gpu-screen-recorder and wf-recorder are child processes of the easyshot daemon. If the daemon crashes, or the session ends
badly, those children must stop. A recorder left running after its parent has gone is filling a disk somewhere, holding
your microphone open, with no interface left to stop it.

On Linux the usual answer is `prctl(PR_SET_PDEATHSIG, SIGINT)`: ask the kernel to send the child a signal when its parent
dies. The original plan said exactly that. It doesn't work here, and the reason is a detail I knew from the operations side
rather than from programming. The kernel clears the parent-death signal when a process executes a binary that is setuid,
setgid or has file capabilities. gpu-screen-recorder's capture helper is very often installed with capabilities, since
that's how it reads the framebuffer. The child would set the signal, `exec` the recorder, and lose it, silently.

![If the daemon dies, so does the recorder: a watcher reading a pipe, and the signal ladder on EOF](art/posts/recording-a-window-you-cannot-see/supervision.svg)

So every recorder runs in its own process group beside a tiny `/bin/sh` watcher. The watcher reads from a pipe whose write
end only the daemon holds. Nothing is ever written to it. When the daemon exits for any reason, including `SIGKILL` and the
out-of-memory killer, the kernel closes its end, the watcher's read returns end-of-file, and the watcher sends `SIGINT` to
the whole group, then `SIGKILL` ten seconds later if anything is still there.

It's the oldest trick in Unix process supervision: a pipe is closed when its last holder dies, however it dies. No
signals to configure, nothing that a capability can strip.

Stopping a recording on purpose is a ladder too. easyshot asks gpu-screen-recorder to stop over its control interface and
waits five seconds, so the file is finalised properly. Then `SIGINT`, then `SIGKILL` after ten more. wf-recorder has no
pause, so pausing it stops it, and the segments are joined with ffmpeg's concat demuxer when the recording ends.

## What I'd tell someone building one

- **Use the window source where it exists.** On Hyprland and sway, `ext-image-copy-capture` with a toplevel source gives
  you a window's own frames whatever is on top of it. Check for it at run time and fall back honestly where it's missing.
- **Expect buffer constraints to change constantly.** An animated resize is hundreds of failed frames, not an error.
- **Never queue frames.** One slot, newest wins, and a pacer for a constant frame rate.
- **Pre-roll the encoder** before the clock starts.
- **Assume you can't hide from a recorder that reads the scanout.** Place your interface instead.
- **State your audio settings on every start,** because something in the session is remembering the old ones.
- **Don't trust `PR_SET_PDEATHSIG` across an `exec` of a binary with capabilities.** A pipe that closes when you die can't
  be stripped.

None of this shows in the interface. You pick a window, press a key, and get a video of that window. That's how it should
be: the work that goes into the boring path is the work nobody should ever notice.
