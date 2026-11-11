---
title: Rewrite history only when you can prove it
published_at: 2026-10-17T09:00:00+06:00
topics: [engineering, operations]
excerpt: Nibble had thirty-six database migrations after its first week. Folding them into one per table was easy to type and hard to get right. The order of foreign keys was the whole job - and a schema diff was the only proof I trusted.
art: /art/posts/rewrite-history.svg
---
Nibble had thirty-six database migrations after its first week. Most created a table. The rest added foreign keys,
recreated the search index with a new column, renamed the identity tables, and added a column to sessions — the ordinary
sediment of a project finding its shape.

Nobody was running Nibble yet except my own site, so there was no history worth keeping. Release 0.18.1 folded the
thirty-six into one migration per table, each creating its table exactly as it is today. It's a change that is easy to
type and easy to get subtly wrong, and the way I approached it is the way I approach any change to something that holds
data: decide what "the same" means, then prove it.

## Keep the identities

A Rails migration's timestamp is its version; it's what the database records once the migration has run. So I kept each
table's original timestamp on its folded migration. A database already on 0.18.0 has every one of those versions recorded,
finds nothing to run, and never notices the change. Only a database from before 0.18.0 has to be created afresh — and at
that point, the only one was mine.

That's the first principle of rewriting history: **the systems that already depend on it must not be able to tell**.

## The order is the whole job

Folding would have been trivial if each table's foreign keys could sit inside its own migration. They can't. The tables had
been created in an order that had nothing to do with which tables point at which: drafts, entries and sessions were all
created before users, and all of them point at users.

The rule I settled on: **a foreign key goes in whichever of its two tables' migrations runs later.** The keys pointing at
users live in the users migration, and by the time it runs, every table involved exists. Crucially, that works on any
database, not just SQLite — which happily forgives a key pointing at a table that doesn't exist yet. A rule that only
holds because one database is lenient isn't a rule; it's a coincidence waiting for a PostgreSQL user.

## Prove it, don't believe it

I didn't trust myself with this one, and that's the point of the exercise. The proof was mechanical:

1. Delete the schema file.
2. Build a database purely from the new migrations.
3. Dump its schema.
4. Diff it against the schema from before the change.

It matched — with exactly one difference, which turned out to be an improvement: two Active Storage foreign keys had been
declared twice, once by Rails and once by an old Nibble migration, and now they're declared once. Then the full CI run
built a brand-new site from the migrations and upgraded it, end to end.

## The sysadmin's version of the same habit

None of this is specific to migrations. It is the habit that years of administering servers teach — moving databases between
machines, migrating systems, changing anything that holds someone's data:

- **Define "the same" in a way a machine can check** — a schema dump, a checksum, a row count, a `diff` of the
  configuration that's actually loaded.
- **Compare against the real before**, not against what you remember it to be.
- **Explain every difference.** One unexplained line in a diff is a reason to stop, even when it turns out to be harmless.
- **Rehearse on a copy, then run it for real**, and keep the way back until the new state has earned your trust.

Tidy history is pleasant. Knowing the tidy version produces the same database is the part that lets you sleep.

The original write-up is [Thirty-six migrations, folded](https://nibble.ink/blog/thirty-six-migrations-folded) on the
Nibble blog.
