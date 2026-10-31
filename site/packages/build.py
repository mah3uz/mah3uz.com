"""Writes site/packages/default — the content this site starts from — as a Nibble content package.

Run it after editing the copy below, then import the package:

    python3 site/packages/build.py
    bin/rails nibble:content:import site/packages/default            # a fresh database
    bin/rails nibble:content:import site/packages/default --mode=update   # overwrite what's there

Pages and posts are edited in the Control Plane afterwards; this file is only the seed. Post bodies are written in a
small Markdown subset (## headings, paragraphs, - lists, ``` code, > quotes, **bold**, `code`, [links](url)) and
converted to the rich-text JSON Nibble stores.
"""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).parent / 'default'


# --------------------------------------------------------------------------- rich text

def inline(text):
    nodes = []
    pattern = re.compile(r'(\*\*(.+?)\*\*|`(.+?)`|\[(.+?)\]\((.+?)\)|\*(.+?)\*)')
    pos = 0
    for match in pattern.finditer(text):
        if match.start() > pos:
            nodes.append({'type': 'text', 'text': text[pos:match.start()]})
        if match.group(2):
            nodes.append({'type': 'text', 'text': match.group(2), 'marks': [{'type': 'bold'}]})
        elif match.group(3):
            nodes.append({'type': 'text', 'text': match.group(3), 'marks': [{'type': 'code'}]})
        elif match.group(4):
            nodes.append({'type': 'text', 'text': match.group(4), 'marks': [{'type': 'link', 'attrs': {'href': match.group(5)}}]})
        elif match.group(6):
            nodes.append({'type': 'text', 'text': match.group(6), 'marks': [{'type': 'italic'}]})
        pos = match.end()
    if pos < len(text):
        nodes.append({'type': 'text', 'text': text[pos:]})
    return nodes


def rich(markdown):
    doc = []
    blocks = re.split(r'\n\s*\n', markdown.strip())
    for block in blocks:
        block = block.strip('\n')
        if block.startswith('```'):
            lines = block.split('\n')
            language = lines[0][3:].strip() or None
            code = '\n'.join(lines[1:-1])
            doc.append({'type': 'codeBlock', 'attrs': {'language': language}, 'content': [{'type': 'text', 'text': code}]})
        elif block.startswith('## '):
            doc.append({'type': 'heading', 'attrs': {'level': 2}, 'content': inline(block[3:])})
        elif block.startswith('### '):
            doc.append({'type': 'heading', 'attrs': {'level': 3}, 'content': inline(block[4:])})
        elif block.startswith('> '):
            text = ' '.join(line[2:] for line in block.split('\n'))
            doc.append({'type': 'blockquote', 'content': [{'type': 'paragraph', 'content': inline(text)}]})
        elif block.startswith('- '):
            items = [line[2:] for line in block.split('\n')]
            doc.append({'type': 'bulletList', 'content': [
                {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': inline(item)}]} for item in items
            ]})
        else:
            doc.append({'type': 'paragraph', 'content': inline(' '.join(block.split('\n')))})
    return doc


def write(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120))


# Long-standing Unsplash photos, hot-linked as Unsplash asks. Each sits over generated art, so a page still looks
# finished if one ever fails to load.
def unsplash(photo):
    return f'https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1800&q=80'


CREDIT = 'Photo: Unsplash'

# --------------------------------------------------------------------------- globals

write('globals/site/en.yml', {
    'name': 'mah3uz',
    'tagline': 'Software engineer since 2009 — building products, developer tools and software for the Linux desktop.',
    'social_links': [
        {'label': 'GitHub', 'url': 'https://github.com/mah3uz'},
        {'label': 'Nibble', 'url': 'https://nibble.ink'},
        {'label': 'Darwan', 'url': 'https://darwan.dev'},
    ],
    'favicon': 'brand/favicon.svg',
})
write('globals/seo/en.yml', {
    'title_template': '{title} · {site_name}',
    'default_description': 'Mahfuz (mah3uz) — software engineer since 2009, building Nibble, Quarry, Sysman, Darwan and '
                           'Insensical: products, developer tools and Linux desktop software.',
    'organization_name': 'mah3uz',
    'default_share_image': 'brand/social-card.png',
    'organization_logo': 'brand/favicon.svg',
})

# The files themselves sit in assets/brand/ beside this list; the import uploads them once.
write('assets.yml', [
    {'path': 'brand/favicon.svg', 'title': 'mah3uz mark', 'alt': 'The mah3uz mark: a teal tile with a peeled corner'},
    {'path': 'brand/social-card.png', 'title': 'Social card',
     'alt': 'mah3uz — products, dev tools and Linux desktop software. Software engineer since 2009.'},
])

