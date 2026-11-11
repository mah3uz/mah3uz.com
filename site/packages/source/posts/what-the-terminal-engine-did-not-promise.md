---
title: What the terminal engine didn't promise
published_at: 2026-11-05T09:00:00+06:00
topics: [rust, engineering, security]
excerpt: Insensical is built on libghostty-vt, Ghostty's terminal engine as a library. It gave me a superb parser. It didn't promise that every screen could be saved, that every saved screen could be read, or that it would answer questions in the right order. Here is what I built around it.
art: /art/posts/terminal-engine.svg
---
A terminal emulator is two programs pretending to be one. One half is a parser and a state machine: it reads the bytes a
program writes, escape sequences and all, and keeps a model of the screen, the cursor, the colours, the scrollback. The
other half draws that model. The first half is where the decades of compatibility live, and it's the half you least want to
write yourself.

[Insensical](/projects/insensical), my terminal multiplexer, doesn't write it. It uses **libghostty-vt**, the terminal
engine from Ghostty, packaged as a library. It's an excellent piece of work and I'd choose it again. But a library promises
a particular set of things, and the space between those promises and what a product needs is where I spent a surprising
amount of October.

## Why this engine, and how it's held

Insensical's design depends on *replicas*. The daemon keeps the authoritative terminal for every pane; each window that
shows a pane keeps a replica of it; the raw bytes from the program go to both, so every byte is parsed exactly once by the
copy that draws it. For that to work, a replica has to be able to start from somewhere: when a window attaches to a pane
that has been running for an hour, it needs the screen as it is now, not a replay of an hour of output.

libghostty-vt has an open snapshot format: it can encode a terminal's whole state and decode it into another terminal.
That's the feature the architecture rests on. Snapshots are used to attach a window (0.8 ms for a 200 × 60 pane with 4,000
lines of history), to resynchronise a client that fell behind, to keep screens across a restart of the daemon, and to send
screens to other machines.

There's no official Rust binding, so Insensical uses the community `libghostty-rs` binding, pinned to an exact commit and
used in exactly one crate. The decision record says why in one line: *"No official binding exists; one crate isolates its
churn."* The engine itself is untagged, and the risk register says plainly that *"its snapshot format has no compatibility
promise."* So the Ghostty commit the engine is built from is written down in three places, and a test fails if they
disagree. Client and daemon refuse to talk unless their protocol number *and* engine are exactly the same, because a
snapshot from one engine promises nothing to another.

All of that is the normal care you'd take with any young dependency. The interesting part is what happened at the edges.

## A screen that couldn't be saved

The first one showed up as a pane that no window could attach to. The shell was running fine; you just couldn't see it.
It stayed that way for as long as the shell ran.

The trigger turned out to be ordinary: close an editor that had a file with Chinese or Japanese text in it, then make the
pane narrower. Wide characters take two cells. When the engine shrinks a screen, it can leave the first half of a wide
character in the last column and cut off its second half. That happens on the alternate screen (the one full-screen
programs like editors use) every time, and on the main screen when line wrapping is off. A terminal holding that half
character can't be encoded at all: the encoder fails for the whole terminal with `InvalidValue`.

And the alternate screen keeps whatever the last program drew after the program exits. So the broken cell outlives the
editor, and every attach fails until something redraws that spot.

The fix comes in two parts, and neither touches the engine. During a resize, Insensical turns wrapping on, so the main screen
reflows its lines instead of cutting them. Then a `mend` step looks for a half character and repairs it *the way a program
would*, by writing to the terminal: on a visible alternate screen, a cursor move and an erase for each broken half; on a hidden
one, switch to it, clear, and switch back. If the program is in the middle of writing an escape sequence at that moment,
the snapshot is taken from a terminal rebuilt from the replay instead.

I like fixes that work by speaking the same language as the system they're fixing. Writing escape sequences into the
terminal can't leave it in a state the engine doesn't understand, because that's the engine's normal input.

