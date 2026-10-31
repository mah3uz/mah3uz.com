---
id: nibble-cli
order: 2
title: Nibble CLI
tagline: Create a site, run its tasks, and edit any Nibble site's content from your terminal.
description: The command-line companion to Nibble, written in Rust. It creates new sites, runs a site's tasks, and works on the content of any Nibble site you sign in to — as you, and never as more than you.
stage: building
kind: Command-line tool
year: "2026"
monogram: "›_"
accent: "#1388A6"
featured: false
cover: /art/nibble-cli.svg
website: https://nibble.ink
repository: https://github.com/mah3uz/nibble-cli
stack: [Rust, CLI, OAuth, Nibble]
highlights:
  - "`nibble new` sets up a complete site, ready to deploy"
  - Signs in to any Nibble site and works on its content remotely
  - Acts with your permissions, never more
  - A single fast binary
seo:
  description: "The command-line companion to Nibble, written in Rust. It creates new sites, runs a site's tasks, and works on the content of any Nibble site you sign in…"
---

## The idea

A CMS lives in a browser, but the people who build sites live in a terminal. Nibble CLI is the bridge: one binary
that starts a new site, runs the tasks a site needs, and lets you work on the content of any Nibble site you can sign
in to — locally or in production.

## As you, never more than you

The CLI signs in the way a person does and acts with that person's permissions. It can't do anything the account
behind it couldn't do in the Control Plane, which makes it safe to hand to scripts, CI jobs and AI agents alike.

## Why Rust

It starts instantly, ships as a single file, and has no runtime to install. For a tool you reach for dozens of times a
day, that matters.
