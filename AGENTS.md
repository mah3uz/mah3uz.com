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
- **Projects** are entries in the content package, written as Markdown in `site/packages/source/projects/` (schema in
  `site/schema/`); `order` sets their position. `category: client` marks client work, shown separately from my own
  products. `stage` is building / shipped / experiment / archived. `/projects` is the page `source/pages/projects.md`.
- **Images are Nibble library assets, never files in `public/`.** Every image a page, post or project shows lives in the
  package's `site/packages/default/assets/` (listed in `assets.yml`, which `build.py` writes) and is referenced by its
  library path, without a leading slash: `featured_image: art/posts/sqlite-is-enough.svg`, `logo: logos/quarry.svg`,
  and `![alt](art/posts/<slug>/figure.svg)` in a post body. The import uploads a file only when the library has none at
  that path, so a redrawn image reaches the live site through **Replace** on that asset in the Control Plane.
- **Brand mark:** the site's logo is the bracketed tile — the teal gradient tile with three corner brackets and a
  peeled corner, holding an "m" (`assets/brand/favicon.svg`, set as the site settings' `logo`; `components/BrandMark.vue`
  draws the same mark inline). The header shows the site settings' logo, and the site name only when no logo is set.
- **Project logos** are each product's own logo, copied from its repository into `site/packages/default/assets/logos/`
  and named in the project's `logo:`, and kept still: strip any `<animate>`/`<animateTransform>`/`<set>` from a copied SVG,
  because an animated SVG in an `<img>` makes the browser lay out and repaint the whole page every frame, forever
  (Quarry's mascot once kept the home page busy at a third of a core). Nibble CLI's is Nibble's mark with a terminal
  badge. A project without a logo falls back to the bracketed tile with its monogram (`components/ProjectTile.vue`).
- **Cover art** is generated SVG, from `site/art/generate.py`, written into the package
  (`python3 site/art/generate.py site/packages/default/assets/art`). Add a function there for a new project or post
  rather than drawing by hand, then run `build.py` so `assets.yml` lists it.
- **Timeline marks:** every About milestone has a `logo` — the project's own from `logos/`, or a mark from
  `art/marks/`, drawn in `site/art/marks.py` on the brand's teal tile (`art/marks/mah3uz.svg` is the brand mark).
  Add a mark there for a new milestone that has no logo.
- **Pages, posts, projects, menus, site settings and images** come from the content package `site/packages/default`,
  which `site/packages/build.py` writes from the Markdown sources in `site/packages/source/` and the files in
  `default/assets/`. Import with `--mode=update` to replace live content with the package.
- **Removing a field** that holds data needs a content migration in `site/schema/migrations/` (deploys refuse otherwise).
- **Artwork, not stock photos.** Every page, post and project has generated artwork (`ArtBanner.vue`; a page's or post's
  `featured_image`, a project's `cover`).
  Project covers are drawn in `site/art/generate.py`; pages, posts and newer projects in `site/art/more.py`. There are no
  Unsplash or stock images anywhere.
- **Photography** is my own, from unsplash.com/@mah3uz. The `unsplash-photos` scheduled task
  (`site/schema/tasks/unsplash-photos.yml`) imports my 30 most-viewed photos with their statistics into the `photos`
  collection every 12 hours; nothing is stored locally. Images are hotlinked from `images.unsplash.com` (sized by
  `lib/unsplash.ts`) and every link back to Unsplash carries the `utm_source=mah3uz&utm_medium=referral` attribution
  Unsplash's API guidelines require. The access key is the secret `unsplash_access_key` (credentials
  `nibble.secrets.unsplash_access_key`, or `NIBBLE_SECRET_UNSPLASH_ACCESS_KEY`) — never in a file in git.
- **Positioning:** I am both a software engineer and a Linux systems administrator, professionally since 2009, and on
  Linux since I first used computers. Copy should reflect both sides — never only "developer".
- **Emails** are drawn in the site's design by `app/views/layouts/nibble/mailer.html.erb` (and `.text.erb`), which
  Nibble uses for every email it sends; the mark is `public/mail/mark.png` because most mail clients don't show SVG.
  Preview them at `/rails/mailers` in development (`test/mailers/previews/site_mail_preview.rb`). The contact form
  (`site/themes/neat/schema/forms/contact.yml`) sends the visitor a confirmation that carries only my words and the
  topic they picked — never their name or message, so the form can't be used to send anyone else's text. The headings
  Nibble puts on form emails are set in `config/locales/en.yml`.
- **Client work** stays factual and confidential: no staging URLs, no internal details the client hasn't published.
