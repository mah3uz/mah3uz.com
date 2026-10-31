---
id: umbrel-apps
order: 11
title: Umbrel app store
tagline: A community app store for umbrelOS, packaging the Gopeed download manager for self-hosted home servers — and keeping it current.
description: A community app store for umbrelOS, the self-hosting operating system, that packages Gopeed — an HTTP, BitTorrent and magnet download manager — as a one-click app with pinned images, a proxy and persistent storage.
category: product
stage: shipped
kind: Self-hosting · Packaging
year: "2025"
monogram: "U"
accent: "#2A8FB0"
featured: false
cover: /art/umbrel-apps.svg
repository: https://github.com/mah3uz/umbrel-app-store
stack: [Docker Compose, umbrelOS, Self-hosting, Container packaging]
highlights:
  - Gopeed packaged for umbrelOS with a digest-pinned image, app proxy and storage volumes
  - Maintained through upstream releases from v1.8.0 onwards
  - File ownership fixed for the umbrelOS user model
seo:
  description: "A community umbrelOS app store by mah3uz that packages the Gopeed download manager for self-hosted home servers with Docker Compose."
---

## Self-hosting, made one click

umbrelOS turns a small home server into a self-hosted app platform, and its community app stores let anyone package
software for it. I built one to package [Gopeed](https://gopeed.com), a download manager for HTTP, BitTorrent and magnet
links, so it installs on an Umbrel the same way any first-party app does.

## The work behind a "simple" package

Packaging is where operations experience earns its keep. The app definition pins the container image by digest rather
than by a moving tag, so an install today is byte-for-byte the install that was tested. It runs behind Umbrel's app proxy
rather than exposing its own port, and keeps its data on storage volumes that survive updates and reinstalls.

Maintenance is the part people skip. The package has followed Gopeed through its releases — from v1.8.0 to v1.9.1 and
v1.9.3 — and a later fix set the process's user and group IDs so files written by the app are owned correctly on the host,
which is exactly the kind of detail that turns into a support question six months later if nobody handles it.
