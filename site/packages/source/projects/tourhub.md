---
order: 8
title: TourHub
category: client
client: TourHub
role: Software & infrastructure engineer
tagline: "Building TourHub, the marketplace that connects touring and live-event crew with the shows that need them — verified profiles, contracts, and payment secured before anyone sets foot on stage."
description: "An ongoing engagement building TourHub, an Australian marketplace for live-events crew founded by touring audio veterans: verified crew profiles, a tier system earned on the road, contracts with payment secured through Stripe, and the environments that carry it all to production."
stage: building
kind: Live-events marketplace · Rails
year: "2026"
monogram: "T"
logo: logos/tourhub.svg
accent: "#00743F"
featured: false
cover: art/tourhub.svg
website: https://tourhub.io
stack: [Ruby on Rails, Inertia.js, Stripe, Progressive web app, Linux servers, Staging & production environments]
highlights:
  - Marketplace for live-events crew across 15 disciplines, from audio and lighting to logistics
  - Every profile reviewed before it appears in search
  - Payment secured through Stripe before the work starts, with disputes handled by the TourHub team
  - Installable app with push notifications
  - "Over 2,400 professionals on the waitlist ahead of launch"
seo:
  description: "TourHub: an Australian marketplace connecting touring and live-event crew with organisers, with verified profiles, contracts and Stripe-secured payments. Built with Ruby on Rails and Inertia."
---

## TourHub

TourHub was founded by touring audio veterans who were tired of the industry running on group chats, handshake deals
and unpaid invoices. Hiring a touring crew used to mean Facebook groups, personal networks and reputation by hearsay;
payment was a bank transfer with no protection; and excellent crew were invisible outside their own circle.

TourHub replaces that with one platform for crew and the teams that hire them, across Australia. It is preparing to
launch at [tourhub.io](https://tourhub.io), with more than 2,400 professionals already on the waitlist.

## What the platform does

- **Find exactly who a show needs.** Crew are searchable by discipline — tour and road management, production, stage
  management, audio, lighting, video, rigging, backline, wardrobe, logistics, merchandising and more — by gear
  proficiency, and by verified tier.
- **Reputation that is earned.** Crew climb from *Road Rookie* to *Road Legend* as they complete verified contracts,
  and every profile is reviewed by the TourHub team before it appears in search.
- **Paid before the show.** A hire becomes a contract, and the crew member's payment is secured through Stripe before
  they pack their kit. If something goes wrong, disputes are resolved by TourHub's team, not left to whoever chases
  hardest.
- **Built for the road.** It installs like an app and sends push notifications, because the people using it are
  rarely at a desk.

## The engagement

The work spans both halves of what I do. On the engineering side, that means building the product in **Ruby on
Rails** with **Inertia**: the marketplace, profiles and verification, contracts and Stripe payments. On the operations
side, it means the environments those features travel through: a staging environment that mirrors production closely
enough to be trusted, and a production platform people will rely on while they're on tour.

- **Staging that tells the truth.** A staging environment is only useful if it behaves like production — same
  configuration shape, same kind of data, same deploy process. Every change is reviewed there before it ships.
- **Money handled carefully.** Payments are the part of a marketplace that can't be approximately right. They get the
  most testing, the clearest records and the most conservative changes.
- **Small, frequent releases.** Small changes are easy to reason about, easy to verify and easy to roll back.

The specifics of client work stay with the client. If you're building a platform that needs both careful engineering and
a steady hand on its infrastructure, [let's talk](/about#contact).
