---
title: Keeping a daemon alive
published_at: 2026-11-03T09:00:00+06:00
topics: [operations, rust, linux]
excerpt: Insensical's daemon owns every terminal you run, so it mustn't die and it mustn't stall. What threatened it wasn't clever bugs. It was fork getting slower with every thread, a signal mask children inherit, a cgroup that gets cleaned up, and a 1 KiB read on a Mac.
featured_image: art/posts/daemon-alive.svg
---
I've had tmux running on servers for most of my career. Its best feature is the one you never think about: you
disconnect, the network drops, your laptop sleeps, and when you come back everything is still running. A multiplexer's
server is a promise that your work outlives your connection to it.

[Insensical](/projects/insensical) makes the same promise for a desktop where you might be running five coding agents
at once. A background daemon owns every program; the native window, the terminal interface and the browser page are all
clients of it. Close the window and nothing stops. Upgrade the program and nothing stops either.

A process that makes that promise has to be boring in a very particular way. It can't crash, it can't stall, and it
can't take anything down with it when it does restart. Almost none of what threatened that in practice was in my code's
logic. It was in the operating system underneath, in the places where a process meets the kernel, systemd and the other
processes on the machine. That's where my sysadmin years paid for themselves.

## Two programs, threads, and no async runtime

The first decisions were structural. Insensical is two binaries: `isc`, which is the daemon, the command line and the
terminal interface, and `insensical`, the window. The reason is in the first rows of the decisions log: *"The daemon must
run where no GPU or window-system library exists."* A daemon that links against a GPU stack can't run on a headless server,
and it carries a few hundred megabytes of libraries that have nothing to do with keeping a shell alive. `isc` is one
statically linked file.

Inside the daemon, I chose plain threads and blocking I/O over an async runtime:

> Threads and channels, not an async runtime … blocking I/O on a few dozen threads is simpler than a second runtime in the
> GUI.

Each pane gets a thread that blocks on its pseudo-terminal. Before trusting that at scale, I measured it with a thousand
panes: no wake-ups while idle, 36 kB of memory touched per thread, and 0.07 ms to answer a command. I rejected a single
thread for quiet panes and smaller stacks. The simple design held.

One more structural rule is worth mentioning because it's the opposite of Rust's default. When a thread panics while
holding a lock, Rust *poisons* the lock and every later attempt to take it fails. In most programs that's sensible. In
Insensical the daemon takes the lock anyway. The reason given in the log is the whole philosophy of the daemon:
*"Refusing would turn one failed pane into losing every program."*

## fork got slower with every pane

The first real scaling problem appeared when I restored a saved layout with a thousand panes. The daemon took 20 to 32
seconds before its socket answered.

![Restoring 1,000 panes: 20 to 32 seconds with fork, about one second with posix_spawn](art/posts/keeping-a-daemon-alive/spawn.svg)

The cause was `fork`. To start a pane's shell, the daemon forked and then `exec`ed. `fork` copies the parent's memory map,
and the kernel's cost for that grows with the parent's size and its number of threads. And the daemon has a thread per
pane. In a bare test program, `fork` took 0.4 ms with no threads and 4.5 ms with a thousand. In the daemon it was 18 ms a
pane. Each pane started made the next one slower to start.

The fix was `posix_spawn`, which on Linux creates the child without copying the parent's memory map. The child is spawned
as the leader of a new session, then opens the pane's terminal so that it becomes the controlling terminal, which is what a
shell expects. Spawning dropped to 3 ms a pane, and restoring a thousand panes to about a second.

It had one sharp edge, found the next day. `execvp` quietly runs a script with no `#!` line through `sh`, as shells always
have. `posix_spawn` refuses it. So a pane whose command was a bare script stopped starting. The daemon now does what
`execvp` does when it sees that error.

The same thousand-pane test found a second cost. Saving the layout serialised the daemon's whole model under its lock on
every change: 800 kB a change at a thousand panes, and about two fifths of the daemon's time. It now compares what it last
saved with what it has, and writes only when they differ.

## The mask children inherit

