---
id: rrussat
order: 7
title: rrussat
tagline: A peer-to-peer, end-to-end encrypted messenger that runs entirely in the terminal.
description: An experiment in private messaging with no server in the middle. Peers find each other directly, every message is end-to-end encrypted, and the whole thing lives in your terminal.
stage: experiment
kind: Messenger · Terminal
year: "2026"
logo: /logos/rrussat.svg
monogram: "R"
accent: "#167A8E"
featured: false
cover: /art/rrussat.svg
repository: https://github.com/mah3uz/rrussat
stack: [Rust, P2P, Encryption, TUI]
highlights:
  - Peer-to-peer, with no central server
  - End-to-end encrypted
  - Runs entirely in the terminal
seo:
  description: "An experiment in private messaging with no server in the middle. Peers find each other directly, every message is end-to-end encrypted, and the whole…"
---

## The question

How small can a private messenger be? rrussat is my answer in progress: no accounts, no central server, just peers
talking to each other directly, with every message encrypted end to end.

## Why the terminal

Because it removes everything that isn't the conversation. A terminal interface is fast, accessible over SSH, and
honest about what's happening.

## Status

This is an experiment: a place to learn about peer-to-peer networking and applied cryptography in Rust. It's public so
others can learn from it too.
