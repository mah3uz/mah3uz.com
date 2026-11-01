---
title: Security that lives in the browser is decoration
published_at: 2026-10-03T09:00:00Z
topics: [security, operations]
excerpt: Nibble's Control Plane locked itself after fifteen idle minutes — and a page reload walked straight back in. Two humbling fixes, and the sysadmin's rule behind them - enforce where the state lives.
art: /art/posts/security-in-the-browser.svg
---
This one was humbling, so I'll start with it.

Nibble's Control Plane had an idle lock. After fifteen quiet minutes it covered the screen and asked for your password. It
looked exactly like a security feature. It wasn't one, because the whole thing lived in the browser. The session on the server was still perfectly valid, so **reloading the page skipped the
lock entirely**.

Anyone who has administered servers for long enough knows this shape of mistake, because it is everywhere: the firewall
rule on the wrong interface, the `sudo` restriction that a shell escape walks around, the hidden admin link that is only
hidden. Enforcement has to happen where the state lives. Anything else is a hint.

## Expiry belongs to the session

The fix was to make the server responsible. Every Control Plane request now records when the session was last active.
When a request arrives after too long a gap, the session is deleted on the server and its cookie with it, so a reload
lands on the sign-in page, as it always should have. The default is two hours, and a site can choose its own.

Two details mattered more than the main idea:

- **Asking the time must not reset the clock.** The browser still counts down so it can warn you a minute before. To stay
  in step, it asks the server how long is left — and that question must not count as activity. Otherwise an open tab
  would keep its own session alive forever by politely checking on it.
- **Losing a session shouldn't lose your work.** If your session ends while you're halfway through a page, a dialog asks
  for your password (and your two-factor code, if you use one) and signs you back in right there, with everything you
  typed still on the page. Security that punishes people teaches them to work around it.

And the test that mattered wasn't a unit test. I set the idle time to two minutes, signed in, waited for the warning,
waited for the dialog, and reloaded. Sign-in page. Then I did it again and signed in through the dialog, and checked that
the page was the one I'd left.

## The endpoint that a cleanup almost opened

The second story is about the opposite risk: removing something and discovering what it was quietly protecting.

Rails ships a direct-upload endpoint at `/rails/active_storage/direct_uploads`, and out of the box it accepts uploads from
anyone. Nibble had drawn its own, authenticated route on that same path, which happened to hide the Rails one. When I
set out to hand every Rails default back to the application, giving that path back would have opened anonymous uploads to
the site's storage.

So the path now answers 404, and the Control Plane uploads through a route of its own that checks who is uploading. The
lesson I took: **when you remove a layer, ask what was standing behind it**. An accidental protection is still a
protection, right up until a well-meaning cleanup removes it.

## The rule, written down

From both stories, the rule I now apply to everything I build — and the one I've applied to servers for years:

1. **Decide where the truth lives**, then enforce there: the session on the server, permissions in the database, limits in
   the daemon. The interface may *show* the rule; it never *is* the rule.
2. **Distrust anything that is merely hidden.** Unlinked pages, disabled buttons and overlays are presentation.
3. **Test the bypass, not just the happy path.** Reload the page. Call the endpoint directly. Copy the request with curl
   and change one thing.
4. **Look behind what you remove.** Before deleting a route, a rule or a proxy, find out what it was shadowing.

A security feature that only exists in the browser is a UI feature. That line is now in Nibble's blog, and it's on a sticky
note in my head.

The full write-ups: [The lock screen a reload could skip](https://nibble.ink/blog/the-lock-screen-a-reload-could-skip) and
[Giving Rails back to the app](https://nibble.ink/blog/giving-rails-back-to-the-app).
