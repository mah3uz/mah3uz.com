---
title: What I'm focused on now
template: now
eyebrow: Now
intro: A snapshot of where my time and attention go this season — the products I'm building, the systems I'm running, and what I'm learning. Updated as things change.
art: /art/pages/now.svg
cards:
  - title: Building
    text: Nibble towards a stable 1.0 — fewer, firmer guarantees, and the first sites run by people other than me.
  - title: Operating
    text: Client platforms in production, and the servers behind this site and my products — patched, monitored and backed up.
  - title: Shipping
    text: Sysman's alerts, Darwan's wallpaper and saver work, Quarry and Insensical point releases.
  - title: Learning
    text: Native Linux UI with GPUI, eBPF across kernel versions, and the sharp edges of applied cryptography.
seo:
  title: Now
  description: What Mahfuz Shaikh is focused on now — building Nibble, operating client platforms, shipping Linux tools, and learning GPUI and eBPF.
---

## Building

Most of my product time goes into **Nibble**. The goal for the next stretch is a 1.0 that deserves the name: a smaller set
of guarantees I am prepared to keep for years, an upgrade path people can trust without reading every changelog, and the
first sites installed and run by people other than me. Its companion, **Nibble CLI**, is where much of the day-to-day
experience lives — creating sites, running their tasks, and working on content from a terminal or an AI agent, always as
the person who signed in.

## Operating

Alongside my own work I run production systems: client platforms, and the infrastructure behind this site and my products.
That means the unglamorous, essential work — patching and upgrades, backups that are tested by restoring them, monitoring
that alerts on what matters, and deploys small enough to be boring. I'm particularly interested right now in making
single-server deployments with Kamal as dependable as much larger setups, because for most applications one well-run
machine is the right answer.

## Shipping

- **Sysman** — alerts in the collector daemon are next, so a machine can tell you about a problem rather than waiting to be
  asked.
- **Darwan** — continuing the wallpaper manager and screensaver work, and keeping pace with the Wayland compositors it
  supports.
- **Quarry** and **Insensical** — point releases driven by daily use; the best feature requests come from the tool getting in
  my own way.

## Learning

GPUI, the GPU-accelerated UI framework from the Zed editor, for native Linux software that feels instant; eBPF and BTF for
observability that works across kernel versions; and, through rrussat, the practical details of applied cryptography —
where the hard part is never the algorithm, but the state machine around it.

## Not doing

Taking on new long-term commitments. I keep some room for focused engagements where engineering and infrastructure meet —
[get in touch](/about#contact) if you have one in mind.