# --------------------------------------------------------------------------- navigation

write('navigation/main/en.yml', {'tree': [
    {'url': '/projects', 'title': 'Work'},
    {'entry': 'pages/now', 'title': 'Now'},
    {'entry': 'pages/blog', 'title': 'Writing'},
    {'entry': 'pages/uses', 'title': 'Uses'},
    {'entry': 'pages/about', 'title': 'About'},
]})

# --------------------------------------------------------------------------- pages

write('collections/pages/en/home.yml', {
    'title': 'I build calm, fast software for the web and the Linux desktop.',
    'template': 'home',
    'eyebrow': 'Software engineer · since 2009',
    'intro': "I'm Mahfuz. I've been designing, building and shipping software professionally since 2009. Today I build "
             'my own products: Nibble, a CMS you run as your own app; fast Rust tools for the terminal; and apps and '
             'themes for the Linux desktop.',
    'cards': [
        {'title': 'Own the stack', 'text': 'Software you can run, read and move. I favour tools that leave you in charge of your data and your server.'},
        {'title': 'Fast is a feature', 'text': 'Instant start-up, no spinners, no surprises. Speed is how software shows respect for the people using it.'},
        {'title': 'Keyboard first', 'text': 'Everything I build can be driven without a mouse, including this site. Press / and see.'},
        {'title': 'Ship, then sharpen', 'text': 'Put real work in front of real people early, then keep polishing the parts they actually touch.'},
    ],
    'seo': {'title': 'mah3uz — software engineer building products, dev tools and Linux apps', 'exact_title': True},
})

write('collections/pages/en/about.yml', {
    'title': 'Engineer, product builder, and still a tinkerer.',
    'template': 'about',
    'eyebrow': 'About',
    'intro': "I've been building software professionally since 2009. These days I make products of my own, with the same "
             'care I used to give other people’s roadmaps.',
    'content': '''I'm **Mahfuz**, known online as **mah3uz**. My career has run alongside the web itself: from server-rendered pages and jQuery to single-page apps, from shared hosting to containers, and back again to simple, fast, server-rendered software. Along the way I've learned to tell what lasts from what's fashionable.

Today my time goes into my own products. [Nibble](/projects/nibble) is a content management system you run as your own Rails application. [Quarry](/projects/quarry) and [Sysman](/projects/sysman) are Rust tools for people who live in a terminal or on a Linux desktop. [Darwan](/projects/darwan) themes the two screens every Linux user sees each day, and [Insensical](/projects/insensical) rethinks the terminal multiplexer for the age of coding agents.

## What I do

- **Product engineering** — taking an idea from a sketch to something people pay for and rely on.
- **Platforms and content systems** — schemas, editorial workflows, caching, search and deployment.
- **Developer tools** — CLIs and TUIs that start instantly and stay out of the way.
- **Linux desktop software** — native apps and themes in Rust, QML and Qt.

## Working together

I take on a small amount of work alongside my products: architecture reviews, a hand on a hard part of a product, or building something end to end. If that sounds useful, [write to me](#contact).''',
    'cards': [
        {'title': 'Boring technology, beautiful results', 'text': 'Proven foundations — Rails, SQLite, PostgreSQL, plain HTML — leave room to spend the novelty budget where users can feel it.'},
        {'title': 'Small, sharp tools', 'text': 'One thing, done well and fast. I would rather ship three focused tools than one that tries to do everything.'},
        {'title': 'Data that stays yours', 'text': 'Self-hostable, exportable, readable. Software should never hold the things you made hostage.'},
        {'title': 'Craft is in the details', 'text': 'Keyboard paths, empty states, error messages and dark mode are not polish. They are the product.'},
    ],
    'photo': unsplash('photo-1517694712202-14dd9538aa97'),
    'photo_credit': CREDIT,
    'seo': {'title': 'About'},
})

