---
title: Why this site runs on a CMS I built
published_at: 2026-09-29T09:00:00Z
topics: [product, engineering]
excerpt: Every developer eventually writes a content management system. I did it on purpose, after years of installing, patching and rescuing other people's. These are the decisions that made Nibble — and the one I got wrong first.
art: /art/posts/cms-i-built.svg
---
Every developer eventually writes their own content management system. It usually happens by accident: a blog engine
grows an admin screen, then a media library, then a plugin system, and one day it is a CMS nobody meant to build.

I built Nibble on purpose. After years of installing, configuring, upgrading, securing and occasionally rescuing content
systems — as the developer building the site and as the administrator keeping it alive afterwards — I knew exactly what
I wanted, and I could not find it.

## What I was looking for

Content systems fail people in two predictable ways. The hosted ones are lovely until you need something they don't
support, and then you learn that your content, your URLs and your release schedule belong to someone else. The
build-it-yourself frameworks give you total freedom and then ask you to assemble, secure, monitor and upgrade a dozen
moving parts for a site with three editors.

I wanted something in between: **an application I own**, installed into my own repository, that I can read, change and
deploy like any other codebase — with a database I can copy with one command, and an upgrade path that never touches my
code.

## The decision everything else rests on

Nibble draws one firm line. Everything under `vendor/nibble/` belongs to Nibble; everything else — schema, content, theme,
deployment configuration, custom Ruby — belongs to the site. An upgrade replaces that folder whole.

That sounds like a packaging detail. It is actually the whole upgrade story. Because a release cannot have touched anything
the site owns, a site can take a release without reading it. The upgrade command checks every file in the folder against
the release manifest and refuses if someone edited one in place, snapshots the database first, and keeps the previous
release so you can step back. As someone who has spent too many evenings untangling a "minor" CMS upgrade that overwrote a
customisation, I value that guarantee more than any feature.

## One database, one machine

Nibble uses SQLite for everything: content, the page cache, background jobs and full-text search. It deploys with Kamal as
one container on one server, with nightly snapshots shipped off the machine.

From an operations point of view, this is the part I am happiest with. There is no cache cluster to size, no search
service to keep in sync, no queue to monitor separately. The whole system is one process tree and one file you can back
up. For the sites Nibble is built for, that is not a limitation; it is the reason they will still be running, quietly, in
five years.

## Caching that knows what changed

Page caching is easy to add and notoriously hard to invalidate. Nibble solves it by owning the queries. Each view declares
what it needs in a small YAML file beside it, and Nibble runs those queries itself — so it knows exactly which records a
page depended on. The rendered page is cached against those records, and publishing a change clears exactly the pages that
used it.

## The one I got wrong first

Some content belongs in a pull request rather than an admin screen. Nibble lets a folder of Markdown be a collection —
this site's projects are exactly that.

My first version synced the Markdown files into database rows. It worked, until a page's route and its file disagreed and
nothing reported the difference: the schema said one address, the database held another, and the site served the wrong
one quietly. Two releases later I removed the sync entirely. Files are now read into an in-memory index when the site
boots: nothing is copied, nothing can drift, and there is no step to remember on a deploy.

It was a useful reminder of an old operations rule: **any two copies of the same truth will eventually disagree.** Design
so there is only one.

## AI agents, as the person who invited them

Modern sites have a new kind of editor: AI agents. Nibble lets them work on a site through MCP, but never as a superuser.
An agent's permissions are the intersection of the person's roles, the app's grant and the site's agent-access settings,
and live changes can be held until a human approves them. Every change, from any source, goes through one lifecycle that
requires an explicit actor — there is no default, so nothing can forget who is acting.

## Built on itself

This site is a Nibble site. The projects are Markdown files in the repository, the writing is edited in the Control Plane,
the theme is my own, and the whole thing deploys to a server I run. Writing your own CMS is usually a warning sign. Writing
one you would happily hand to someone else — and run for years — is a different project altogether, and it's the one I'm
working on.
