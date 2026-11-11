---
title: Release scripts that refuse to half-ship
published_at: 2026-10-20T09:00:00+06:00
topics: [operations, engineering]
excerpt: "The worst release is the one that stops halfway — a tag pushed, a package published, the documentation still describing last week. Every project I ship uses the same pattern to make that impossible: check everything, ask once, then do it all."
art: /art/posts/release-scripts.svg
---
I have cleaned up after a lot of half-finished releases over the years. A tag pushed but no build attached. A package
published to one repository and not the other. A database migrated but the application not deployed. Documentation
describing a version that never quite shipped. Each is small; each costs an evening; and each happened because a release was
a sequence of manual steps, and somewhere in the middle one of them failed.

Every project I ship now uses the same pattern to make that impossible. It is simple enough to describe in one sentence:
**check everything that could fail, ask once, and then do everything.**

## Phase one: preconditions

Before a release script does anything visible, it verifies every condition it will later depend on. Quarry's `just ship`, for
example, checks that:

- the version is well-formed and newer than the last tag;
- the changelog has a non-empty *Unreleased* section, so the release has notes;
- the working tree is clean and `main` is up to date with the remote;
- the GitHub CLI is authenticated;
- SSH access to the Arch User Repository works;
- the Homebrew tap repository exists;
- the documentation host is logged in.

Only then does it run the linter and the full test suite on a fresh build. The principle is the same as a pre-flight
checklist: discover the missing credential *before* you've published half the release, not after.

## Phase two: one question

Once every check passes, the script bumps the version and asks a single question. Quarry's is worded deliberately: *"Everything
after this is public and can't be taken back."* One confirmation, at the only point where it's meaningful, is far more effective
than a dozen prompts people learn to dismiss.

## Phase three: everything, in a safe order

After the confirmation, the script does it all: tags the release, uploads the build, creates the GitHub release with the
changelog section as its notes, publishes both Arch packages — from source and prebuilt — through throwaway clones, pushes a
branch that triggers the Homebrew build and *waits* for that workflow to finish, and deploys the documentation.

Order matters. Sysman's release workflow marks a release as "latest" only after every artefact is uploaded, because its
installer script downloads from the latest release; mark it too early and, for a few minutes, the installer points at a release
with missing files.

## The changelog is part of the release

Every one of these scripts refuses to run with an empty changelog, and that is a feature. My changelogs follow one rule, borrowed
from years of reading other people's: write for the person running the software, *"not for someone reading the diff."* What
changed, what they need to do, and what to watch for. User-visible changes are recorded under *Unreleased* in the same commit as
the change, so the notes are written while the context is fresh rather than reconstructed at release time.

Nibble carries the same idea into upgrades: a release that would change how a site behaves arrives switched off, and the site
opts in after reading the entry. Upgrading alone never changes what visitors see.

## Gates across repositories

The pattern extends beyond a single project. Nibble and its command-line tool are released separately, and people run whichever
versions they installed. A server release that silently broke existing clients would be invisible until users found it. So the
CLI has a contract test that boots a real Nibble site and drives the real binary against it — and **Nibble's** release script runs
it before it will tag. A release that would break the CLI people already have is caught before it exists.

## Why it's worth it

A release script like this takes an afternoon to write and saves that afternoon on the first release that would have failed
halfway. More importantly, it changes how releasing feels. When the script checks everything and refuses to half-ship, releasing
becomes routine — and routine releases are small, frequent releases, which are the safest kind there is.

After seventeen years, my rule is simple: if a release takes more than one command and one confirmation, it's not finished being
automated.
