# Your site

This directory is yours, and an upgrade never touches what you put in it:

- `schema/` — your collections, taxonomies, blueprints, globals, navigation and forms
- `packages/` — the content package: pages, posts, projects, menus, settings and every image
- `art/` — the scripts that draw the site's artwork
- `themes/<name>/` — your own theme; one of Nibble's, such as `crumbs`, needs no copy here
- `cp/` — your Control Plane overrides

Your own Ruby lives where Rails puts it — `app/`, `config/initializers/`, `test/` — and is yours as well. So is every
Rails setting in `config/`: the lines Nibble needs there are marked `# Nibble:` with the reason, and
in production, Nibble names any it relies on and no longer finds, at boot and in `bin/rails nibble:check`.

## Schema

Schema is read in three layers — Nibble's own, then your theme's, then `site/schema/` — and the last one to define a
handle wins, so a file here named after one of Nibble's replaces it. It uses the same layout as Nibble's:
`collections/<handle>.yml`, `taxonomies/`, `blueprints/collections/<collection>/<handle>.yml`, `fieldsets/`,
`globals/`, `navigation/`, `forms/`.

**An override replaces the whole file**, not the keys in it: start from a copy of the one you are replacing. To
remove one of Nibble's collections instead, list it under `disable:` in `config/nibble.yml`. Run
`bin/rails nibble:check` after editing anything here.

## Content and images

All content lives in the database and reaches it through the content package `site/packages/default/`, which
`site/packages/build.py` writes from Markdown in `site/packages/source/` (`pages/`, `posts/`, `projects/`) and from the
files in `site/packages/default/assets/`:

```sh
python3 site/art/generate.py                                   # draw the artwork into the package
python3 site/packages/build.py                                 # write the package
bin/rails nibble:content:validate site/packages/default
bin/rails nibble:content:import site/packages/default --mode=update
```

Every image is an asset in the Control Plane's library, never a file in `public/`. Content names one by its library
path, without a leading slash: `featured_image: art/posts/sqlite-is-enough.svg`, `logo: logos/quarry.svg`, and
`![alt](art/posts/<slug>/figure.svg)` in a post. The import uploads a file only when the library has none at that
path, so a redrawn image reaches the live site through **Replace** on that asset in the Control Plane.

`--mode=update` replaces what has been edited in the Control Plane since the package was made. On a server, run the
import straight after a deploy that changes the schema the package fills.

## Control Plane overrides

To change one of Nibble's Control Plane screens, copy it to the same path under `site/cp/` and edit the copy:

```
vendor/nibble/frontend/nibble-cp/pages/cp/entries/Edit.vue   ->   site/cp/pages/cp/entries/Edit.vue
```

Yours is loaded instead of ours. Nothing else changes, and Nibble's file stays where it is.

Use `bin/rails nibble:eject` rather than copying by hand: it puts the file in the right place and records that you
now maintain it, so upgrades can tell you when the original changed.

**An override is a copy, not a patch.** Once a file is here it stops getting our improvements and bug fixes, so
prefer the supported extension points first and eject only when there is no other way.

## Your own Ruby

In an initializer of your own in `config/initializers/`, subscribe to Nibble's load hooks rather than reopening its
classes:

```ruby
ActiveSupport.on_load(:nibble_entry) do
  def reading_minutes = (data["body"].to_s.split.size / 200.0).ceil
end
```

Hooks are published for `:nibble_entry`, `:nibble_term` and `:nibble_asset`.

## Slots

Some parts of the Control Plane take a replacement without ejecting anything. Drop a component at
`site/cp/slots/<Name>.vue` and it is used instead of ours:

| Slot | Replaces |
|---|---|
| `Logo.vue` | the mark in the Control Plane header |
| `SidebarExtra.vue` | empty space at the bottom of the sidebar |
| `Scripts.vue` | nothing — a place to add your own scripts or widgets to every Control Plane page |

Slots survive upgrades, so prefer one over ejecting the whole screen.
