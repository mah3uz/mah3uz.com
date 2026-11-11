---
order: 4
title: Sysman
tagline: A system monitor for Linux that remembers — a crash-proof collector daemon and a native app to explore what happened.
description: Sysman is a Linux system monitor in Rust with three parts — a collector daemon that samples the machine every two seconds and keeps history in SQLite, a native GPU-accelerated app built on GPUI to explore it, and an optional, tightly confined helper for the readings that need root. Its first rule is that the last reading before a crash is already on disk.
category: product
stage: building
kind: System monitor · Linux
year: "2026"
logo: logos/sysman.svg
monogram: "S"
accent: "#0E9AA7"
featured: true
cover: art/sysman.svg
website: https://sysman.asmechanics.com
repository: https://github.com/mah3uz/sysman
stack: [Rust, GPUI, SQLite, systemd, eBPF, Linux]
highlights:
  - 14 collector modules, each on its own thread with its own deadline
  - Every reading is fsync'd before the next tick, so the moments before a crash survive it
  - About 2–3% of one CPU core on a 32-thread desktop with around 700 processes
  - 823 tests; collectors tested against fixture /proc and /sys trees
  - Packages for Arch and Debian/Ubuntu, install-tested in clean containers
seo:
  description: "Sysman is a crash-proof Linux system monitor in Rust: a collector daemon with SQLite history and a native GPUI app that explains why things happened."
---

## Monitors forget

Every administrator knows the moment: a machine froze, rebooted, or crawled for twenty minutes, and by the time you look,
every monitor on it shows a calm present. `top` tells you about *now*. Proper fleet monitoring tells you about servers,
and rarely about the desktop you actually work on. I wanted the history — on my own machine, in open formats, with no
account and no telemetry — and I wanted it to survive the very event I was trying to diagnose.

Sysman splits the job in three:

- **`sysmand`**, a collector that runs as a systemd *user* service. Every two seconds it samples CPU, memory, pressure,
  sensors, GPUs, disks, network, processes and more; it writes a crash log, stores history in SQLite, and serves live data
  over a Unix socket.
- **`sysman`**, a native desktop app built with GPUI, the GPU-accelerated toolkit behind the Zed editor, with eleven
  views: Dashboard, Processes, GPU, Energy, Network, Disk with a disk map, Hardware, Explorer, Insights, Logs and Groups.
- **`sysman-helper`**, optional, off by default, for the few readings that genuinely need root.

## Two non-negotiables

The design document begins with two rules, and everything else follows from them.

**"The last reading before a crash is on disk."** Each sample is appended to a JSON Lines log and `fdatasync`'d before the
next tick. SQLite has its own thread and a bounded queue; if it ever falls behind, records are dropped and *counted*,
*"so the database never delays the crash log."* After a hard reset, the last lines of the log tell you which way it went:
temperatures climbing points at cooling, everything flat points at the power supply, a burst of GPU errors points at the
driver.

**"One failing source does not stop the others."** Every collector runs on its own worker thread. Ticks align to the wall
clock; a module that misses its deadline — three quarters of the interval — is recorded as late, and its reply discarded.
Panics are caught. A GPU driver that hangs is the classic case: NVML is called on an inner thread with a one-second
deadline, and after its first hang it is abandoned for `nvidia-smi`, run as a child process that is killed if it, too,
takes longer than a second. A GPU that has powered itself down is never polled awake.

## Honest numbers

Sysman refuses to show a misleading zero: values that need root are shown as *not permitted*. A typo in the configuration
stops the daemon, *"so a typo cannot silently switch something off."* And the daemon is held to a footprint budget —
every collector change is measured for CPU and memory before and after, and judged *"for a modest laptop rather than for
the machine it was measured on."*

That budget caught real costs. One family of motherboard sensor chips was being read over port I/O so expensively that
polling it cost about 4.6% of a core; those chips are now read every ten seconds by default. Following the system journal
initially cost around 120 MB of memory; reopening only the files that are actually growing brought it to about 7 MB. The
reference measurement is about 2.6% of one core, 85 MB of memory and 23 threads on a 32-thread desktop with around 700
processes.

## History that stays useful

Series are named by JSON pointer and devices keyed by stable identifiers, never by position, so adding a disk doesn't
scramble a year of charts. Raw points are kept for 48 hours, one-minute roll-ups for 90 days and fifteen-minute roll-ups for
two years; a restart rebuilds any half-finished minute from raw points, *"so a restart loses nothing."* Process identity is
the PID *plus* its start time, so a reused PID is never confused with the process that had it before. The database grows by
adding columns and is never rebuilt.

## "Why is this running?"

The feature I am proudest of answers the question every administrator asks about an unfamiliar process. Sysman classifies
a process from its cgroup and its parent chain — a systemd service, socket-, timer- or D-Bus-activated, a login autostart,
an app, a terminal job, an orphan, a container (Docker, Podman, Kubernetes), Flatpak, Snap, cron or the kernel — and shows
the evidence. It then explains what happens *if you end it*: whether systemd will restart it, based on the unit's
`Restart=` policy and the difference between a clean `SIGTERM` and a `SIGKILL`. The rule is written into the design:
*"Facts only: every cause names its evidence, and what cannot be known is said."*

The Logs view applies the same principle to the journal and package-manager history together, surfacing what is worth a
look: crashes folded per program, OOM kills, failed units and restart loops, unclean shutdowns, GPU faults, disk and NVMe
errors, thermal throttling and repeated failed sign-ins.

## A root helper that knows its place

Some readings need privilege: SMART data, energy counters, other users' I/O, and per-process network traffic. The helper
reads NVMe health through an admin ioctl and SATA drives through `smartctl` in a mode that won't spin up a sleeping disk,
and counts network bytes per process with eBPF — one program per kernel signature, chosen at load time from the running
kernel's BTF, so it works across kernel versions. It runs under systemd with an allow-list of capabilities, a read-only
system, no network, and no writable-and-executable memory; it answers one request per second per connection, eight
connections at most. And it reports which processes are *listening* on ports, never their connections, because joining
connections to processes *"would tie every user's remote peers to processes."*

## Built like infrastructure

Sysman has 823 tests. Collectors are tested against fixture `/proc` and `/sys` trees, every collector's output round-trips
through shared schema types, and each journal rule has a test built from a real entry. Release CI builds inside Ubuntu
22.04 to hold the glibc floor, then install-tests the Debian package in fresh Ubuntu 22.04, Debian 12 and Ubuntu 24.04
containers — checking linked libraries and clean removal — and only marks a release as latest once every artefact is
uploaded. It ships for Arch (`sysman`, `sysman-bin`), Debian and Ubuntu, and as a checksum-verified installer that refuses
to run over a package-manager install.