write('collections/pages/en/now.yml', {
    'title': "What I'm focused on now",
    'template': 'now',
    'eyebrow': 'Now',
    'intro': 'A snapshot of where my attention is this season — what I am building, shipping and learning.',
    'content': '''## Building

Most of my days go into **Nibble**. The aim is a CMS that feels like your own application, because it is: schema in YAML, themes in Vue, content in SQLite, deployed with Kamal to a server you control. Alongside it, the **Nibble CLI** makes starting a site and editing a live site's content as natural as using git.

## Shipping

**Darwan** keeps growing its collection of hand-crafted themes for SDDM and Quickshell, and **Quarry** keeps getting faster at the everyday work of reading and querying databases. **Insensical** is heading towards a multiplexer that treats long-running agent sessions as first-class.

## Learning

**Sysman** is my excuse to go deep on GPUI and native rendering in Rust, and **rrussat** is a hands-on course in peer-to-peer networking and applied cryptography.

## Not doing

Saying yes to new long-term commitments. I keep a little room for short, focused collaborations — [get in touch](/about#contact) if you have one in mind.''',
    'cards': [
        {'title': 'Primary focus', 'text': 'Nibble and its CLI — making a self-hosted CMS feel effortless.'},
        {'title': 'On the side', 'text': 'Darwan themes, Quarry polish and Insensical sessions.'},
        {'title': 'Exploring', 'text': 'GPUI for native Linux apps, and P2P encryption in Rust.'},
    ],
    'seo': {'title': 'Now'},
})

write('collections/pages/en/uses.yml', {
    'title': 'The tools I use every day',
    'template': 'uses',
    'eyebrow': 'Uses',
    'intro': 'The software behind my work. Several of these I built because I wanted them to exist.',
    'content': '''## Desktop

- **Arch Linux** — a rolling base I understand completely.
- **Hyprland** — a tiling Wayland compositor that stays out of the way.
- **Darwan** — my own themes for the login and lock screens.
- **Walker** — a fast, keyboard-driven application launcher.

## Terminal and editor

- **Neovim** — my editor for almost everything.
- **Insensical** — my own multiplexer, built for long agent sessions.
- **Ghostty** — a fast, native terminal emulator.
- **Quarry** — my SQL client for PostgreSQL, MySQL and SQLite.

## Languages

- **Rust** — for tools and desktop apps that must be fast and dependable.
- **Ruby** — for products, and the joy of Rails.
- **TypeScript** — for the browser, typed end to end.
- **QML** — for Qt interfaces on the Linux desktop.

## Frameworks

- **Ruby on Rails 8** — the backbone of Nibble.
- **Vue 3 and Inertia** — server-rendered pages that behave like an app.
- **Tailwind CSS** — design tokens in code, as this site shows.
- **GPUI** — GPU-accelerated native UI in Rust, used by Sysman.

## Data and shipping

- **SQLite** — for far more than people expect; this site runs on it.
- **PostgreSQL** — when many writers need one database.
- **Kamal** — zero-downtime deploys to a plain server.
- **Homebrew** — how Quarry and Insensical reach people.''',
    'photo': unsplash('photo-1555066931-4365d14bab8c'),
    'photo_credit': CREDIT,
    'seo': {'title': 'Uses'},
})

write('collections/pages/en/blog.yml', {
    'title': 'Notes from the workshop',
    'template': 'posts/index',
    'eyebrow': 'Writing',
    'intro': 'Engineering notes on building products, developer tools and Linux desktop software — newest first.',
    'seo': {'title': 'Writing'},
})

write('collections/pages/en/search.yml', {
    'title': 'Search',
    'template': 'search',
    'eyebrow': 'Find anything',
})

# --------------------------------------------------------------------------- topics

TOPICS = {
    'engineering': ('Engineering', 'Architecture, trade-offs and the decisions behind the software.'),
    'rust': ('Rust', 'Building fast, dependable tools and desktop apps in Rust.'),
    'product': ('Product', 'Turning ideas into things people rely on.'),
    'linux': ('Linux', 'The Linux desktop, and making it a little nicer.'),
}
for slug, (title, description) in TOPICS.items():
    write(f'taxonomies/topics/en/{slug}.yml', {'title': title, 'description': description})

# --------------------------------------------------------------------------- posts

