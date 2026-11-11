---
order: 12
title: tide
tagline: "A redesign of tide, the self-hosted video meeting service: a new interface in light and dark, an installable app, a screen-share popout and safer chat — on top of a Go and LiveKit core."
description: "My fork of tide, an open-source, self-hosted video meeting service from Convex Works. I redesigned its whole interface around a new meeting stage, added an installable app, a screen-share popout and carefully bounded chat features, and keep it in step with upstream."
category: product
stage: building
kind: Video meetings · Self-hosted
year: "2026"
logo: logos/tide.svg
monogram: "t"
accent: "#1F8F6A"
featured: false
cover: art/tide.svg
repository: https://github.com/mah3uz/tide
stack: [Go, SvelteKit, Svelte 5, Tailwind CSS 4, LiveKit, WebRTC, SQLite, OIDC, Docker, Dokploy]
highlights:
  - A complete redesign — light and dark themes on one layout, built on semantic tokens
  - The Orbit stage — the speaker in the lens, everyone else around it — from phone to desktop
  - Installable app, screen-share popout, and chat with minimal markdown and opt-in images
  - "About 11,500 lines across 116 files, kept mergeable with upstream"
seo:
  description: "tide, redesigned: my fork of a self-hosted Go and LiveKit video meeting service, with a new light and dark interface, an installable app, a screen-share popout and safer chat."
---

## tide

[tide](https://github.com/Convex-Works/tide) is an open-source, self-hosted video meeting service by Convex Works: one
Go binary that embeds a SvelteKit web app and the LiveKit media server. Meeting links, a guest lobby with host controls,
screen sharing, chat, and optional recording to S3-compatible storage — run it with a single `docker run`, or add sign-in
through any OIDC provider.

It is a good foundation: small, honest about what it does, and easy to host. My fork keeps all of that and gives it a new
face.

## A redesign, end to end

Calm, small and precise. I rebuilt the interface on a design language of my own, written down as a contract the code is
checked against:

- **Two themes, one layout.** Light and dark share every component; only the token values differ. The theme follows the
  system, a toggle overrides it, and it is applied before the first paint, so it never flashes.
- **Semantic tokens, enforced.** Every colour, radius, shadow and duration is a named CSS custom property. The build
  fails on any `var(--x)` that is used but never defined — because CSS drops an undefined variable silently.
- **The Orbit stage.** The latest speaker fills the *lens*; everyone else, you included, is a *portal* around it. A grid
  view lays everyone out evenly. On a phone the lens fills the width and the portals scroll in a strip beneath it; side
  panels are sheets that dock beside the stage on wide screens and become bottom sheets on small ones.
- **State in the chrome, not in toasts.** A two-pixel hairline across the top of the app is the status channel: the brand
  gradient when connected, amber while reconnecting, grey when offline, pulsing red while recording.
- **Motion with rules.** Only transform and opacity animate; nothing loops unless live state drives it; nothing animates
  in a hidden tab; reduced motion turns it all off.
- Roboto and JetBrains Mono, self-hosted; icon-first controls with tooltips; roles as words, not badges.

## What I added

Upstream deliberately freezes its feature list. The fork adds a few things, each kept small:

- **An installable app.** A web manifest and a service worker that caches the app shell — and never an API call, the
  signalling path or any media.
- **A screen-share popout.** A share can be lifted out into a small window of its own, using Document Picture-in-Picture
  where the browser has it, the browser's own picture-in-picture or presentation mode where it doesn't, or an ordinary
  resizable window on the desktop.
- **Minimal markdown in chat**, parsed to data and rendered as components, so no message can inject markup. Links must be
  bare, so with guests in the room a link always shows where it goes.
- **Images in chat**, off unless the server enables them. The sender's browser re-encodes each image, dropping metadata
  such as its location; images travel browser to browser over the media server's data channel, are held only in memory,
  and vanish with the meeting. Receivers check the format and dimensions, and limits on size, rate and memory bound what
  one sender can make everyone else hold.
- **Deployment on Dokploy**, with tide behind Traefik and media still reaching it directly over UDP.

## Staying a good fork

A fork that can't take its upstream's fixes is a liability. Fork-only work lives in new files; each upstream document
carries a single pointer line to the fork's own notes; and updates are merged, never rebased, so taking a new upstream
release stays a routine merge.
