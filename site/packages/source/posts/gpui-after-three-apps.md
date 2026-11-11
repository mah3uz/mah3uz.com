---
title: GPUI, after three apps
published_at: 2026-11-08T09:00:00+06:00
topics: [rust, linux, engineering]
excerpt: "I've now shipped three native apps on GPUI, the UI framework behind the Zed editor: a system monitor, a terminal multiplexer and a screenshot tool. Each one pushed it somewhere different. This is what I know now about pinning it, patching it, budgeting it, and where it still runs out."
featured_image: art/posts/gpui-three-apps.svg
---
A few weeks ago I wrote about [building Sysman's interface on GPUI](/blog/native-linux-apps-in-rust-with-gpui), and
mostly about the charts I had to write and what it took to ship a native binary on Linux. Since then I've built two more
applications on it, and they couldn't be more different from a system monitor or from each other.

[Insensical](/projects/insensical) is a terminal multiplexer whose window draws dozens of live terminals at once, each
one a grid of styled cells that can change thousands of times a second. [easyshot](/projects/easyshot) is a screenshot
and recording tool whose interface is mostly *not* windows: full-screen overlays, floating toasts, preview cards stacked in
a corner, a control bar that follows you across monitors, all of them Wayland layer-shell surfaces.

Three apps, three different kinds of stress. GPUI handled all of them, and each one found a different edge. This is the
longer version of what I'd tell anyone thinking of using it.

## What GPUI is

GPUI is the UI framework the Zed team built for their editor. It's written in Rust from top to bottom and draws everything
on the GPU: Metal on macOS, and on Linux through wgpu (Vulkan, or GL where Vulkan isn't available). Text goes through
CoreText on a Mac and cosmic-text on Linux.

The programming model is a hybrid that takes a day to get used to. Your application's state lives in *entities*, owned by
the app and reached through handles. A *view* is an entity that knows how to render: each frame it builds a tree of
*elements* (divs with flexbox-style layout, text, images, or your own elements that paint directly). Elements are cheap
and rebuilt; entities persist. When an entity changes, you tell GPUI it has, and the views that depend on it render again.

What you can actually *paint* is a short list. The Insensical architecture document puts it precisely:

> gpui exposes a fixed set of primitives (quads, paths, shaped text, glyphs, images). It has no API for a custom shader,
> pipeline or texture.

That sentence decided more of the design of all three apps than any other fact about GPUI. Everything you see in them is
rectangles with rounded corners and borders, vector paths, glyphs and bitmaps. There's no escape hatch to your own GPU
code. If you need something else, you build it out of those, or you draw it on the CPU and hand GPUI an image.

![What GPUI gives you, and what you build: five primitives at the bottom, and each app's own layer on top](art/posts/gpui-after-three-apps/primitives.svg)

I've come to see that limit as healthy. Every pane, overlay and card in my apps is an ordinary element, so they compose:
a terminal can sit inside a floating window inside an overview, with a thumbnail of it somewhere else, and nothing special
is needed for any of it. I explicitly rejected drawing Insensical's terminals with a platform-specific renderer in a child
surface, because it *"would break the rule that a pane is an ordinary element, which is what lets floats, overlays and
thumbnails compose for free."*

## Getting it at all

The first surprise for most people is that there's no "GPUI 1.0" on crates.io from its authors. Zed develops GPUI inside its
own repository, for its own needs, and the public API moves when Zed needs it to.

Insensical and easyshot both use `gpui-pre`, a crates.io snapshot of a specific Zed commit published by the GPUI-Kit project, with
`gpui-component` from the same project on top for buttons, inputs, menus and the like. Both are pinned with `=`:

```toml
gpui = { package = "gpui-pre", version = "=0.3.10" }
gpui_platform = { package = "gpui-pre-platform", version = "=0.3.10", features = ["font-kit", "wayland", "x11", "runtime_shaders"] }
gpui-component = "=0.8.1"
```

I'd have preferred Zed's git source at a pinned revision, and recorded why I didn't use it: the component library requires
`gpui-pre`, and any other source would put *two* copies of GPUI in the dependency graph. That's the failure I warned about
in the Sysman post. It compiles, it links, and then types that look identical aren't, or two copies fight over the same
window. easyshot's build has a check, `cargo tree -d` filtered for GPUI and zbus, that fails if a second copy ever
appears, like the one I described for Sysman.

## Two ways to live with a young toolkit

Here the two newer apps went in opposite directions, and I think both were right.

![Two ways to live with a young toolkit: easyshot carries ten patches as commits on a vendored copy, Insensical uses GPUI unpatched](art/posts/gpui-after-three-apps/patches.svg)

**easyshot patches GPUI.** The vendored copy is GPUI exactly as published on crates.io, and the patches are ordinary git
commits on top of it. The decisions log describes it: *"copied as-is from crates.io and our patches are git commits on
top, so the patch set is the diff."* No patch files, no scripts that apply them. `git log -- vendor/` is the list, and
moving to a new GPUI version means replaying those commits.

There are ten of them, and nearly all are about Wayland:

- **P1** adds a margin API for layer surfaces, so a pinned screenshot can be positioned and moved.
- **P5** and **P8** add custom cursors (a crosshair with a size readout, a pen, a text cursor per tool) through GPUI's normal
  cursor path. A side channel would have been simpler, and *"would be overwritten by that cache."*
- **P6** gives a drag a picture, so dragging a preview card out to a chat shows its thumbnail.
- **P7** has layer surfaces report server-side decorations, which removes padding GPUI reserved for window borders that
  layer surfaces don't have.
- **P10** offers file drags as Copy only.
- **P11** and **P14** give tooltips an app-wide delay and make them hide by themselves after a reading time.
- **P12** makes element opacity public, so a custom element can fade an image it paints.
- **P13** clears hover when the pointer leaves a window. More on that one below.

**Insensical doesn't patch GPUI at all.** Its architecture document says it's used unpatched, notes the two patches that
would be worth having (activating a window with a token received from elsewhere, and possibly a sprite-sorting fix), and
says that any patch would be kept as a short documented series and offered upstream. Instead it works around what it
meets:

- GPUI's `baseline_offset` adds a font's descent as if it were positive, while its text systems report it as negative, so
  text sits a descent too low. Insensical's grid works out the baseline from the ascent and descent itself.
- On Linux GPUI learns the desktop's light or dark appearance only after the first frame, and says "light" until then,
  so a dark desktop can get a flash of the light theme. Insensical asks the settings portal before its window opens.
- GPUI has no way to activate a window with an activation token from another process, so clicking a notification can't
  focus the window on every compositor. On Hyprland it works with `focus_on_activate`; elsewhere the window is marked
  urgent. The limit is documented, not hidden.

The difference comes down to *where the gap is*. easyshot's needs were in GPUI's platform layer: what a layer surface can
do, how a cursor is set. There's no way to reach those from outside the framework. Insensical's needs were inside the
element tree, where you control what's drawn. My rule now: patch when the gap is in the platform layer you can't reach;
work around when the gap is in what you draw, and keep the workaround next to a test.

## Set a budget before you write the code

Before Insensical's grid existed, its decisions log already had this row:

> gpui for the interface, at most 4 ms of UI-thread CPU per worst-case 200×60 frame.

Four milliseconds leaves room for the rest of the window and for a 120 Hz display, where a whole frame is 8.3 ms. And the
row named what would happen if GPUI couldn't meet it:

> If a change pushes the UI-thread figure past 8 ms with no way back, gpui is the wrong toolkit for this product; iced with a
> custom wgpu grid widget is the named alternative.

![A frame budget, set before the code: measured at 2.0 ms, budget at 4 ms, a different toolkit past 8 ms](art/posts/gpui-after-three-apps/budget.svg)

The worst case it's measured on is a full 200 × 60 grid where every cell has unique colours, the worst styling a program
can produce. It measures 2.0 ms at the median. I haven't needed the alternative. But writing it down before I started meant
every performance decision afterwards had a number to be judged against, and a clear point at which to stop arguing and
change course. I wish I'd done the same for every project I've had to rescue.

## Drawing a terminal out of five primitives

A terminal is the most demanding thing I've drawn with GPUI: thousands of cells, each with a character, colours, bold and
italic, underlines, and the screen can change every few milliseconds. Here's what it took to stay inside the budget.

**No text is shaped per frame.** Letting GPUI shape every cell of a heavily styled screen measured 14 ms, several times
the budget. Now glyphs are resolved once into a cache, by
character and style, and placed by cell position. A terminal is a grid; there's nothing to shape.

**Rows are cached until the engine says they changed.** The terminal engine marks rows dirty. A row that isn't dirty
reuses what it painted last time.

**Panes are cached elements.** What a pane drew last frame is reused until its own view says it has changed or its size
has. A busy build in one pane costs the panes beside it nothing. Not redrawing unchanged panes took a frame with six panes
from 4.8 ms to 1.5 ms, and memory with seventy panes open from 365 MB to 74 MB.

**Fewer, bigger primitives.** Adjacent cells with the same background become one rectangle. Each grid paints in two layers,
because primitives painted outside a layer each cost a search in GPUI's scene.

**Box-drawing characters are geometry.** Line-drawing, block and Powerline characters are painted as rectangles and paths on
exact device pixels rather than taken from a font, so the lines of a `tmux`-style border or a table meet their neighbours
with no gaps.

**Frames are pulled, never pushed.** The terminal engine's Rust types can't be sent between threads, so each terminal lives
on a thread of its own and the interface asks it for a plain-data frame of the changed rows when it's about to paint. During
a flood of output the terminal advances through many states between two paints, and the intermediate ones are never built.
Output throughput is set by how fast the engine parses, not by how fast GPUI draws.

## The rebuild that cascades

GPUI has one behaviour that took me two attempts to work with. When a view changes, GPUI rebuilds every view *above* it in
the tree as well. Usually that's cheap. In a window full of terminals, it isn't.

Each pane in Insensical has a small state line under its header: running, waiting, done. I wanted the "running" mark to
turn slowly, like a spinner. The first decision was simply no: *"The state line under a pane's header doesn't animate,"*
because GPUI redraws the window whole, and motion would redraw every terminal at around 2 ms each, ten times a second.

Later I found a structure that made it possible. The window is built in three layers, and the marks live where their changes
rebuild nothing else. Marks step ten times a second while any pane is running. There's a test with a long name,
`a_step_of_the_turning_mark_builds_nothing_again`, which checks it: ten steps used to build the window ten times; now they
build it once.

The same work turned up a subtle one at fractional scaling. GPUI snaps a view laid out on its own and the same view laid out
inside the window to *different* pixels at a scale like 1.5. Mixing the two made anything centred shake by one pixel on each
animation step. The fix was to lay it out one way, always.

## Layer shell: GPUI off the beaten path

easyshot is where I went furthest from what GPUI is used for in Zed. Almost nothing in it is a normal window. The area
picker is a full-screen layer surface on every output; toasts and the preview deck are small surfaces anchored to a corner;
the recording bar sits on top of everything; pins float above other windows.

Each kind needed a decision about keyboard focus. The capture bar takes the keyboard only when you click it, so it never
locks your typing. The recording bar never takes it at all, so the app you're recording keeps receiving keys while you
record it.

Then came the bug that led to patch P13. A toast with an Undo button stayed open forever once you'd hovered it. Toasts pause
their timer while hovered, so you can read them, and they never un-paused. The toast's input region is only the card, so
moving the pointer off the card means leaving the surface entirely. GPUI does send a mouse-exited event, but it doesn't clear
its record of where the mouse is, and in the next refresh it decides the pointer is still over the button. The same bug was
in the pin's close button, in the Settings home screen and in sliders. One patch fixed GPUI, and a single shared clock now
owns every toast's time and hover state, with a build check that fails if any toast is timed by its own timer.

A few more lessons from the same area:

- **Pay the cold start once.** The first layer surface GPUI opens is noticeably slow. The daemon opens and closes a 1 × 1
  transparent surface at start-up, so the first real overlay, when you press the capture key, is instant.
- **Change the input region, not the surface.** The preview deck fans out when you hover it. Resizing the surface on hover
  would move it under the pointer, which changes the hover, which resizes it. Now the surface keeps its fanned size and only its
  input region changes, so the pointer's position on the surface never moves.
- **Match displays by name.** On fractional outputs GPUI divides display bounds by the integer scale, so matching a display
  to an output by its rectangle fails. Match by the output's name.

## When the primitives run out

The fixed primitive set shaped some features directly:

- **Masks are rectangles only.** Redaction rotated with the image can't be a GPUI mask, so it's a patch of pixels prepared
  on the CPU with transparency outside the shape.
- **There are no element transforms.** A countdown that shrinks and fades as it ends is done with spring timing on opacity
  and size rather than a scale transform.
- **One renderer for what you see and what you save.** easyshot's editor preview and its export both draw annotations with
  tiny-skia on the CPU, from the same draw list. What you see in the editor is exactly what lands in the file, which matters
  more to a screenshot tool than drawing the preview on the GPU.

And two image lessons from Insensical. Small pictures had a dark rim because GPUI sampled them between their own pixels and
the transparent black beside them in its texture atlas, so images are now rasterised at exact device pixels. And the
component library's root element filled the window with an opaque background, which quietly defeated a transparent window.

## Text, input and accessibility

Input methods are the clearest gap I've hit. The text fields in Insensical's window read the finished text of a key press,
so text from an input method arrives once it's committed, but nothing is shown while it's still being composed. Showing that
needs a field to implement GPUI's input-handler trait, which a field of plain data can't. Terminal panes are different: with
`input-method = true`, the composition is shown at the cursor.

Smaller ones: by default GPUI hides the pointer while you type, which in a drawing app means pressing Space or a tool's
letter makes the pointer vanish until you move the mouse, so easyshot turns that off at start-up. On Linux, GPUI reports
Ctrl+Shift+] as `ctrl-}`, so key bindings use the shifted character. And a variable font I bundled rendered at its
lightest weight unless the weight was chosen explicitly.

Accessibility is better than I expected for a young framework. GPUI builds an AccessKit tree from every element that has
both an id and a role, which reaches screen readers through AT-SPI on Linux. Every component in easyshot's own UI library
sets a role, a label and a value; Insensical announces state changes through live regions and uses GPUI's own tab stops
and focus styles. Checking it with Orca is still manual.

## Linux and macOS are different platforms

Insensical also runs on macOS, and GPUI hides less of the difference than you'd hope:

- A point is one pixel on a Mac and one and a third on Linux, so the default text size is 13 points on one and 12 on the
  other to come out the same.
- A Mac counts the title bar in a window's bounds.
- An icon font has to be registered with CoreText as well as with GPUI, or icons printed by a program come from the system's
  last-resort font.
- Notifications go through GPUI on a Mac, which requires an app bundle, and through the daemon over D-Bus on Linux.
- GPUI's platform can only be created on the main thread on a Mac, so window tests run under nextest, one process each.

## What it costs to build

GPUI is a big dependency, and it shows in the build:

- It's too slow to use unoptimised, so every project builds dependencies at `opt-level = 2` even in development.
- Every test binary links GPUI and wgpu. In easyshot about half of each binary was debug information, and the debug
  target directory reached 483 GB. Relinking after a change wrote gigabytes and stalled my desktop on disk I/O. Line tables
  only, no incremental builds for the workspace and no debug info for dependencies fixed it.
- GPUI's off-screen test scheduler occasionally hangs at the very end of a window test, about one run in twelve in
  Insensical. It doesn't happen in the real application, and the test runner has a time limit for it.

## Would I choose it again?

Yes, for the same kind of software. If the job is a native app that should feel like part of a Linux desktop, draw a lot of
data quickly and run on a modest machine, GPUI is the best option I know of in Rust. It's fast, the programming model holds
up as an app grows, and having layout, text and drawing in the same language as everything else is worth a great deal.

What I'd tell someone starting:

- **Pin it exactly, and guard against a second copy.**
- **Set a frame budget and a named fallback before you write the first view.**
- **Learn the primitive set early.** If what you need can't be built from quads, paths, glyphs and images, find out on day
  one.
- **Patch the platform layer only when you must,** as commits on a vendored copy, and work around everything else next to
  a test.
- **Cache by what changed.** Glyphs, rows, panes. The rebuild cascades upward, so put things that change often where their
  changes rebuild nothing.
- **Read the source.** The documentation is thin, and the source is readable.

It's a young framework, and it shows in places. It's also the reason three very different apps of mine start instantly,
stay smooth with thousands of things on screen, and use little enough of a laptop that nobody uninstalls them for it.