The daemon handles signals the careful way: it blocks them in every thread and takes them with `sigwait` on one thread, so
a signal never interrupts some random thread in the middle of something.

There's a catch that every Unix programmer meets once. A blocked signal mask is inherited by child processes, and survives
`exec`. Every shell the daemon started would have had `SIGINT` and `SIGHUP` blocked. Ctrl-C would do nothing in any pane,
and closing a pane would never hang up its program. So every child has its mask cleared before `exec`. With
`posix_spawn`, that's part of the spawn attributes.

## The shutdown race

At machine shutdown, every process gets `SIGTERM` at roughly the same time. Shells usually exit a moment *before* the
daemon is told. The daemon sees a pane's program exit, removes the pane as it should, saves the layout... and the next
morning your projects are empty.

The rule now is that a save that *removes* panes is written two seconds late, a save that adds a pane is written at once,
and changes inside one pane wait a quarter of a second. When the daemon gets `SIGTERM`, `SIGINT` or `SIGHUP`, it writes any
pending change that removes nothing, drops any pending change that removes panes, and freezes the file. A shutdown can no
longer persuade it that you closed everything.

## setsid isn't enough any more

For thirty years, the way to start a background process that survives its terminal has been `setsid`: a new session, no
controlling terminal, no hang-up when the terminal goes. Insensical's clients start the daemon on demand, so this mattered.

On a modern Linux desktop it isn't enough. systemd puts each application you launch in its own transient *scope*, a cgroup,
and when the application exits, its scope is cleaned up, which kills every process still inside it. Sessions are irrelevant
to cgroups. Start the daemon from a terminal emulator, close the terminal, and the daemon dies with it, `setsid` or not.

So a client starts the daemon in a scope of its own:

```
systemd-run --user --scope --collect --quiet --unit=insensical-daemon-<hash>
```

If that exits within half a second (on a machine without a systemd user instance, for example), it falls back to plain
`setsid`. Test daemons never get a scope, so a test can't leave a unit behind on the
machine it ran on. This is exactly the kind of bug a developer-only background would never think to look for, and an
administrator who has chased "why does my process die when I log out" a dozen times looks for first.

## Upgrading in place, and the fine print

The headline feature of the daemon is `isc restart-server`: replace the running daemon with the newly installed version
and keep every terminal, every program and every screen.

I considered the usual design, passing the pseudo-terminal file descriptors to a new process, and rejected it. Insensical
instead calls `exec` on the new binary *in the same process*. It stays the parent of every pane's program, it keeps its
process ID, and there's never a moment where two daemons both think they're in charge.

![Upgrading in place: the same process writes its state, checks the new binary can read it, finishes in-flight work and execs](art/posts/keeping-a-daemon-alive/handover.svg)

`exec` has no undo. Once it's called, the old program is gone. So before the real handover, the daemon runs the new binary
once as `isc carried` and asks whether it can read the state it's about to be handed, with ten seconds for an answer. Only
then does it write the state to an unnamed file and `exec`.

The fine print took several rounds:

- **The environment leaks.** The new daemon finds its state through a file descriptor number in `INSENSICAL_HANDOVER`. But
  a daemon inherits its environment from whatever started it, so that variable could arrive from somewhere else. The new
  daemon only accepts the number if it names a regular, unnamed file, owned by the user, above descriptor 2. And it removes
  the variable before it starts any thread, so no pane's program ever inherits it.
- **Work in flight is lost at exec.** A notification command, or an HTTPS post to a phone, running at the moment of the
  handover was simply cut off, and the command left unreaped. The daemon now waits up to ten seconds for each before
  anything stands still. Fixing that showed a second bug: a send that panicked kept its slot, and four of those would have
  left every later notification unsent.
- **Listeners must survive without a gap.** The optional hub that serves the browser page holds TCP listeners. Re-binding
  after `exec` would leave the port free for a moment, for any other user on the machine to take. So the hub clears
  `FD_CLOEXEC` on its listeners just before `exec` and sets it back before any thread starts.
- **A failed exec changes signals.** If `exec` fails, the process carries on as the old program, but starting a program had
  set `SIGPIPE` back to its default action, which is to die. The first write to an `ssh` connection that had gone away
  would have killed the hub. It sets `SIGPIPE` back to ignored after a failed `exec`.