POSTS = [
    {
        'slug': 'why-this-site-runs-on-a-cms-i-built',
        'title': 'Why this site runs on a CMS I built',
        'published_at': '2026-10-28T09:00:00Z',
        'topics': ['topics/product', 'topics/engineering'],
        'excerpt': 'Every developer eventually builds a CMS. Here is why I did it on purpose, and what Nibble does differently.',
        'photo': unsplash('photo-1498050108023-c5249f4df085'),
        'art': '/art/nibble.svg',
        'body': '''Every developer eventually writes their own CMS. Most of us do it by accident: a blog engine that grows an admin, then a media library, then a plugin system. I did it on purpose, because I kept wanting the same thing and couldn't find it.

## What I wanted

I wanted a CMS that was **an application I own**, not a service I rent. Something I could read, change and deploy like any other codebase, with a database I can copy with one command, and an upgrade path that never touches my code.

- Content described in **files I can review** — schema as YAML, in the repository.
- **Server-rendered pages** that behave like an app once loaded.
- One database, **SQLite**, for content, cache and jobs.
- A theme that is just **Vue components**, not a templating language of its own.

## How Nibble draws the line

Nibble installs into `vendor/nibble`, and everything else is the site's: the schema, the content, the theme, the deploy configuration. An upgrade replaces that one folder and nothing else. That single rule is what makes it feel like your app rather than someone else's product.

> A theme never ships content. A site never edits the CMS. Everything else follows from those two lines.

## What you're looking at

This site is a Nibble site. The projects are a folder of Markdown files reviewed like code, while this post was written in the Control Plane. The theme, *Neat*, takes its colours from a pair of banners, and every page is rendered on the server and cached against exactly the records it read.

Building your own CMS is usually a warning sign. Building one you would happily hand to someone else is a different project entirely, and that's the one I'm working on.''',
    },
    {
        'slug': 'sqlite-is-enough',
        'title': 'SQLite is enough (for most of us)',
        'published_at': '2026-10-12T09:00:00Z',
        'topics': ['topics/engineering'],
        'excerpt': 'One file, no server, and more than enough for most products. Why my projects start on SQLite — and when they shouldn’t.',
        'photo': unsplash('photo-1558494949-ef010cbdcc31'),
        'art': '/art/quarry.svg',
        'body': '''For years the default answer to "which database?" was a server: PostgreSQL or MySQL, running somewhere, with its own backups, users and upgrades. For most of what I build now, the answer is a file.

## Why SQLite

SQLite runs in the same process as your application. There is no network between your code and your data, which means queries that would be "fast" over a socket are effectively instant. With **WAL mode**, readers don't block the writer, and a single server comfortably handles far more traffic than most products will ever see.

- **Operations disappear.** No database server to patch, tune or keep alive.
- **Backups are a copy.** `VACUUM INTO` writes a consistent snapshot while the site keeps running.
- **Development matches production.** The same engine, the same file format, everywhere.

## Where it stops

SQLite allows one writer at a time. If many processes on many machines must write to the same data constantly, use PostgreSQL — that is exactly what it is for. That's why [Quarry](/projects/quarry) speaks both: I use the right one for the job, and I want one tool for both.

## The rule I use

Start on SQLite. Keep your SQL portable. Move when the numbers tell you to, not when a diagram does. Most products never need to move at all.''',
    },
    {
        'slug': 'native-linux-apps-in-rust-with-gpui',
        'title': 'Native Linux apps in Rust with GPUI',
        'published_at': '2026-09-20T09:00:00Z',
        'topics': ['topics/rust', 'topics/linux'],
        'excerpt': 'Notes from building Sysman on GPUI, the GPU-accelerated UI framework behind the Zed editor.',
        'photo': unsplash('photo-1461749280684-dccba630e2f6'),
        'art': '/art/sysman.svg',
        'body': '''When I started [Sysman](/projects/sysman), a system monitor that remembers history, I wanted the app to feel instant even when scrubbing through hours of samples. That ruled out a web view. It led me to **GPUI**, the UI framework the Zed team built for their editor.

## Why GPUI

GPUI renders on the GPU and is written in Rust from top to bottom. Layout, text and drawing happen in the same language as the rest of the application, so there is no bridge to cross and no second runtime to ship.

- **Rendering on the GPU** keeps dense charts smooth.
- **One language** for the collector, the storage and the interface.
- **Ownership rules** make state changes explicit, which is exactly what a live dashboard needs.

## Splitting the work

Sysman is two programs. A small **collector daemon** samples the system and stores history; the **app** reads that history and draws it. Keeping them apart means the collector stays tiny and always-on, while the app can be as rich as it likes and only runs when you open it.

## What I'd tell someone starting out

GPUI is young and moving quickly, so read the source as much as the docs — Zed itself is the best example application. Start with one view, get the data flowing, and only then make it pretty. The speed you get for free is remarkable.''',
    },
]

for post in POSTS:
    write(f"collections/posts/en/{post['slug']}.yml", {
        'title': post['title'],
        'published_at': post['published_at'],
        'topics': post['topics'],
        'excerpt': post['excerpt'],
        'photo': post['photo'],
        'photo_credit': CREDIT,
        'art': post['art'],
        'body': rich(post['body']),
    })

print(f'wrote {sum(1 for _ in ROOT.rglob("*.yml"))} files to {ROOT}')
