---
title: Letting AI agents near production, carefully
published_at: 2026-10-27T09:00:00+06:00
topics: [security, engineering]
excerpt: AI agents are becoming colleagues with keyboards. After years of managing who can do what on servers, I've applied the same principles to them — least privilege, explicit actors, approvals and honest boundaries — across four tools I build.
art: /art/posts/ai-agents.svg
---
For most of my career, access control was about people and services: which user can log in to which server, which service
account can read which database, which deploy key can push to which repository. The principles are old and well tested —
least privilege, explicit identity, separation of duties, and an audit trail you can actually read.

AI agents are a new kind of actor in that picture. They write code, edit content, run commands and query databases, often
faster than a person can review. I build several tools that agents use, and in each of them I have tried to apply the same
principles I would apply to a new member of an operations team. Here is what that looks like in practice.

## Principle one: an agent acts as someone

The most dangerous design is an agent with its own, broad credentials — a superuser with good intentions. In Nibble, my CMS,
an AI application connects over MCP with OAuth, signed in *as a person*, and its permission is the **intersection** of three
things: what that person may do, what the app was granted, and what the site allows agents to do at all. It can never exceed
the person who connected it.

Underneath, every change from any source passes through one lifecycle that requires an explicit actor. There is no default,
*"so no caller can forget who is acting."* That single rule does more for auditability than any logging feature: every
change has an answer to "who did this?"

The command-line tool follows the same rule: it works *"as you and never as more than you."* Its sign-in requires PKCE,
stores tokens in the operating system's keychain, and refuses to follow a project folder's configuration to a site you
haven't explicitly allowed — so cloning a repository can't redirect your credentials.

## Principle two: separate proposing from doing

Change management exists because the person who proposes a change shouldn't be the only one who approves it. Agents make
that more important, not less.

- In **Nibble**, changes to live content can be held for approval. Approving one carries it out — and re-checks permissions at
  that moment, because the situation may have changed since the agent proposed it. Entry changes made through the CLI are
  drafts until someone allowed to publish does.
- In **Quarry**, my SQL client, the language-model feature *"writes SQL for your schema and leaves it for you to review. It
  never runs anything by itself."* A database is exactly the place where a confident, wrong statement does real damage.

## Principle three: send the minimum

Every byte you send to a model is a byte you've disclosed. Quarry sends the question and the *schema* — table and column
names, types, keys — and nothing else: *"No rows are ever sent."* The schema is capped in size. API keys are stored apart from
the configuration and tied to the server they belong to, and a generic `OPENAI_API_KEY` in the environment is deliberately
ignored, so a key can never be sent to a server it wasn't meant for. When Quarry uses a local coding agent's command-line tool
instead of an API, it runs it with no tools, from an empty temporary folder, so a project's instruction files can't leak into
the request.

## Principle four: narrow defaults, deliberate expansion

Nibble's agent access starts narrow — reading, and drafting entries — and anything more is a deliberate choice by an
administrator. Some convenient options are simply off by default: device-code sign-in, for example, because codes can be
phished. The list of operations an agent can perform is generated from one registry and guarded by a snapshot test, so
widening what agents can do is always a visible, reviewed change rather than a side effect.

## Principle five: be honest about boundaries

Security documentation has a habit of implying guarantees it can't keep. I try to do the opposite.

Insensical, my terminal multiplexer, lets agents start and supervise other agents — within limits of eight at once and two
levels deep — and lets you protect a pane so agents can't drive it. Its manual is blunt about that protection: *"It isn't a
wall."* And about the tool itself: *"Letting an agent run `isc` lets it do anything you can."* That honesty is a security
feature. People make good decisions when they know exactly what a control does and doesn't do.

## Principle six: know when you're needed

Supervision only works if you notice when it's needed. Insensical works out the state of every terminal pane — running,
waiting, done, failed — from the strongest evidence available: an explicit report from the program, terminal signals such as
notifications and password prompts, or the command finishing. When five agents are running, it shows you which one is waiting
on you, without reshuffling your layout. An approval queue nobody looks at is not a control.

## The same old principles

None of this is new. It is the access-control thinking that keeps servers safe, applied to a new kind of user: act as a known
identity, never exceed the person responsible, separate proposing from doing, disclose the minimum, start narrow, and tell the
truth about your boundaries. Agents are genuinely useful colleagues. Like any new colleague with production access, they should
earn wider permissions — and the systems they touch should make that the easy path.
