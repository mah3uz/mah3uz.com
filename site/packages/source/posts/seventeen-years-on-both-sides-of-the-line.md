---
title: Seventeen years on both sides of the line
published_at: 2026-10-31T09:00:00Z
topics: [engineering, operations]
excerpt: Most organisations separate the people who build software from the people who run it. I have spent my career doing both. Here is what that taught me about designing systems that survive contact with production.
art: /art/posts/seventeen-years.svg
---
Most organisations draw a line between the people who *build* software and the people who *run* it. Developers write the
application; administrators, operations, or — in more recent vocabulary — platform teams keep it alive. Tickets cross the
line in both directions, and a surprising amount of every outage lives in the gap.

I have spent more than seventeen years on both sides of that line, often on the same day. I write software, and I
administer the Linux servers it runs on: provisioning machines, managing their configuration, automating deployments,
patching, monitoring, backing up, and being the person who gets the call when something breaks. Linux has been my
operating system since I first started using computers, so the servers never felt like someone else's territory.

This is not a story about one job or one stack. It is the handful of lessons that kept proving themselves, across clients,
languages and decades of changing fashion.

## The gap is where the expensive problems live

The bugs that cost the most rarely belong to one side. A page is slow, and the application team profiles the code while the
real cause is a database server configured for a machine half its size. A deploy fails, and the developers stare at their
diff while the disk is full of logs nobody rotated. An "intermittent" error turns out to be a DNS cache, a connection pool
limit, a memory cap in a container, a clock that drifted.

Each of those is easy for someone who can see both layers at once, and nearly impossible for two teams passing tickets
across a boundary. The most valuable thing I bring to a project is not any particular language; it is the habit of
following a problem down through every layer until the behaviour makes sense.

## Build like you will be paged for it

The single biggest change that operating systems made to how I write software is this: **I design for the person who will
run it.** Usually that person is me, at an inconvenient hour, with incomplete information.

That turns into concrete habits:

- **Failure modes are designed, not discovered.** What happens when the database is unavailable for thirty seconds? When the
  disk fills? When a dependency hangs instead of failing? If the answer is "we'll find out", the design isn't finished.
- **Logs are written for the reader at 3am.** Not "error occurred", but what was being attempted, with what input, and what
  the operator should check first.
- **Starting and stopping are features.** A service that shuts down cleanly, resumes where it left off and can be restarted
  without ceremony is worth more than most of its features.
- **Backups exist only if restores work.** Untested backups are a belief system. Schedule the restore drill like any other
  task.

You can see these in the products I build today. Sysman's first design rule is that *"the last reading before a crash is
on disk"* — every sample is synced before the next one is taken, precisely because the moment you most need the data is
the moment the machine died. Darwan's lock-screen supervisor exists because a lock screen that crashes must never leave
someone locked out.

## Fewer moving parts

Every component in a system is something to install, configure, patch, monitor, back up and eventually migrate. When I
started, a "proper" web stack meant a web server, an application server, a database, a cache, a queue, a search server and
something to supervise them all. Each was reasonable on its own. Together they were a full-time job.

I have become steadily more conservative about adding parts. For most applications, a well-understood database on a
well-run server is not a compromise; it is the right design. Nibble, the CMS I build, deliberately uses one SQLite database
for content, cache, background jobs and full-text search, and deploys as one container to one machine. Its architecture
notes say it plainly: *"No Redis, no Elasticsearch, no separate front-end application, no GraphQL… Each is a thing nobody
has to run, monitor or pay for."*

That isn't an argument against scale. It is an argument for earning complexity with evidence — measured load, real
requirements — rather than adopting it in anticipation.

## Refuse loudly rather than continue wrongly

Operations teaches you to fear the silent failure far more than the loud one. A service that crashes is noticed in
minutes. A service that quietly does the wrong thing can corrupt data for weeks.

So I build systems that refuse:

- A configuration typo should stop a daemon at start-up, not quietly disable a feature. Sysman does exactly this, *"so a
  typo cannot silently switch something off."*
- A release script should check *everything* — clean tree, correct version, written changelog, credentials for every
  destination — before it does anything public, and then ask once. My release scripts all follow that pattern.
- An upgrade should refuse to proceed over files someone edited by hand, rather than overwrite them. Nibble's upgrade
  compares every file against the release manifest and stops on any drift.
- A value you couldn't read should be shown as unknown, never as a reassuring zero.

## Automate the third time

I do a task by hand the first time, so I understand it. The second time, I write it down. The third time, I automate it —
and the automation becomes the documentation. Server builds, deploys, backups and releases should be repeatable by anyone
on the team, including a future version of me who has forgotten every detail.

The goal of automation is not speed. It is *repeatability*: the confidence that the thing that worked on Tuesday will work
the same way on Friday, for someone else, without the folklore.

## Small releases, written changelogs

Large releases concentrate risk; small ones spread it so thin it nearly disappears. A change you can describe in one
sentence is a change you can verify, monitor and undo. I would rather ship ten small releases in a fortnight than one big
one at the end of the quarter.

And every release deserves a changelog written for the person running the system, not for someone reading the diff: what
changed, what they need to do, and what to watch for. It is the cheapest reliability tool there is.

## Security is a default

Seventeen years of patching servers will make anyone a little paranoid, in a useful way. Security works when it is the
path of least resistance: services that run with the least privilege they need, sockets that only their owner can open,
secrets that never reach logs or shell history, releases that are signed and verified, inputs that are validated at every
boundary that matters. The insecure option should be the one that takes extra effort.

## The thread

Languages and frameworks changed many times over these years — the operating system under them didn't, and neither did
the questions: *What happens when this fails? Who will run it? How will they know what's wrong? Can we undo it?* Answering
those questions early is most of what I mean by engineering.

It is also why I still enjoy the work. The craft is in the details, and the details are in the whole system.
