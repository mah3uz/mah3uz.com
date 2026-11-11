---
title: "Cargo's defaults ate 483 GB: a Rust build postmortem"
published_at: 2026-11-11T12:00:00+06:00
topics: [rust, operations, engineering]
excerpt: "A postmortem of build storage and test time across seven Rust workspaces: a 483 GB target folder that stalled a 32-core desktop on disk I/O, a release that ran another checkout's tests, a /tmp full of test leftovers, and the changes that fixed each one, with the numbers."
art: /art/posts/target-folder.svg
---
## Summary

In early November my workstation began to stall during Rust builds and test runs: slow redraws, input lag, dropped audio.
The cause was disk I/O, not CPU. One workspace's `target/debug` had reached **483 GB**, and relinking its test binaries
was writing about 1.3 GB to disk every two seconds.

Looking into it turned up a set of related problems across seven Rust workspaces, all of them consequences of Cargo's
defaults meeting an unusual workload. The main causes were:

1. Full debug information for every dependency, in every test binary.
2. One test binary per integration-test file.
3. Build outputs that Cargo never removes.
4. A shared target folder that let one checkout run another's tests.
5. Tests that ran one binary at a time, in an order that left the slowest for last.
6. Tests that left their files in a memory-backed `/tmp`.
7. Parallel builds competing with each other, and with the desktop, for CPU and memory.

Each has a fix, and most of the fixes are a few lines of configuration. Together they took the largest `target/` from 483
GB to tens of gigabytes, halved the debug builds of the smaller projects, cut one slow test from 58 seconds to 5, and took
a test suite from 254 seconds to about 90. Two of the fixes were wrong for some projects, and those are the most useful
parts of this report.

## Impact

- **Desktop stalls.** Disk pressure stall information (`/proc/pressure/io`) showed every process that needed the disk
  waiting for 21 to 27 percent of the time during builds. CPU and memory pressure were close to zero.
- **Disk.** easyshot's `target/debug` reached 483 GB; Insensical's `target/` passed 100 GB; Sysman's was 22 GB.
- **A failed release.** Darwan's release script stopped when 14 tests failed in 0.00 seconds. They were another checkout's
  test binaries.
- **Failed test runs.** One Insensical run had 94 failures with *"Disk quota exceeded"* when `/tmp`, a 63 GB tmpfs,
  reached 50 GB.
- **Slow feedback.** Insensical's Rust suite took 254 seconds; one window test alone took 58.
- **Memory risk.** Five parallel builds on 32 threads could start around 128 `rustc` processes on a 124 GB machine.

