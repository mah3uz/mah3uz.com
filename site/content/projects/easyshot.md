---
id: easyshot
order: 6
title: easyshot
tagline: Screenshots, markup and screen recording for Linux on Wayland, run from your own compositor's key binds.
description: easyshot is a screenshot, annotation and screen-recording app for Hyprland, sway and niri, written in Rust on GPUI. It always freezes the screen before you pick, has a full editor with Smart Redaction, records a single window even when it is covered or on another workspace, and runs as one background service driven by key binds, a command line and easyshot:// links.
category: product
stage: shipped
kind: Screenshots & recording · Wayland
year: "2026"
logo: /logos/easyshot.svg
monogram: "e"
accent: "#21BDB0"
featured: false
cover: /art/easyshot.svg
website: https://easyshot.site
repository: https://github.com/mah3uz/easyshot
stack: [Rust, GPUI, Wayland, layer-shell, ext-image-copy-capture, GStreamer, gpu-screen-recorder, wf-recorder, tiny-skia, cosmic-text, Tesseract, D-Bus, systemd]
highlights:
  - Area, window, full screen, previous target, timed and scrolling capture, always on a frozen screen
  - An editor with 13 tools, crop and rotate, backgrounds, Smart Redaction, and unsaved edits that survive a crash
  - Records one window from its own frames, even when it's covered or on another workspace
  - One daemon owns everything; the command line, tray, links and key binds all speak the same nine routes
  - Agent access through a command line, a skill and MCP, off by default, with consent enforced by the daemon
  - "About 165,000 lines of Rust in 20 crates and some 2,100 tests, built in eleven days"
  - Version 0.1.0 shipped on 11 November 2026 for Arch (AUR) and as a signed tarball; MIT licence
seo:
  description: "easyshot: a screenshot, annotation and screen-recording app for Linux on Wayland (Hyprland, sway, niri), built in Rust with GPUI."
---

## A screenshot tool that feels at home on a tiling desktop

I take a lot of screenshots: bug reports for clients, steps for documentation, the state of a server dashboard before I
change something. On a Mac there are excellent tools for this. On my own desktop, Arch with Hyprland, I had `grim` and
`slurp` wired to a key, which gives you a PNG and nothing else. No arrows, no blur over the API key in the corner, no quick
recording of a window to show someone what's going on.

easyshot is the tool I wanted: capture, mark up and record, driven entirely from key binds in your own compositor, with a
small floating preview of each capture that you can drag straight into a chat or a ticket. It runs as one background
service with a tray icon, and it never edits your compositor's configuration. It writes a binds file you include yourself.

## What it does

**Capture.** Area, window, full screen, the previous target, timed (3, 5 or 10 seconds) and scrolling capture. The screen
always freezes first, so a tooltip or a menu stays exactly as it was while you pick. Text recognition (with Tesseract), QR
codes and a colour picker work on the same frozen frame. A capture can be pinned above other windows.

**Annotate.** An editor with 13 tools, editable text, crop, rotate and flip, backgrounds and gradients, a camera angle,
progressive blur, borders, watermarks and presets. Smart Redaction reads the image, finds emails, keys and card numbers,
covers them, and tells you what it hid with an Undo button.

**Record.** An area, a display or a single window, with system sound and the microphone on separate tracks. A trim viewer
opens when you stop and exports MP4, WebM or GIF.

**Drive it from anywhere.** `easyshot capture region` from a key bind, `easyshot://capture/region` from a launcher, the tray
menu, or `easyshot doctor` when something isn't right. All of them reach the same daemon through the same short list of
routes.

## How it's built

easyshot is written in **Rust**, about 165,000 lines across twenty crates, on **GPUI**, the GPU-accelerated UI framework
from the Zed editor. Every overlay, toast, pin and preview card is a Wayland layer-shell surface opened through GPUI.

The crates are layered and the layering is enforced. Layer 0 is pure data, layer 1 is pure computation (rendering,
stitching, text recognition), layer 2 does I/O (storage, Wayland, D-Bus, recording) and layer 3 is the interface. A check in
the build fails if a lower layer depends on a higher one, or on GPUI at all. Another check fails if the words `hyprctl`,
`SWAYSOCK` or `NIRI_SOCKET` appear anywhere outside the three folders that are allowed to know which compositor is running.
Everything else sees only a set of capabilities, chosen at runtime by which Wayland protocols the compositor actually offers.

### One daemon, a thin command line

`easyshot daemon` is a long-running GPUI application that owns the tray, every window and overlay, the capture and
recording engines and the clipboard. `easyshot <command>` is a small client with no GPUI in it at all: it sends the command
over the session bus, starts the daemon if it isn't running, and waits for the result. The daemon already has the GPU
context warm and the screen frozen before a slow client would have finished starting.

Links from outside are deliberately limited. `easyshot://` accepts exactly nine routes and no arguments, so a link can open
the area picker but can never start a recording on its own.

### Recording a window you can't see

gpu-screen-recorder has no window mode on Wayland, and the screen-cast portal makes you pick the window again in its own
dialog. So easyshot records a window itself: it asks the compositor for that window's own frames through
`ext-foreign-toplevel-image-capture-source` and `ext-image-copy-capture`, paces them on a GStreamer clock and encodes with
whichever H.264 encoder the machine has. On Hyprland a window on a hidden workspace recorded at 114 frames a second. Where
the compositor can't provide a window's frames it falls back to recording the window's rectangle, and says so.

I wrote up the details in [Recording a window you can't see](/blog/recording-a-window-you-cannot-see).

### Unsaved edits survive

The editor writes a recovery journal after each committed change, and reopens any journal it finds at start-up. One path
covers a closed window, a panic, the out-of-memory killer and a power cut, which is the point: a shutdown hook would only
cover the first. Every file easyshot writes goes through a temporary file, `fsync` and a rename, and a file written by a
newer version opens read-only rather than being overwritten.

## Agents, with permission

An AI agent can take screenshots, read text from the screen and record short demos through `easyshot agent`, an
installable skill or an MCP server. All three are the same request underneath. Agent access is off by default; turning it
on needs you to click Allow in a dialog the daemon shows; access can be limited to particular outputs or windows; and secrets
are redacted from an agent's captures unless you say otherwise. Nothing is ever sent over the network.

## Shipping

Version 0.1.0 shipped on 11 November 2026, eleven days after the first commit. It runs on Hyprland, sway and niri,
with Hyprland as the home it was built on. It's on the AUR as `easyshot` and
`easyshot-bin`, and as a signed release tarball with an install script for other distributions. The install enables a
systemd user service, so the daemon is there at login on Hyprland, sway and niri, which ignore XDG autostart. It's
released under the MIT licence, and the website with a how-to guide is at [easyshot.site](https://easyshot.site).