## A screen that couldn't be read back

The second was worse, because the failure looped. A window asked for a pane's screen, received a snapshot, couldn't decode
it, asked again, and was sent the same snapshot. It happened with a pager open in a large pane, around 300 × 160.

Large screens are stored in several pages internally, and above roughly 46,000 cells a screen spans more than one. Scrolling
the alternate screen from its top row moved a row across a page boundary, and the engine counted one style too many. It then
encoded a page that it couldn't read back.

I'll be honest about the state of this one: at the engine commit Insensical moved to a few days later, my reproduction no
longer fails. Either it was fixed upstream in between, or the reproduction misses something. Either way, the lesson didn't
change, and neither did the fix.

![Never send a snapshot you can't read: encode, read it back into a throwaway terminal, and fall back to a redraw from the replay](/art/posts/what-the-terminal-engine-did-not-promise/readback.svg)

**The daemon now reads back every snapshot before it sends it.** It encodes the screen, decodes the first part into a
throwaway terminal, and only sends the bytes if that works. If it doesn't, it sends a snapshot of a terminal redrawn from
the pane's replay. That copy is less complete (it loses hyperlinks, the shell's prompt marks and the hidden screen), but a
slightly poorer screen beats a pane you can't see at all.

## Treat a saved screen like a packet from a stranger

Once I started looking at snapshots as data that could be wrong, a more serious question came up. Snapshots aren't only
passed between threads of one process. They're written to disk when the daemon restarts, and they travel over the network
to other machines. The bytes a decoder reads might come from a file or a socket.

A snapshot page begins with 20 bytes of claims: how many columns, how many rows, how much room for styles, links, joined
characters and text. The decoder lays out its tables by those numbers using 32-bit offsets and doesn't add them up first.
I found that changing one byte, and fixing up the CRC-32C checksum so it still matched, made the decoder write outside the
page.

The engine's authors didn't promise this was safe input, and I don't think they should have to. The engine reads what it
wrote. But I'd been about to feed it bytes from places it never expected. So every snapshot goes through a small guard
before it reaches the decoder: records must be whole, a page must be exactly as wide as the terminal, and the room a page
claims must add up to at most 1 GiB in total. The guard is tested with about 6,000 pages that each claim something different
at every power of two of each number, plus 3,000 at random.

After many years of running servers, this is the reflex I trust most. A state file is input. A cache is input. Anything that
crossed a process boundary is input, and input gets checked before it's believed.

## Every workaround has a test that fails without it

At this point Insensical had three workarounds wrapped around an engine that is moving quickly upstream. The danger with
workarounds is that you keep them forever after the bug is gone, or remove them while it's still there.

So each one is held by a test that runs against the real engine with the workaround switched off. When the engine moved
to a new commit, the commit message recorded the result:

> Every workaround is kept: with each taken out, a page that claims too much room or too few columns still ends the
> process, and a wide character cut in two is still not encoded.

When one of those tests starts passing without its workaround, that's the signal to delete the workaround. Until then, it
stays.

## A hundred thousand pictures

