# mah3uz

This file is yours. Nibble generated it once and will never write it again, so put whatever you want an agent
to know about this site here: its conventions, what you are building, anything you would otherwise have to
repeat. Claude Code reads it through CLAUDE.md; Codex, Cursor and most other agents read it directly.

## How this site works

Read [vendor/nibble/NIBBLE-ARCHITECTURE.md](vendor/nibble/NIBBLE-ARCHITECTURE.md) first. That file is Nibble's, it arrives with every release, and it
describes the CMS underneath this site: where its code lives, how a request becomes a page, what is yours to
change and what belongs to Nibble.

The short version: everything under `vendor/nibble/` is Nibble's and an upgrade replaces it. `app/`, `site/` (schema,
content, your theme and Control Plane overrides), `config/nibble.yml`, `config/deploy*.yml`, `Dockerfile`,
`db/migrate` and this file are yours.

## Tools for agents

In development, `bin/rails nibble:dev:mcp` serves tools an agent can call: render a page and see its props and the
files that answered it, check the schema, run the tests, read the development log, and search Nibble's docs for the
installed version. `bin/rails nibble:dev:setup` asks which of Claude Code, Codex and Cursor to set up, writes only into this folder, and
stops Claude Code editing `vendor/nibble/`.

## Conventions

<!-- Yours to fill in. Some things worth writing down: how you name things, what you want tested, which
     decisions are settled so nobody reopens them. -->
- **Theme:** `site/themes/neat` — colours come from the two brand banners (dark `#0A1A20 → #0D2A31` with a teal glow,
  light `#F3FCFA → #DDF4F0` with a mint glow, ink `#043040`, accents `#62EDD4 / #21BDB0 / #1388A6`). Tokens live as
  `--neat-*` variables in `styles/theme.css` and are exposed to Tailwind as `canvas`, `surface`, `ink`, `muted`,
  `faint`, `line`, `accent`. Use those, never raw greys, so both registers keep working.
- **Motifs:** three viewfinder corners (`Corners.vue`) and a peeled bottom-right corner (`Peel.vue`). Motion is CSS
  (`animate-rise`, `animate-drift`…) plus the `v-reveal`, `v-spotlight` and `v-tilt` directives in `lib/motion.ts`;
  all of it respects `prefers-reduced-motion`. Browser-only code goes in `onMounted` — server rendering has no window.
- **Projects** are Markdown files in `site/content/projects/` (schema in `site/schema/`). `category: client` marks
  client work, shown separately from my own products. `stage` is building / shipped / experiment / archived.
  Run `bin/rails nibble:build` after editing them.
- **Mascot:** the site's brand is a cheerful teal keycap with headphones, smiling with the sideways "3" of mah3uz —
  `components/Mascot.vue` (animated; pass `alive` to make its eyes follow the pointer) and `site/art/mascot.svg`
  (favicon, social card). It matches the family of the product logos. No animals.
- **Project logos** are each product's own logo, copied from its repository into `public/logos/` and named in the
  project's `logo:` frontmatter. Nibble CLI's is Nibble's mark with a terminal badge. A project without a logo
  (client work) falls back to a plain monogram.
- **Cover art** is generated SVG in `public/art/`, from `site/art/generate.py`
  (`python3 site/art/generate.py public/art`). Add a function there for a new project rather than drawing by hand.
- **Pages, posts, menus and site settings** were seeded from `site/packages/default`, which `site/packages/build.py`
  writes. Edit live content in the Control Plane; re-run the script only to rebuild a fresh database.
- **Photos** are hot-linked from images.unsplash.com and always sit over generated art (`CoverPhoto.vue`), so a page
  never shows a broken image.
- **Client work** stays factual and confidential: no staging URLs, no internal details the client hasn't published.