Screens come through the handover as engine snapshots, but only if the new daemon has exactly the same terminal engine.
Otherwise they're replayed from output, which I measured as imperfect: for screens with random scrolling regions, about
one in ten came out with rows displaced. That's written down too.

## A slow client must never slow the program

A daemon with many clients will always have one that falls behind: a laptop on bad Wi-Fi, a window that's busy, a phone
that went to sleep. The rule from the very start was:

> A client that falls behind is resynced by snapshot, not buffered.

The rejected alternatives were unbounded queues, which turn one slow client into the daemon's memory growing without
limit, and back-pressure on the pseudo-terminal, which means a slow *viewer* throttles the *program*. Your build shouldn't
run slower because a phone is watching it.

So each client has a bounded queue. When it's full, the client is cut off: its queue is dropped and replaced with a single
frame that says why, `Ending{Slow}`, and the client gets one second to read that frame before its socket is shut. The second
matters. Without it the client sees a broken connection and has to guess; with it, it reconnects on its own and tells you
it did. On the client side, the connection reader stops reading once 4 MiB of output is waiting, so the queue that fills
up is the daemon's bounded one, where the limit can see it, not the window's own memory.

## A Mac reads a kilobyte at a time

The macOS port brought its own lesson. On a Mac, a pseudo-terminal hands over at most 1,024 bytes per read. A 200 MB flood
of output became 200,000 separate reads, each one waking the pane's thread and sending a message to every client.
Throughput was 67 MB/s, a third of what a terminal on its own managed.

The fix is to gather: during a flood, after each kilobyte the daemon waits up to 100 microseconds for the next one before
sending. It only does this in a flood. A single key's echo still goes out immediately, because the thing a person notices
first is a keystroke that feels late.

The port also taught me to write down what I hadn't run. A lot of the Mac code was written on Linux, and the platform notes
say: *"Code not built and run on a Mac is unverified."* Plenty of commit messages end with "Not built or run on a Mac". I'd
rather read that than find out.

## One static binary, and the TLS that comes with it

`isc` is one statically linked file for x86-64 and arm64 Linux, and the arm64 build is linked where no C is compiled at
all. Servers are often arm64 with an unusual C library, and I wanted to copy one file onto a machine and have it work.

That decision chose the TLS stack. `ring`, `aws-lc` and OpenSSL all need a C compiler. Insensical uses `rustls` with
`rustls-graviola`, a provider written in Rust and assembly by the author of rustls. I rejected the pure RustCrypto provider
because it says of itself that it isn't meant for production. graviola has its own catch: it needs AES, AVX2, ADX and BMI2
on x86-64, and AES, SHA-2 and PMULL on arm64. A Raspberry Pi 4 has none of the arm64 ones. So the hub checks the CPU
first and refuses TLS with a sentence explaining why, instead of failing with an illegal instruction.

## Idle means idle

The last property is the quietest. A daemon that holds your terminals all day should cost nothing when nothing's
happening. Measured with eight idle shells, the daemon had zero wake-ups in ten seconds. The architecture document states
the figure with its limits: *"daemon: 0 wakeups in 10 s holding 8 idle shells, measured with no tray. GUI: not measured."*
The tray's thread on Linux checks the settings every two seconds, and it says so.

## What carries over

- **Measure at the scale you claim.** A thousand panes found two problems that ten never would have.
- **`fork` is not free in a big, threaded process.** `posix_spawn` is, mostly.
- **Children inherit more than you think:** signal masks, environment variables, descriptors without `FD_CLOEXEC`.
- **Distrust a shutdown.** Treat removals during one as suspect.
- **`setsid` doesn't escape a cgroup.** On a systemd machine, start long-lived processes in a scope of their own.
- **`exec` in place is the safest upgrade there is,** once you've handled everything that doesn't survive it.
- **Never let a slow reader slow the writer.**
- **Write down what you didn't run.**

None of this is new. It's the same list of things I'd check on a server that keeps losing a process. The difference is
that this time I was the one writing the process.
