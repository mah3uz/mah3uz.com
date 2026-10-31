---
id: nibble
order: 1
title: Nibble
tagline: A schema-driven CMS you run as your own application.
description: Nibble is a content management system that ships as a Rails 8 application you own. You describe your content in YAML, and editors get a fast Control Plane; visitors get server-rendered pages from SQLite.
stage: building
kind: Content management system
year: "2026"
logo: /logos/nibble.svg
monogram: "n"
accent: "#21BDB0"
featured: true
banner: /banners/nibble.svg
cover: /art/nibble.svg
website: https://nibble.ink
repository: https://github.com/mah3uz/nibble
stack: [Ruby on Rails, Vue 3, Inertia, TypeScript, SQLite, Tailwind CSS, Kamal]
highlights:
  - Content modelled in YAML, read in three layers — Nibble's, the theme's, then the site's
  - Server-side rendering with Vue 3 and Inertia, hydrated in the browser
  - Drafts, revisions, scheduling, workflow and trash built in
  - Agents get the same permissions as the person they act for, through MCP and a management API
seo:
  description: "Nibble is a content management system that ships as a Rails 8 application you own. You describe your content in YAML, and editors get a fast Control…"
---

## Why it exists

Most content management systems ask you to choose: a hosted platform you don't control, or a framework you have to
assemble yourself. Nibble sits in between. It is a whole Rails application, installed into your own repository, that
you deploy with Kamal to a server you own. Upgrading replaces one folder, `vendor/nibble`, and never touches the code
that is yours.

## How it works

Content is **schema-driven**. Collections, taxonomies, blueprints, globals, navigation and forms are declared in YAML,
and every entry is validated against its blueprint before it is saved. A request is resolved to an entry, its view's
query sidecar runs, and the page is rendered on the server with Vue, then cached against exactly the records it read,
so publishing a change clears only the pages that used it.

- **One database.** SQLite in WAL mode holds the content, the cache and the job queue, with nightly snapshots.
- **Themes are Vue.** A theme is layouts, views and components, plus the schema it needs. It never ships content.
- **Content as files.** A folder of Markdown can be a collection too, reviewed in pull requests like code.
- **Built for agents.** An AI agent gets an app grant, and every change still goes through one permission check.

## This site

You're looking at it. mah3uz.com runs on Nibble with its own theme, *Neat*: the projects on this page are a folder of
Markdown files, and the writing is edited in the Control Plane.
