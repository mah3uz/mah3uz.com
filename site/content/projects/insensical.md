---
id: insensical
order: 6
title: Insensical
tagline: A terminal multiplexer with a native window, for running many terminals and coding agents — and knowing which one needs you.
description: Insensical is a terminal multiplexer for Linux and macOS built around a daemon that owns every program, so closing the window stops nothing and upgrading it loses nothing. It works out the state of every pane — running, waiting, done, failed — so when you run several coding agents at once, you know which one is waiting on you.
category: product
stage: building
kind: Terminal multiplexer
year: "2026"
logo: /logos/insensical.svg
monogram: "i"
accent: "#17A398"
featured: false
cover: /art/insensical.svg
website: https://insensical.com
repository: https://github.com/mah3uz/insensical-release
stack: [Linux, macOS, Wayland, X11, Vulkan, Ghostty terminal engine, SSH]
highlights:
  - A daemon owns every program; windows, the terminal UI and the browser page are only its clients
  - Upgrades the server in place with every terminal, program and scrollback intact
  - Hooks for Claude Code, Codex, Gemini CLI, opencode, Cursor CLI, Copilot CLI and more
  - Eight releases in 24 days, shipped for Arch, Debian/Ubuntu and macOS
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
