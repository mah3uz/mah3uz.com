---
order: 6
title: Insensical
tagline: A terminal multiplexer with a native window, for running many terminals and coding agents — and knowing which one needs you.
description: Insensical is a terminal multiplexer for Linux and macOS built around a daemon that owns every program, so closing the window stops nothing and upgrading it loses nothing. It works out the state of every pane — running, waiting, done, failed — so when you run several coding agents at once, you know which one is waiting on you.
category: product
stage: building
kind: Terminal multiplexer
year: "2026"
logo: logos/insensical.svg
monogram: "i"
accent: "#17A398"
featured: false
cover: art/insensical.svg
website: https://insensical.com
repository: https://github.com/mah3uz/insensical-release
stack: [Rust, gpui, libghostty-vt, Zig, WebAssembly, Noise protocol, rustls, Linux, macOS, Wayland, X11]
highlights:
  - A daemon owns every program; windows, the terminal UI and the browser page are only its clients
  - Upgrades the server in place with every terminal, program and scrollback intact
  - Hooks for Claude Code, Codex, Gemini CLI, opencode, Cursor CLI, Copilot CLI and more
  - "Replicated terminals: output is parsed once on its way to the screen, never re-encoded"
  - "Measured: 19 µs p99 added to a keystroke, and 2.9× tmux's throughput for build output"
  - About 159,000 lines of Rust in 11 crates, with some 1,900 tests and 900 recorded design decisions
  - Eight releases in 24 days, shipped for Arch, Debian/Ubuntu and macOS; to be open-sourced under the MIT licence
seo:
  description: "Insensical is a terminal multiplexer with a native window for Linux and macOS that tracks every pane's state, so you know which coding agent needs you."
---

## Run many agents. Know which one needs you.

Terminal multiplexers are one of the oldest good ideas in computing; tmux and screen have kept my sessions alive on
remote servers for most of my career. But the way we use terminals has changed. A single afternoon can now involve four
or five coding agents running in parallel, each one occasionally stopping to ask a question — and a wall of
identical-looking panes gives you no idea which one is waiting.

Insensical is a multiplexer designed for that afternoon. Its core idea is stated in the manual: *"A background server, the
daemon, owns every program. The window and the command line are its clients, so closing the window stops nothing."* The
native window is one client; `isc` running inside any terminal, including over SSH, is another; a local web page is a
third.

## How it's built

Insensical is written in **Rust** — about 159,000 lines across eleven crates — and its architecture starts from a
complaint about every multiplexer before it. A traditional multiplexer sits *in series* between a program and your
terminal: it parses the program's output into a screen of its own, works out what changed, re-encodes that as escape
sequences, and your terminal parses it all again. Every byte is parsed twice, state is kept twice, and what you see
moves at the speed of the slower parser.

Insensical replaces that with **replicated terminal state machines**:

- **The daemon** owns every PTY and child process, and keeps an authoritative terminal for each pane, built on
  **libghostty-vt**, Ghostty's terminal engine. It has no GPU or window-system dependency at all, so `isc` — the daemon,
  the command line and the terminal interface in one binary — runs on a headless server.
- **The window is a client.** For each pane it shows, it holds its own replica of that terminal. The daemon *tees* the
  raw PTY bytes to it unchanged — never screen diffs, never re-encoded output — so on the way from program to pixels each
  byte is parsed exactly once, by the replica that draws it.
- **One writer.** Only the daemon writes to a PTY; every client, the window included, sends input events, and every
  action in the interface is also an API request that `isc` can make.
- **Native panes.** In the window each pane is a real **gpui** element (the UI framework behind the Zed editor), mapped
  one to one to a PTY. Splits, tabs, floats and the overview are layout, not cells drawn inside another terminal.

### Rendering

libghostty is a terminal *state* library — no renderer, no fonts — so drawing the grid is Insensical's own code, on
gpui's primitives. Terminal objects never cross threads: each replica lives on a thread of its own and hands the
interface plain-data frames, which the interface **pulls** when it is ready to paint, so a flood of output never builds
frames nobody sees. Glyphs are resolved once and cached, rows are cached until the engine marks them dirty, no text is
shaped per frame, and a pane that hasn't changed isn't drawn again.

### The protocol

Clients speak a length-prefixed binary protocol over a Unix socket. The hot path — output, snapshots, resyncs — has
hand-encoded fixed layouts with no serialisation library in the way; control messages use `serde` and `postcard`. Each
pane gets its own connection, so one pane's flood can't delay another's, and a client that falls behind is dropped and
resynchronised rather than allowed to grow the daemon's memory. The same frames reach a daemon on another machine through
your own `ssh` and `isc proxy`, multiplexed over one pair of streams; the daemon cannot tell the difference.