![It wasn't the CPU: disk pressure at 21 to 27 percent while CPU and memory pressure sat near zero](/art/posts/cargo-defaults-ate-483-gb/io-pressure.svg)

## Environment

Seven Rust workspaces built over about two months, among them a terminal multiplexer (Insensical), a screenshot tool
(easyshot), a system monitor (Sysman), a SQL client (Quarry) and a lock-screen manager (Darwan). Three are GPU
applications on GPUI, with wgpu underneath. Much of the building and testing ran in AI coding agents working in
parallel, each in its own git worktree, all on one workstation: 32 hardware threads, 124 GB of memory, an NVMe drive,
btrfs with zstd compression and regular snapshots, Rust 1.98.

That workload is the context for everything below. Cargo's defaults are tuned for one person editing one crate in one
checkout. This was many checkouts, many builds at once, and some very large dependency graphs.

## How it was investigated

Every change below was measured before it was made, usually by building the same project twice from clean, once with a
`--config` override. Four commands did most of the diagnosis:

```
du -sh target/*/ target/debug/*/ | sort -h | tail        # where the space is
size -A target/debug/deps/<big-binary> \
  | awk '/^\.debug/{d+=$2}{t+=$2}END{print d/t}'          # share of a binary that is debug info
cat /proc/pressure/io                                     # is the disk stalling everything else?
cargo tree -i <crate> -e normal                           # who pulls in this dependency?
```

The first, on easyshot's folder, gave the shape of the problem straight away.

![Where 483 GB went: 376 GB in deps, 65 GB in examples and 43 GB of incremental state](/art/posts/cargo-defaults-ate-483-gb/where-it-went.svg)

## Findings

### 1. Half of every test binary was debug information

**Symptom.** easyshot had 136 test binaries, each 1 to 1.7 GB. A change to a low-level crate relinked most of them, and
each relink wrote its full size to disk.

**Cause.** Cargo's `dev` profile, used by `cargo build` and `cargo test`, compiles every crate with full debug
information, dependencies included. A test binary that links GPUI carries the debug information of a GPU stack, a text
shaper and a few hundred other crates. In easyshot about half of each binary was `.debug` sections; in Darwan, 42 to 49
percent.

**Fix.** Line tables for the workspace's own code, which is enough for a panic's backtrace to name the file and line, and
no debug information for dependencies:

```toml
[profile.dev]
debug = "line-tables-only"

[profile.dev.package."*"]
debug = false
```

**Result.** Darwan's debug test build went from 4.1 GB to 1.9 GB, and the bytes written to link all its test binaries from
about 1.2 GB to 0.3 GB. Sysman's application binary went from 540–640 MB to 44 MB, and its `target/debug` from 22 GB to
3 GB. Quarry went from 3.7 GB to 1.7 GB.

![Half of every test binary was debug info: Sysman's binary from 540 to 640 MB down to 44 MB, Darwan's largest test binary from 283 to 91 MB, Quarry's from 262 to 67 MB](/art/posts/cargo-defaults-ate-483-gb/binary-anatomy.svg)

![target/ before and after the profile change, on a log scale](/art/posts/cargo-defaults-ate-483-gb/before-after.svg)

**Trade-off.** Variables can't be inspected in a debugger. easyshot and Sysman keep a profile that restores everything
for the occasion, and `CARGO_PROFILE_DEV_DEBUG=full` does the same for a single command:

```toml
[profile.dbg]
inherits = "dev"
debug = "full"

[profile.dbg.package."*"]
debug = "full"
```

**Note.** The first assessment for Darwan recommended no change, because its `just` recipes test in release mode. The
session history showed otherwise: plain `cargo test -q --workspace` had been run 36 times and `cargo build -q -p
darwan-gui` 40 times, all in debug. Decide from what is actually run, not from what the scripts say.

### 2. Every file in tests/ was a separate binary

**Symptom.** The 136 test binaries in finding 1; easyshot's editor crate alone had 27.

**Cause.** Each file directly under `tests/` is compiled and linked as its own executable, and each links every
dependency of the crate.

**Fix.** One integration-test binary per crate, as matklad describes in *Delete Cargo Integration Tests*:
`tests/it/main.rs` declares a module per former file, and the files move into `tests/it/`. easyshot made the change across
the workspace in one commit; a low-level change now relinks roughly one test binary per crate instead of 136.

**Where it doesn't apply.** Darwan has two test files and Quarry three. Merging them was assessed and rejected: it "gains
almost nothing" and makes single files harder to run alone. It pays off with many test files per crate and a heavy
dependency graph.

### 3. Unoptimised dependencies made tests slow

**Symptom.** One Insensical window test took 58 seconds.

**Cause.** Window tests draw real frames through GPUI, off screen. In a debug build GPUI itself is unoptimised, and the
test spent its time there, not in Insensical's code.

**Fix.** Optimise dependencies, and leave the workspace's own crates at `opt-level = 0` so they still compile quickly and
incrementally:

```toml
[profile.dev.package."*"]
opt-level = 2
debug = false
```

**Result.** The same test takes 5 seconds. Dependencies compile once, optimised, and are reused. easyshot and Sysman carry
the same setting, commented *"gpui is too slow to use unoptimised."*

![Optimise the dependencies, not your code: one window test took 58 seconds with dependencies unoptimised and 5 with opt-level 2](/art/posts/cargo-defaults-ate-483-gb/deps-opt.svg)

**Applies when** tests spend their time inside a heavy dependency: a renderer, a codec, a parser, a database engine.

### 4. Cargo never removes old build outputs

**Symptom.** A week after finding 1 was fixed, easyshot's `target/` was back to 68 GB.

**Cause.** Cargo names each build output by a hash of its inputs: sources, dependency versions, enabled features,
toolchain. Any change produces a new file, and the old one stays. easyshot's test gate runs nextest with three different
feature sets, so many test binaries exist three times over before any code changes. After a week the folder held 49
hashed copies of each of 13 example programs, about 193 MB each, plus 171 old copies of one test binary and 162 of
another.

![Cargo never throws anything away: 13 examples times 49 hashed copies is about 22 GB, and 171 plus 162 stale test binaries are about 35 GB more](/art/posts/cargo-defaults-ate-483-gb/stale-copies.svg)

**Fix.** A size-capped clean. easyshot's `just sweep` runs `cargo clean --profile dev` when `target/debug` exceeds a
limit, 80 GB by default. The next build is a full one. Tools such as `cargo-sweep`, which remove only old files, are an
alternative I haven't evaluated.

**Two operational issues in the cleanup itself:**

- **btrfs snapshots retain deleted files.** After `cargo clean` removed 585 GiB, free space barely changed, most likely
  because snapshots still referenced the build output. Lower snapshot retention for the folder, or keep build output out
  of snapshotted subvolumes.
- **Mass deletion causes its own stall.** Deleting hundreds of gigabytes at once on a filesystem mounted with
  `discard=async` sends a burst of TRIM commands to the SSD and stalls the desktop again. Delete in batches.

### 5. A shared target folder ran another checkout's tests

**Symptom.** A Darwan release stopped when 14 tests failed in 0.00 seconds.

**Cause.** A dry run of the release script in a scratch clone had pointed `CARGO_TARGET_DIR` at the real checkout's
`target/`. As far as I can tell from the Cargo issues about it, Cargo leaves the workspace path out of what it hashes,
for reproducible builds, so both checkouts produced the same artifact names. The real release found the clone's test
binaries, treated them as up to date, and ran them, with the deleted clone's path compiled in.

**Fix.** Never share a target folder between checkouts. Darwan's release recipe now runs `cargo clean --release
--workspace` before testing; dependencies stay in sccache, so it costs seconds. The comment above it:

> Artifacts left by another checkout sharing target/ can look up to date and test the wrong sources.

### 6. Every worktree built cold, and incremental output couldn't be shared

**Symptom.** In one round of parallel work in Insensical, twelve builder worktrees each had about 15 GB of `target/`, all
compiling the same dependencies.

**Cause.** Separate target folders (finding 5) mean separate builds. And easyshot's 43 GB of incremental state was never
shared between worktrees at all.

**Fix.** Two parts. First, sccache shared by every checkout, configured per machine in a git-ignored file that the
project's config includes when it exists:

```toml
# .cargo/config.toml (in git)
include = [{ path = "local.toml", optional = true }]

# .cargo/local.toml (ignored, this machine only)
[build]
rustc-wrapper = "sccache"
incremental = false

[env]
SCCACHE_CACHE_SIZE = "40G"
```

sccache can't cache a crate built incrementally, so the workspace's own crates would never hit the cache with
incremental on. Second, worktrees are removed as soon as their branch is merged, which removes their `target/` with them.
A session-start hook removes any agent worktree that is clean, merged and idle for a day, and nothing else.

**Where it doesn't apply.** `incremental = false` was right for easyshot and wrong for Sysman. Measured in Sysman,
rebuilding after an edit took 10 seconds with incremental off against 5 with it on, and a fresh worktree 88 seconds
against 67. Sysman keeps incremental on, and its notes say not to revisit it without new numbers. The answer depends on
crate size, link cost and how many checkouts build at once. Measure it per project.

### 7. Tests ran one binary at a time

**Symptom.** Insensical's Rust suite took 254 seconds, 131 of them in one binary whose tests mostly wait on real timers.

**Cause.** `cargo test --workspace` runs test binaries sequentially. Tests run in parallel only within one binary.

**Fix.** [cargo-nextest](https://nexte.st), which runs every test as its own process across all binaries at once. On 32
cores the same suite takes about a minute and a half. Process-per-test also brings isolation: a hang can be ended on its
own, and global state, environment and ports belong to one test. Every test that starts a daemon gives it its own socket,
state directory and config directory, so a test can never reach the copy in daily use.

![The same 1,878 tests: 254 seconds with cargo test, 161.7 with nextest in name order on 12 threads, and 134.0 with the slowest tests started first](/art/posts/cargo-defaults-ate-483-gb/suite-time.svg)

```toml
# .config/nextest.toml
[profile.default]
fail-fast = false
retries = 1
slow-timeout = { period = "60s", terminate-after = 3 }

[test-groups]
sway-seat = { max-threads = 1 }

[[profile.default.overrides]]
filter = "test(/(^|::)platform_/)"
test-group = "sway-seat"
```

The retry and the three-minute limit address a known fault: a GPUI window test hangs at the very end, in the toolkit's
off-screen scheduler, in about one run in twelve. nextest ends that one test and runs it again; without it, the only
remedy is a time limit on the whole run. The test group serialises tests that share one resource, a single sway seat,
while everything else runs in parallel.

**Caveats.** Process-per-test has a cost. The first nextest run of the window tests had five past 60 seconds, each paying
GPUI's start-up; splitting the window tests into modules and finding 8 resolved it. For small CPU-only tests, process
overhead can make nextest slower than `cargo test`. nextest also doesn't run doctests, so every gate runs `cargo test
--workspace --doc` as well.

### 8. The slowest tests started last

**Symptom.** With nextest in name order, two web tests of 46 and 33 seconds started when most others had finished, and
the run waited on them: 161.7 seconds for 1,584 seconds of tests on 12 threads.

**Fix.** A priority override for the twenty slowest tests, so they start first and short tests fill in around them.

**Result.** 134.0 seconds, 17 percent faster.

![Start the long ones first: in name order the long tests start late and stick out; started first, the short tests pack around them](/art/posts/cargo-defaults-ate-483-gb/slowest-first.svg)

**Caveat.** One test that takes 13 seconds alone took 165 seconds on a Mac when it started together with the other heavy
tests, all competing for the same resources. It was removed from the list. Priority reorders work; it doesn't add
capacity. Check it on every platform.

### 9. Timing tests ran in the everyday suite

**Cause.** Quarry has performance tests: rendering 100,000 rows of ten coloured columns, listing a schema of 3,000 tables.
They're only meaningful in release mode and slow to set up.

**Fix.** They're ignored by default and run by a separate `just test-slow` recipe:

```rust
#[test]
#[ignore = "timing; run with --release -- --ignored"]
fn render_100k_rows_fast() { /* ... */ }
```

**Result.** The everyday suite is 327 tests in 0.24 seconds. Tests that need a real PostgreSQL or MySQL read its address
from an environment variable and skip when it isn't set.

### 10. Tests filled /tmp

**Symptom.** 94 test failures with *"Disk quota exceeded"* in one Insensical run.

**Cause.** `/tmp` is a tmpfs, held in memory, and it was 50 GB full out of 63: about 16,000 leftover directories from one
kind of test and 13,000 from another. One test, which checks that `isc` can replace itself, copied the binary each time
and left 260 to 400 MB behind per run.

**Fix.** Every test removes the directories it creates when it ends, pass or fail, and the self-replacement test removes
its copies. A leak into a memory-backed `/tmp` is a memory leak. Check `du -sh /tmp`, not only `target/`.

### 11. One release profile served every purpose

**Symptom.** In Insensical, an optimised build for local installs and browser tests took most of a minute after every
change.

**Cause.** The release profile uses thin LTO and a single codegen unit, which shipped builds need: the grid calls into the
toolkit once a glyph and the codec once a frame, across crate boundaries that only link-time optimisation can see through.
Local installs don't need it.

**Fix.** A second profile for fast optimised builds:

```toml
[profile.page]
inherits = "release"
lto = "off"
codegen-units = 16
```

**Result.** After a change to the protocol crate, a `page` build took 36 seconds against 126 for release on Linux, and 32
against 89 on a Mac.

![One profile per job: dev, dbg, page and release, each with its own settings](/art/posts/cargo-defaults-ate-483-gb/profiles.svg)

**Caveat.** easyshot's equivalent, `fast`, made its image benchmarks three to seven times slower than a shipped build,
because its SIMD wrappers were no longer inlined across 16 codegen units. Those few crates are overridden back to one
codegen unit and `opt-level = 3`. A faster build profile is fine for installing; benchmark only with a profile you've
checked against release.

Release builds also strip symbols. In Insensical they were a fifth of each binary: the app went from 70 MB to 50 and
`isc` from 37 MB to 28, at the cost of addresses instead of names in a panic's backtrace.

### 12. A default feature pulled in an unused crate family

**Cause.** Quarry uses `arboard` for text on the clipboard. Its default `image-data` feature brings in the whole `image`
crate family, which Quarry never uses. `cargo tree -i image -e normal` showed the path.

**Fix.** `default-features = false` with only the feature Quarry needs. 157 lines left `Cargo.lock`, and `cargo test
--no-run` went from 25 seconds to 13 in a single measurement on a busy machine, so that figure is indicative only.

### 13. Parallel builds competed with each other and with the desktop

**Symptom.** With several builds running, the desktop stuttered, and five builds could start around 128 `rustc`
processes, each wanting a few gigabytes, on a 124 GB machine.

**Cause.** Each Cargo sizes itself to the whole machine. On 32 threads, one build starts 32 jobs, and so does each of the
other four. Nothing ranks a build below the desktop.

**What was tried first.** A cap: twelve jobs per build and four test threads. It kept the machine stable and left most of
it idle whenever a single build was running.

**Fix.** Three small pieces of machine configuration, so that a single build uses every core, parallel builds share the
cores, and the desktop always wins:

![Builds below the desktop: every cargo runs in build.slice and takes its jobs from one shared pool of tokens](/art/posts/cargo-defaults-ate-483-gb/build-slice.svg)

- **A systemd slice for builds.** `CPUWeight=10`, against the default of 100, gives the desktop ten times the share when
  both want the CPU; when the desktop is idle the build gets everything, because a weight isn't a limit. `MemoryHigh` is a
  soft ceiling: past it, the kernel reclaims memory from builds and slows them before applications start to swap.
- **A wrapper named `cargo`,** ahead of the real one on the `PATH`, that runs every Cargo as a transient scope inside that
  slice. A scope rather than a service, so the build stays attached to the terminal, with its output and Ctrl-C as usual.
  Everything Cargo starts lands in the slice: `rustc`, the linker, build scripts, nextest, the test binaries and the
  sccache server.
- **A shared jobserver.** Cargo and `rustc` speak GNU make's jobserver protocol: a pipe holds one token per job slot, and
  a process takes a token before starting a job and returns it afterwards. Normally each Cargo makes its own pool. The
  wrapper points every Cargo at one shared pool through `CARGO_MAKEFLAGS`, kept by a small user service. On 32 threads it
  holds 31 tokens, plus the one slot each Cargo holds by itself, so a build on its own uses all 32 and five builds share
  them.

No I/O weight is set. A user's systemd manager doesn't get the I/O controller by default, and on an NVMe drive using the
`none` scheduler it would have no effect. The disk stalls were fixed by writing less (findings 1 and 2), not by
priority.

**What it takes.** All of it lives in your home directory: two systemd user units, two small scripts, and nothing that needs root. It works
on any Linux desktop with systemd and cgroups v2, which is every mainstream distribution today (`stat -fc %T
/sys/fs/cgroup` prints `cgroup2fs`). The jobserver needs Python 3, and Cargo needs to be recent enough to accept a
`fifo:` jobserver; I'm on 1.98.

The slice goes in `~/.config/systemd/user/build.slice`. Set `MemoryHigh` to about 70 percent of your RAM; mine is 90 GB of
124.

```ini
[Unit]
Description=Cargo builds, below the desktop in CPU and memory

[Slice]
CPUWeight=10
MemoryHigh=90G
```

The jobserver is a script in `~/.local/bin/cargo-jobserver`, made executable. It creates a named pipe in your runtime
directory that only you can open and fills it with one token per hardware thread, minus one. The loop at the end
matters: a build killed while it holds tokens never gives them back, and without a refill the pool would slowly shrink.
Every 30 seconds, if nothing is compiling, it empties the pipe and fills it again. Because it only refills when nothing
is building, it can never hand out more tokens than exist.

```python
#!/usr/bin/env python3
import errno
import os
import signal
import subprocess
import sys
import time

PATH = os.path.join(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"), "cargo-jobserver")
# Each cargo also holds one implicit slot of its own.
TOKENS = max(1, (os.cpu_count() or 1) - 1)


def building():
    return subprocess.run(["pgrep", "-u", str(os.getuid()), "-x", "cargo|rustc"], capture_output=True).returncode == 0


def refill(fd):
    while True:
        try:
            if not os.read(fd, 4096):
                break
        except OSError as e:
            if e.errno == errno.EAGAIN:
                break
            raise
    os.write(fd, b"+" * TOKENS)


def main():
    try:
        os.unlink(PATH)
    except FileNotFoundError:
        pass
    os.mkfifo(PATH, 0o600)
    fd = os.open(PATH, os.O_RDWR | os.O_NONBLOCK)

    def stop(*_):
        try:
            os.unlink(PATH)
        finally:
            sys.exit(0)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    refill(fd)
    while True:
        time.sleep(30)
        # A build killed while holding slots never returns them; reset only when nothing builds.
        if not building():
            refill(fd)


if __name__ == "__main__":
    main()
```

A user service keeps it running, inside the build slice too, and restarts it if it ever dies. It goes in
`~/.config/systemd/user/cargo-jobserver.service`:

```ini
[Unit]
Description=Shared build-slot pool for every cargo build

[Service]
Slice=build.slice
ExecStart=%h/.local/bin/cargo-jobserver
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
```

The wrapper is `~/.local/bin/cargo`, also executable. It looks for the real `cargo` further down your `PATH`, skipping
itself, so it works the same with rustup or a distribution package. If the pool exists, it points Cargo at it, and then
it runs Cargo as a scope inside the slice. Two checks keep it out of trouble: when it's already inside the slice (Cargo
calling Cargo from a build script, say) it doesn't nest another scope, and when there's no user bus, as in a bare SSH
session, it simply runs Cargo as it is.

```sh
#!/bin/sh
# Every cargo runs in build.slice, below the desktop, and draws its jobs from the shared pool.
self=$(readlink -f "$0")
real=
IFS=:
for dir in $PATH; do
  if [ -x "$dir/cargo" ] && [ "$(readlink -f "$dir/cargo")" != "$self" ]; then real="$dir/cargo"; break; fi
done
unset IFS
[ -n "$real" ] || { echo "cargo: no cargo on PATH besides $self" >&2; exit 127; }
run=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
[ -p "$run/cargo-jobserver" ] && export CARGO_MAKEFLAGS="-j --jobserver-auth=fifo:$run/cargo-jobserver"
if grep -q '/build\.slice/' /proc/self/cgroup || [ ! -S "$run/bus" ]; then
  exec "$real" "$@"
fi
exec systemd-run --user --scope --quiet --collect --slice=build.slice -- "$real" "$@"
```

The one thing that's easy to get wrong is the order of your `PATH`. `~/.local/bin` has to come before the directory
holding the real Cargo, or the wrapper never runs. `type -a cargo` tells you: the wrapper should be listed first. After
that, `systemctl --user daemon-reload` and `systemctl --user enable --now cargo-jobserver.service` bring it up, and the
pool appears as a pipe in your runtime directory:

```sh
$ type -a cargo
cargo is /home/you/.local/bin/cargo
cargo is /usr/bin/cargo
$ ls -l "$XDG_RUNTIME_DIR/cargo-jobserver"
prw------- 1 you you 0 Nov 11 13:21 /run/user/1000/cargo-jobserver
```

You can watch it work. Start a build, and in another terminal `systemctl --user status build.slice` shows the jobserver
and a `run-…scope` holding `cargo` and its `rustc` processes, with the memory ceiling in the header. Start a second build
in another checkout while the first is running, and `pgrep -c rustc` stays close to your number of cores instead of
doubling. Mid-build, the slice looks something like this:

```
● build.slice - Cargo builds, below the desktop in CPU and memory
     Memory: 6.1G (high: 90G, available: 83.9G)
     CGroup: /user.slice/user-1000.slice/user@1000.service/build.slice
             ├─cargo-jobserver.service
             │ └─1165 python3 /home/you/.local/bin/cargo-jobserver
             └─run-p51283-i51284.scope
               ├─51290 /usr/bin/cargo build
               ├─51402 rustc --crate-name serde ...
```

Once the pool is there, remove whatever you added before to keep builds in check: `jobs =` in a `.cargo/config.toml`,
`CARGO_BUILD_JOBS`, `-j`, `--test-threads`, `RAYON_NUM_THREADS`, `nice`, `taskset`. Each of them either bypasses the pool
or shrinks it a second time. Keep only the limits a test needs to be correct, like the nextest test group earlier. And if
you ever want it gone, disabling the service and deleting the four files puts everything back as it was.

**Limits.** The wrapper covers `cargo` run by name only. A tool that calls `/usr/bin/cargo` by its full path or runs
`rustc` itself bypasses it, as does a build inside a container. Agents are instructed to run `cargo` by name and never to
set `CARGO_MAKEFLAGS`. None of this makes one build faster; it makes several builds share the machine fairly and keeps the
desktop usable while they do. The four files live in one stow package in my dotfiles, as machine configuration, outside
every repository.

### 14. Every change ran every test

**Symptom.** A small change to a device icon took hours across three agent jobs.

**Cause.** Each job's brief said it was done when the browser test suite passed, so every job ran a six-minute browser
suite regardless of what it touched.

**Fix.** A `just test-changed` recipe runs nextest only for crates affected by a change, using nextest's `rdeps()`
filter, and falls back to everything when `Cargo.toml`, the lock file or the toolchain changes. The standing rule is to
run the tests of the part that changed during the work, and the whole suite once, when the parts are put together.

## What was considered and not adopted

- **`split-debuginfo = "unpacked"`.** Moves debug information out of binaries; not adopted because its interaction with
  sccache wasn't verified.
- **A faster linker (mold, wild).** Faster links, same output size. `rust-lld` is already the default on x86-64 Linux since
  Rust 1.90, and the problem was bytes written, not link time. Darwan uses `lld`, but for correctness: Qt binaries fail to
  link with GNU `ld.bfd`.
- **A shared target folder, or a global `build.build-dir`.** The first is finding 5. The second works on Cargo 1.98 but
  was declined in favour of lower snapshot retention.
- **Throttling build I/O.** Not effective with the NVMe `none` scheduler, and unnecessary once builds wrote less.
- **Per-project job caps.** Replaced by the shared jobserver in finding 13.

## Where things stand

- easyshot: 56 GB in `target/debug` after a week of feature-set and example copies, with the sweep capping it at 80 GB.
- Insensical: 31 GB. Sysman: about 3 GB in debug. Darwan and Quarry: about 4 to 5 GB each, debug and release builds
  together.
- Insensical's Rust suite: about a minute and a half on 32 cores, down from 254 seconds.

Two items remain open. Quarry's `target/` has grown back above its post-fix 1.7 GB through the same accumulation as
finding 4, and the window-test hang rate hasn't been re-measured since the move to nextest.

## Recommendations

For a Rust workspace with a large dependency graph, this is the block I'd start from:

```toml
[profile.dev]
debug = "line-tables-only"

[profile.dev.package."*"]
opt-level = 2
debug = false

[profile.dbg]
inherits = "dev"
debug = "full"
```

And then:

- **Measure first:** `du`, `size -A`, `/proc/pressure/io`, `cargo tree -i`.
- **Use one integration-test binary per crate** when there are many test files.
- **Clean `target/` on a schedule,** and account for snapshots and TRIM when you do.
- **Never share a target folder** between checkouts; share sccache instead.
- **Measure `incremental = false`** for your project before adopting it.
- **Run tests with nextest:** a per-test timeout, a retry for known hangs, test groups for shared resources, and the
  slowest tests first.
- **Keep timing tests out of the everyday run.**
- **Make tests clean up after themselves,** particularly in a memory-backed `/tmp`.
- **Keep a build profile per purpose.**
- **Put builds below the desktop,** and run only the tests a change can affect.

None of these are novel. Most are what I'd check on any server running out of disk. With Rust, the build is what fills it.