The kitty graphics protocol lets a program place an image in the terminal. Each placement is about 20 bytes:
`ESC _ G a=p,i=1,C=1,q=2 ESC \`. The engine keeps every placement, and the cost of adding one grows with how many already
exist, so the total cost grows with the square of the count. The binding limits the bytes of a picture and the size of one
picture. Nothing limits the count.

![Kitty image placements: from 1.1 ms for a thousand to 16.28 seconds for a hundred thousand](/art/posts/what-the-terminal-engine-did-not-promise/placements.svg)

In a debug build of the engine, a thousand placements took 1.1 ms. Sixteen thousand took 212 ms. A hundred thousand took
16.28 seconds, during which that pane's writer is held. A 2 MB file sent to `cat` can do it.

This one I haven't fixed, because the fix belongs in the engine. What Insensical does is bound the aftermath: of one
picture's placements in view, only the 256 nearest the front are drawn. And the limit is written in the architecture
document, where someone choosing whether to rely on it will find it. Not every problem is yours to solve, but every problem
you know about is yours to write down.

## Answer in the order you were asked

Insensical works out what each pane is doing, so that when you run several coding agents at once you know which one is
waiting for you. The best evidence is the program saying so. For that there's a draft escape sequence, OSC 7501, with which
a program can report that it's idle, working, blocked or done.

A program that wants to use it first has to know whether the terminal understands it. It does that the classic way: it
sends the question `OSC 7501 ; ?`, then immediately sends `CSI c`, the device attributes request that every terminal
answers. Whichever answer arrives first decides it. If the 7501 answer comes before the device attributes, the terminal
understands. If the device attributes come first, it doesn't.

![Answer in the order you were asked: Insensical splits the output at the end of the question and answers before the engine sees CSI c](/art/posts/what-the-terminal-engine-did-not-promise/osc7501.svg)

The engine answers `CSI c` itself, internally. Its C interface doesn't pass an unknown OSC sequence on and gives no
callback for it. So if Insensical noticed the question after the engine had processed the whole chunk of output, the
engine's answer would already be on its way, and the program would conclude it wasn't heard.

The solution is a small scanner of Insensical's own that runs over output before the engine sees it. When it finds a 7501
question, it gives the engine the output only up to the end of the question, writes its own answer, and then gives the
engine the rest. Only the daemon's authoritative terminal answers. Replicas see exactly the same bytes and must stay silent,
or the program would get two answers to every question.

Because this scanner sits on the path every byte of output takes, it has to cost nothing. It gives up on any other OSC
sequence after 64 bytes and on a 7501 report after 4,096, and every field of a report (key, id, app name, title, the base64)
is checked against the protocol's limits before any of it is believed.

## The prompt with nothing on the wire

The opposite problem: `sudo`, `ssh` and `git` ask for passwords and send nothing that says so. No escape sequence, no bell.
A pane waiting for a password looks exactly like a pane that's busy.

The decision record has one row for this, and I'm fond of it:

> A terminal taking a line with echo off in canonical mode is a pane that waits.

The daemon owns the pane's pseudo-terminal, so it can read its terminal modes. A program reading a password puts the
terminal in canonical (line-at-a-time) mode with echo turned off. That combination is the signal, and it ends when the modes
change back or the command ends. I rejected matching the word "password" on screen, and rejected echo-off on its own, since
plenty of full-screen programs turn echo off. The architecture document has a rule that covers all of it: *"What is on the
screen is never read to guess a state."* Screens lie; terminal modes don't.

The same fact turned out to be useful twice more. Insensical can predict your typing locally, the way Mosh does, to hide
latency on a remote machine. It must never draw a predicted character into a password prompt, so prediction only turns
on after two typed characters in a row have been confirmed by the real screen. And a remote machine whose `ssh` asks for a
password is never retried on a timer, because each retry is a failed login in someone's auth log. The rejected design would
have made 2,880 attempts a day.

## Reporting upstream

Each of these has been written up as a report for the engine, with a reproduction and the names of the tests that show
it. At the time of writing, none of them have been sent yet. I want to send them with the reproductions checked against the
latest engine, not the one I happened to be pinned to, and the engine moves quickly. That's on my list, and it's the right
order of operations: work around it in your own code first, then help fix it where it belongs.

## What carries over

- **A library promises a parser, not a product.** Find out what it actually promises, and write down the rest as risks.
- **Hold a fast-moving dependency in one place,** pin it exactly, and test that the pin is the same everywhere it's
  written.
- **Read back what you write** before you send it somewhere it can't be fixed.
- **Anything that crossed a boundary is input,** including your own files.
- **Keep each workaround with a test that fails without it.**
- **When you can't fix a limit, publish it.**

Ghostty's engine saved me months. Respecting it meant learning exactly where its guarantees ended, and building the rest
myself.
