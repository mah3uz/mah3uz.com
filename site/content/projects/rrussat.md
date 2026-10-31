---
id: rrussat
order: 7
title: rrussat
tagline: A peer-to-peer, end-to-end encrypted messenger with a terminal client and a Flutter app — and no application server in the middle.
description: rrussat is a one-to-one messenger built in Rust on iroh and QUIC. Identities are keypairs, pairing is a QR code or a line of text, messages are protected with X3DH and a Double Ratchet, and history lives in a local SQLite file sealed under a passphrase. It is an exercise in applied cryptography and honest engineering, not an audited security product — and it says so.
category: product
stage: experiment
kind: Messenger · Terminal & app
year: "2026"
logo: /logos/rrussat.svg
monogram: "R"
accent: "#167A8E"
featured: false
cover: /art/rrussat.svg
repository: https://github.com/mah3uz/rrussat
stack: [Rust, iroh, QUIC, X3DH, Double Ratchet, SQLite, ratatui, Flutter]
highlights:
  - One Rust core behind two very different clients — a terminal UI and a Flutter app
  - X3DH handshake and Double Ratchet, with every key derivation labelled and every stored blob bound to its context
  - Direct, LAN or relayed — each contact shows which path is actually in use
  - 330 tests, mutation-checked so that security tests can actually fail
seo:
  description: "rrussat is a Rust peer-to-peer end-to-end encrypted messenger with a terminal client and a Flutter app, built on iroh, X3DH and the Double Ratchet."
---

## The question

How small can a private messenger be? rrussat is my working answer: no accounts, no application server, two people talking
to each other directly. *"No application server is involved."* Your identity is a keypair generated the first time you run
it, and you pair with someone by showing a QR code — or the same ticket as plain text, because *"a TUI has no camera."*

It is also a deliberate exercise in a discipline I value: being exact about what a system does and doesn't promise. The
README says plainly, *"This is a personal project, not an audited security tool."*

## Honest about "no server"

Peer-to-peer systems love to claim there is no server. rrussat doesn't: *"'No server' holds for message content, not for
NAT traversal."* Connections are made with iroh over QUIC, where the endpoint identifier *is* an Ed25519 public key, so
dialling by public key is built in. Peers are found three ways — mDNS on the local network, the Mainline DHT, and a relay as
the fallback. Relays never see plaintext, *"but they are still servers"*, so every contact shows which path is live:
`DIRECT`, `LAN`, `RELAYED` with its region, or `OFFLINE`, rather than papering over the difference.

The same honesty runs through the interface. A message stays *queued* until it has genuinely left the device — *"Claiming
'sent' optimistically would be a small lie exactly when the peer is unreachable."*

## The cryptography

Sessions begin with an X3DH handshake using a separate X25519 identity key, a signed prekey and an ephemeral key, and
continue with a Double Ratchet. Every derivation is HKDF-SHA256 with its own label; messages are sealed with
ChaCha20-Poly1305. Receipts, typing and presence travel *inside* the ciphertext, so the shape of a conversation doesn't leak
through frame types. Trade-offs are written down as decisions rather than left as gaps: there are no one-time prekeys,
because a serverless design has nowhere to publish them.

History is kept in a single SQLite file sealed with XChaCha20-Poly1305 under a key derived from your passphrase with
Argon2id. Every sealed value carries its context as associated data, so a blob moved to a different column won't decrypt.
And there is an invariant I would underline for anyone implementing a ratchet: the ratchet state is saved in the *same
transaction* as the message that advanced it, and decryption works on a copy, so *"one injected frame cannot desynchronise
a session."*

## Four bugs between "queued" and "delivered"

The very first day produced the most educational fix in the project. Four separate faults stood between a queued message
and a delivered one: there was no signal that the other side had accepted the session (fixed with a `Ready` frame, where
*"refusal is the absence of the frame"*); messages were dequeued before they were written; two peers dialling each other at
once could livelock (resolved by letting *"the connection dialled by the smaller endpoint id"* win); and a standoff where both
sides waited for the other to speak first. The underlying lesson is one every network engineer learns eventually: *a write
that succeeded locally only means the bytes are in a buffer.*

## Tests that test themselves

rrussat has 330 tests, and they are mutation-checked — deliberately breaking the code to make sure the tests notice. That
process found two security tests that *"were passing for the wrong reason"*, and the architecture notes keep the conclusion:
*"A security test that cannot fail is worse than no test."* Even the QR code is verified: the half-block characters drawn
in the terminal are rebuilt into an image and decoded, to prove the code a phone would scan is the code you meant.

## One core, two clients

The cryptography, networking and storage live in a core crate with no UI dependency. A terminal client built on ratatui and a
Flutter app for Linux and Android (with iOS and macOS built and verified) sit on top of it through a generated bridge. The
app adds what a phone needs — camera QR scanning, a keyring or biometric-gated key cache, notifications and a background
service — while the terminal client offers clipboard copy that works over SSH and tmux. Attachments and voice messages are
sealed once per file and fetched over a separate stream, resumable and authenticated by a digest that arrived through the
ratchet first.

rrussat is an experiment, licensed WTFPL, with no public distribution channel yet. Group chat, video and multi-device sync
are explicitly out of scope.
