---
id: sysman
order: 4
title: Sysman
tagline: A system monitor for Linux desktops that remembers what happened.
description: Sysman pairs a lightweight collector daemon, which records your machine's history, with a native GPU-accelerated app to explore it. It answers the question most monitors can't — what was my machine doing an hour ago?
stage: building
kind: Desktop app · Linux
year: "2026"
logo: /logos/sysman.svg
monogram: "S"
accent: "#0E9AA7"
featured: true
cover: /art/sysman.svg
website: https://sysman.asmechanics.com
repository: https://github.com/mah3uz/sysman
stack: [Rust, GPUI, Linux, Daemon]
highlights:
  - A collector daemon that keeps a history of your system
  - A native app built on GPUI to explore it
  - Made for Linux desktops
  - Rust from end to end
seo:
  description: "Sysman pairs a lightweight collector daemon, which records your machine's history, with a native GPU-accelerated app to explore it. It answers the…"
---

## Monitors forget

Most system monitors show you *now*. By the time you open one, the spike that froze your machine is gone. Sysman
splits the job in two: a small collector runs in the background and records what your system is doing, and a native
app lets you scroll back through it.

## Two parts

- **The collector** is a lightweight daemon that samples the system and stores its history.
- **The app** is built with GPUI, the GPU-accelerated UI framework from the Zed editor, so even long histories stay
  smooth to scrub through.

## Status

Sysman is in active development. Follow along on the site or the repository.
