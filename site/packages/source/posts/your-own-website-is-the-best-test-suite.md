---
title: Your own website is the best test suite
published_at: 2026-09-27T09:00:00+06:00
topics: [engineering, product]
excerpt: One evening of clicking around my own documentation produced seven patch releases of Nibble. Fixtures with three files never find what real content finds — and some bugs only show up when you actually run the thing.
featured_image: art/posts/own-website-test-suite.svg
---
There is a stretch in Nibble's changelog where the version goes 0.14.1, 0.14.2, 0.14.3 and on to 0.14.7, all in one
night. I didn't plan it. It is what happened when Nibble's own documentation moved into a folder of Markdown files and I
spent an evening using it the way a reader would.

I have written tests for most of my career, and I still believe in them. But that night was a good reminder of what tests
are: proof that the cases you thought of behave. The cases you didn't think of are where software actually breaks, and the
quickest way I know to find them is to live on what I build.

## What three fixtures never touched

Collections backed by a folder of files were a lovely idea with a tidy test suite. The fixtures had three files. My
documentation has dozens of pages in nested folders, and every corner the fixtures never reached got reached in an hour:

- **Sorting.** A collection ordered by a number sorted it as text, so page 10 came before page 2. Every test passed,
  because no fixture had ten of anything.
- **Filtering.** The `where` and `not` conditions in a view's query didn't narrow a folder-backed collection at all.
- **Counting.** A blueprint didn't count the pages that used it, because those pages weren't rows in a database.
- **Writing.** The Control Plane offered to edit pages that live in a file. Two sources of truth for the same page is a
  bug waiting for a deadline, so those pages became read-only, with the file they come from named on the screen.

And my favourite: Nibble ran on one fixed time zone, wherever in the world a site was, set in a file a site couldn't
change. Scheduled publishing went by it. Nobody had asked for that time zone; it had simply never been noticed, because
my own clock happened to agree with it.

## Bugs that only running finds

Dogfooding isn't only about content. Some bugs live in the gaps between pieces that each pass their own tests, and the
only way to find them is to put the pieces together and run them.

When I freed up the names `User`, `Session` and `Current` so a site could run Rails' own authentication generator, I
didn't just read through the code to check. I made the install test *run the generator* on a freshly installed site. The
first run failed: Rails writes migrations called `CreateUsers` and `CreateSessions`, Nibble had migrations with the same
class names, and migration names have to be unique across every path. I would never have found that by reading.

Live Preview taught me the same lesson from the other direction. The first time I tried the new in-place updates on this
site, an update crashed halfway through patching the header. The page had been failing to hydrate all along — a full
reload had only ever shown it as a warning in the console. The cause was mine: I had regenerated the theme's types for a
different theme while this site's development server was running, and the post page had quietly lost two of its props.
The feature didn't create the bug. Using it for real revealed one that had been there for days.

## Seven releases is not chaos

Seven releases in one night sounds like a fire. It felt like the opposite. Each fix was small and each shipped with the
test that would have caught it, so the suite now knows about ten pages, nested folders and time zones. And each fix made
the next bug easier to see, because there was less noise around it.

One of the seven was about the release script itself. When it refused to cut a release because a check failed, it left
the version bumped and the changelog half-edited. Now a refusal puts every file back exactly as it found it. A tool that
says no shouldn't leave work behind for you to clean up — I wrote more about that in
[release scripts that refuse to half-ship](/blog/release-scripts-that-refuse-to-half-ship).

## What I do now

- **Run my own things first.** This site runs on Nibble; Sysman watches my workstation; Insensical holds my terminals.
  If something is annoying, I'm the first to be annoyed.
- **Use real content, not fixtures.** Real content has ten of things, long titles, nested folders and dates near midnight.
- **Make the end-to-end path a test.** If a feature promises that a generator, an installer or an upgrade will work, a
  test runs that generator, installer or upgrade on a clean machine.
- **Read the console.** A warning that a full reload hides is still a bug. It is just one that hasn't found its moment yet.

The longer versions of these stories are on the Nibble blog:
[Seven patch releases in one night](https://nibble.ink/blog/seven-patch-releases-in-one-night),
[Giving Rails back to the app](https://nibble.ink/blog/giving-rails-back-to-the-app) and
[Live Preview stops blinking](https://nibble.ink/blog/live-preview-stops-blinking).
