---
title: A lock screen that cannot lock you out
published_at: 2026-10-08T09:00:00Z
topics: [linux, security]
excerpt: Theming a login screen means writing to system directories as root; theming a lock screen means one bug can lock someone out of their own machine. How Darwan handles both — a supervised lock, and a root helper that trusts nothing it is given.
art: /art/posts/lock-screen.svg
---
Darwan is a theme manager for the two "gates" of a Linux desktop: the SDDM login screen and a Quickshell lock screen. Its
40 themes were designed by Darkkal44 for the qylock project; my work was the application around them. On paper that sounds
cosmetic. In practice it involves two of the most safety-sensitive things a desktop application can do: **writing to system
directories as root**, and **controlling the screen that stands between a user and their session.**

Both deserve the kind of care I would give a production server. Here is how Darwan approaches them.

## The failure that matters

A broken desktop theme is an annoyance. A broken lock screen is a person who cannot get back into their own computer —
possibly with unsaved work behind it, possibly with no idea how to switch to another terminal and recover. So the design
starts from one requirement: **under no failure should the user be left facing a black screen.**

### A supervisor, not a launcher

Darwan doesn't just start the lock screen; it supervises it. The lock process and its supervisor share a small protocol of
exit codes — authenticated, or a screensaver that was dismissed. Anything else is a failure, and the supervisor restarts the
lock with exponential backoff, from 100 milliseconds up to a two-second cap. Thirty seconds of stable running reset the
failure count.

The supervisor only gives up in one situation: when the lock *never took hold* — because, as the code puts it, *"a lock
that never took hold protects nothing."* Giving up on a lock that is protecting the session would be the dangerous choice;
giving up on one that never started is the honest one.

### A way in, always

If a theme fails to load, the user gets a plain fallback password prompt rather than a black screen. It isn't pretty, and it
doesn't need to be. It needs to work.

### Check the environment before you rely on it

On Hyprland, a replacement locker can only take over a session if the compositor is configured to allow it. Rather than
discover that at the worst moment, Darwan checks the setting and refuses to lock without it. It also configures idle and
sleep handling so the screen is locked *before* the machine suspends, not after it wakes — the default only waits for the
lock when the locker is the compositor's own.

### Test without risk

Finally, users can preview a theme without trusting it: live in the app with a test password, full screen on every monitor
with their real password, in SDDM's own test mode, or headlessly with screenshots. Before a release, every theme is loaded
offscreen and unlocked by typing a password — including from the screensaver mode — and any QML warning fails the check.

## A root helper with no trust in its caller

The login screen lives in system directories, so applying a theme requires root. The common shortcut is to run the whole
tool with `sudo`, or to have a privileged helper that does whatever the application asks. Both put a large, complex
graphical program in charge of root's decisions.

Darwan isolates the privileged work in a small helper, and the helper treats the application calling it as untrusted.

- **Authorisation is narrow.** The helper is started through polkit with an action pinned to its exact executable path.
- **Bytes, not paths.** The helper reads a single JSON request, capped in size, followed by the file contents on standard
  input. *"Nothing is taken from a path"* — so it can't be tricked into reading or writing a file it shouldn't.
- **Validate again.** The helper re-validates every setting against the theme's own manifest rather than trusting that the
  application already did.
- **Check what files are, not what they're called.** Fonts, images and videos are checked by their magic bytes — *"a renamed
  file of another kind is refused"* — and capped in size.
- **Write atomically, and only your own files.** Files are written atomically; the active-theme symlink is staged and swapped
  into place with a rename; and the helper refuses to touch anything that *"exists and is not darwan's symlink."* Its
  configuration file is named so that it sorts last, and wins, without editing anyone else's.

The helper is around nine hundred lines of Rust with its own test suite, which is the point: a small, auditable piece of code
is the only kind that should run as root.

## A caching bug worth remembering

One bug taught a lesson I've learned before in operations. After switching themes, the login screen sometimes showed the new
theme's settings on the *old* theme's widgets. The greeter caches compiled QML by file path and modification time — and every
packaged theme shared the same link path and the same modification time. So the cache was technically correct and practically
wrong: it kept running the previous theme's compiled code.

The fix was a separate link per theme, with old links cleaned up. The lesson is general: **every cache is built on an
assumption about what makes two things the same**, and a deployment that violates that assumption fails silently. When
something "can't be stale" but is, look for the cache key.

## The same principles, anywhere

Strip away the theming, and these are the principles I apply to any privileged or safety-critical component:

1. Design around the failure that hurts most, and make it impossible rather than unlikely.
2. Supervise what must stay running, with backoff and a clear rule for giving up.
3. Keep the privileged part small, and let it trust nothing it is handed.
4. Prefer streams of bytes to paths, atomic swaps to in-place edits, and refusing to proceed over guessing.
5. Test the real failure modes — headlessly, repeatedly, before every release.
