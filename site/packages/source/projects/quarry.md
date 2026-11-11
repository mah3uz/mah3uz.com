---
order: 3
title: Quarry
tagline: A fast SQL client and full-screen TUI for PostgreSQL, MySQL, MariaDB and SQLite — one binary, the same keys everywhere.
description: Quarry is a native SQL client for the terminal, written in Rust. It pairs a REPL in the tradition of pgcli and mycli with a full-screen interface for exploring schemas, editing tables safely and reading query plans, and it is built on the assumption that one day you will be connected to production by mistake.
category: product
stage: shipped
kind: Database client · TUI
year: "2026"
logo: logos/quarry.svg
monogram: "Q"
accent: "#1388A6"
featured: true
cover: art/quarry.svg
website: https://quarry.asmechanics.com
repository: https://github.com/mah3uz/quarry
stack: [Rust, ratatui, tokio-postgres, mysql_async, rusqlite, rustls, reedline]
highlights:
  - PostgreSQL, MySQL, MariaDB and SQLite from one binary, with psql's \d commands translated for each
  - Streaming a million rows to TSV uses about 11 MB of memory instead of 275 MB
  - Read-only mode enforced twice — by the server and by Quarry
  - 349 tests, including drivers run against real database servers
  - Released through Homebrew and the AUR
seo:
  description: "Quarry is a fast Rust SQL client and TUI for PostgreSQL, MySQL, MariaDB and SQLite, with safety rails for production and an LLM that never runs SQL."
---

## One tool for the databases I actually use

On any given day I touch PostgreSQL, MySQL or MariaDB, and SQLite — sometimes all three — across laptops, staging boxes
and production servers I reach through an SSH jump host. Each has its own client with its own habits, and the good
graphical tools are heavy, need a desktop, and don't follow you into an SSH session. Quarry is the tool I wanted
instead: *"One tool, three databases. The same keys, commands and output formats everywhere."*

It ships as a single native binary with two faces. There is a REPL in the tradition of `pgcli`, `mycli` and `litecli`,
with psql's `\d` family translated to each database's catalogue. And there is a full-screen TUI: a schema explorer,
tabbed editors, a virtualised results grid, a table browser with staged edits, structure and DDL views, an explain-plan
viewer and a command palette. `\tui` switches from one to the other without dropping the connection. TLS is built in,
SQLite is bundled, SSH tunnels use the system's own `ssh` — *"Nothing else to install."*

## Designed for the day you connect to production by mistake

The safety guide opens with the assumption that shaped the whole tool: *"quarry assumes you'll one day be connected to
production by mistake, and tries to make that survivable."* After many years of operating databases for other people,
I don't think that assumption is pessimistic; I think it is the job.

- **Destructive statements ask first.** `DROP`, `TRUNCATE`, `SHUTDOWN`, and `UPDATE` or `DELETE` without a `WHERE`
  clause require confirmation — including when they hide inside a CTE or an `EXPLAIN ANALYZE`.
- **Read-only means read-only, twice.** `--readonly` is enforced by the server (a read-only session on PostgreSQL and
  MySQL, `query_only` on SQLite) *and* checked by Quarry statement by statement.
- **Cancel really cancels.** Ctrl-C stops the query on the server, not just the display.
- **Secrets stay out of history.** Statements that look like they contain credentials are never recorded, saved
  connections never store passwords, and every file Quarry writes is readable only by you.
- **Edits are staged.** The table browser shows your changes as SQL and applies them in one transaction, or not at all.

## Streaming, and the one place it can't

Machine-readable output formats — CSV, TSV, JSON, JSON Lines and the rest of the seventeen — stream: rows arrive from the
server in batches of 256 with a time-based flush, and on PostgreSQL the query is cancelled the moment nobody is reading,
so `quarry … | head` stops the query instead of finishing it. Version 0.2.0 measured the difference: streaming a million
rows to TSV went from about 275 MB of memory to about 11 MB. The docs are honest about the exception: *"The table formats
need the whole result first, to size their columns."* Some trade-offs you can't engineer away; you can only document them
and choose well.

In the TUI the same thinking applies to the screen. The results grid is virtualised — it formats only the cells you can
see and sizes columns from a sample — and each connection keeps a second session for the explorer, *"so the explorer keeps
working while a long query runs."*

## An LLM feature designed for distrust

Quarry can write SQL from a question in plain language with `\llm`, but it was designed by someone who reviews other
people's SQL for a living. The model *"writes SQL for your schema and leaves it for you to review. It never runs anything
by itself."* Only the question and the schema are sent — table and column names, types, keys — capped in size; *"No rows
are ever sent."* It can use the Anthropic API, any OpenAI-compatible server including local models through Ollama or LM
Studio, or the Claude Code and Codex command-line tools, which it runs without tools from a temporary folder so they
don't pick up a project's instruction files. API keys are stored apart from the configuration and tied to the server they
belong to, and a generic `OPENAI_API_KEY` is deliberately ignored so a key can never be sent to the wrong server.

## The craft in the details

- A context-aware completer that understands aliases, schema qualifiers, CTEs and derived tables, suggests joins from
  foreign keys and expands `SELECT *`.
- A SQL formatter that is idempotent: format twice, get the same result.
- Vim editing with motions, counts, operators and text objects; rebindable keys with collisions resolved and reported.
- Twenty-seven built-in colour themes, base16 and base24 import, and icons that pick Nerd Font, Unicode or ASCII
  depending on what your terminal can show.
- Configuration saved by editing the TOML in place, so your comments survive.

## Tested against real servers

Quarry has 349 tests. The driver tests run against real PostgreSQL and MySQL servers in throwaway databases; the SSH
tunnel's success path is tested against a disposable `sshd`. Performance is tested too, in release mode: a hundred
thousand rows rendered as a coloured table in under a second, a 10,000-line editor buffer drawn in under two
milliseconds per frame, and a catalogue of three thousand tables loaded in under 200 ms.

Releases are cut by a single `just ship` that refuses to half-ship: it checks the version, the changelog, a clean and
current `main`, and access to GitHub, the AUR, the Homebrew tap and the docs host *before* doing anything public — then
asks once, because *"Everything after this is public and can't be taken back."* Quarry is MIT licensed and available
through Homebrew (`mah3uz/tap/quarry`), the AUR (`quarry-sql` and `quarry-sql-bin`), and as a Linux tarball.