### Remote, without opening a port

The daemon never listens on the network. `isc hub` is a separate process — a client of the socket like any other — that
serves the browser page over HTTPS and WebSockets. The browser runs the same client core compiled to **WebAssembly**,
with its own replica and terminal engine. Sessions between devices are end to end, using the **Noise** protocol
(`XK` handshakes over P-256 or X25519, ChaCha20-Poly1305), tested against an independent implementation, so a hub carries
traffic for joined machines that it cannot read. TLS is `rustls` on a pure-Rust provider, which keeps `isc` a single
statically linked binary for x86-64 and ARM with no C compiler in the build.

### Measured, not claimed

Every performance figure in its architecture document sits beside the benchmark that produced it. On a Ryzen 9 7950X3D
under Linux:

| Measure | Result |
|---|---|
| Latency added to a keystroke | 15 µs p50, 19 µs p99 |
| Attaching to a 200×60 pane with 4,000 lines of history | 0.8 ms p50 |
| Output throughput, build-style text | 159 MB/s — 1.08× of a terminal reading the PTY directly, 2.9× tmux, 4.4× zellij |
| A full 200×60 frame, worst-case styling | 2.0 ms p50 |
| Server memory, thirty panes after 18 MB of output each | 58 MB (tmux 94 MB, zellij 449 MB) |
| A daemon holding eight idle shells | zero wakeups in ten seconds |

On an Apple M1 Pro the same pipeline is 5.8× tmux's throughput. A dedicated section of the documentation records what has
been run on which platform, and anything not run on a platform is described as unverified rather than working.

## Knowing when you are needed

The heart of Insensical is working out what each pane is doing, from the strongest evidence available:

1. **An explicit report** — a program can announce its state, either through the `isc` command or a small escape-sequence
   protocol that agents can speak natively.
2. **Terminal signals** — progress and notification sequences, the bell, and password prompts, detected when the terminal
   stops echoing what you type.
3. **The foreground command ending**, with a threshold for long-running commands.
4. **The exit status** — where an interrupt counts as finished rather than failed.

Panes are idle, running, waiting, done, failed or exited, and the interface draws attention to the ones that need you
without ever reshuffling the layout: *"Nothing is ever reordered because of a state."* A state never ends just because a
program has gone quiet.

## Agents, fenced honestly

Insensical writes hooks for the agents people actually use — Claude Code, Codex, Gemini CLI, opencode, Cursor CLI, Copilot
CLI and others — and ships a guide that agents read through `isc guide`, so a new version teaches every agent at once.
Agents can start and supervise other agents, within limits of eight at once and two levels deep. A pane can be protected so
agents can't drive it. The manual is candid about what that protection is: *"It isn't a wall."* — and equally candid that
*"Letting an agent run `isc` lets it do anything you can."* I would rather a tool tell you the truth about its boundaries
than imply a guarantee it can't keep.

## Upgrading without killing anything

For anyone who has run long jobs in a multiplexer, the most valuable property is that nothing dies. Insensical's daemon
saves the layout on every change, and `isc restart-server` replaces the running server with the newly installed version
*in place*, keeping every terminal, program, screen and scrollback. Compatibility between clients and server is judged by
protocol and terminal engine rather than version numbers. After a clean stop, screens are kept as text and colour; after a
crash, the layout survives, and commands such as resuming an agent session are *offered* at the prompt rather than run on
your behalf.

## Security from the socket up

The daemon listens only on a Unix socket in a directory that must be private to you, and refuses to start if that
directory is too open, is a symlink, or contains something unexpected. Release notes spell out the hardening: clipboard
writes from windows on other workspaces are blocked, opening the file finder never runs a program a repository names, and
a client that stops reading can no longer exhaust the server's memory.

The optional hub serves a local page so you can follow your agents from a phone, without opening a port: devices pair by
code, joined machines dial out, and traffic between them is sealed so the hub *"can't read it."* Guest links are
view-only, single-use and expire within a week.

## Shipping

Insensical shipped eight releases in its first 24 days — from persistent programs and pane states to a full terminal
interface, a browser page, remote hosts over your own SSH, self-update against a signed release record, and start at
login. It is available for Arch (`insensical-bin`), as Debian and Ubuntu packages, as a single static `isc` for x86-64 and
ARM Linux, and for macOS on Apple silicon through `brew install --cask mah3uz/tap/insensical`.

Insensical will be open-sourced under the MIT licence; until then, releases are published from
[insensical-release](https://github.com/mah3uz/insensical-release).
