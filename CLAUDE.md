# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

An **unofficial fan adaptation** of Jet Lag: The Game for rural environments where public transit is thin or absent (cars play under transit-like rules via the vehicle-stations mechanic; county-scale maps stand in for metro maps; real bus/train lines, if any, still play per the official rulebook alongside vehicle stations). Not affiliated with Jet Lag: The Game, Nebula, or Wendover Productions — keep that disclaimer wording when touching top-level READMEs, and never reproduce copyrighted text or artwork from the rulebooks, cards, Investigation Book, or show.

This repo is **supplemental material**, not a standalone game. The READMEs link to the [official Jet Lag store on Nebula](https://store.nebula.tv/collections/jetlag) and assume readers own both the base Hide + Seek home game and the Vol. 1 expansion. Rural-variant rules adapt the official mechanics; they don't replace them.

Today this repo is mostly **content scaffolding, not code**. Most rule and asset files are intentional placeholders with `<!-- TODO -->` comments describing what should eventually go there. Treat the skeleton as load-bearing: structure was deliberately stripped to placeholders rather than invented (see commit `8c0ed9c`), so don't fill in rules speculatively — wait for the user to dictate them.

## Repository layout

Top-level folders are mostly **per-game**, with a small set of shared cross-game folders. Each Jet Lag format gets its own directory with the same internal shape:

```
<game>/
  rules.md    # the ruleset (single file; defers to the official rulebook for everything we don't override)
  setup.md    # how to set up a game (e.g. running tools, importing maps)
  assets/     # printable materials (e.g. investigation-book/)
  tools/      # game-specific Python utilities
  reference/  # structural notes about the original game (see Domain conventions)
```

Currently only `hide-and-seek/` exists. When adding a new format (e.g. `tag/`), mirror this structure and update the root `README.md` and `CONTRIBUTING.md` tables.

The cross-game pieces:

- `vehicle-stations.md` (repo root) — the canonical write-up of the cars-as-trains mechanic that every rural Jet Lag adaptation in this repo shares (what a station is, how the 2d6 departure roll works, route declaration / mid-route changes). Per-game `rules.md` files reference it instead of restating the mechanic. When you change the cross-game mechanic, edit it here, not in the per-game files.
- `stations-generator/` (repo root) — JS workspaces holding the cross-game vehicle-stations algorithm: `stations-generator/core/` (isomorphic algorithmic core), `stations-generator/cli/` (Node CLI), and `stations-generator/test/` (frozen Overpass fixture + reference CSV/KML so `npm test` catches algorithmic drift). The *browser* form of the generator lives in the site (see below) and consumes `@rural-jet-lag/core` as a workspace dependency. Game-specific scripts (Python, currently) still live in `<game>/tools/`. If additional cross-game tools appear later, they should get their own top-level directories named after their purpose, not a generic shared `tools/` slot.
- `site/` (repo root) — the Vite multi-page site at `ruralhs.ramblin.dev`. Landing page + rules/setup/vehicle-stations pages rendered at build time from the source `.md` files (single source of truth — no duplication) via the plugin in `site/plugins/markdown.js`, plus the vehicle-stations generator UI at `/stations`. Deploys to Netlify (`netlify.toml` at repo root) on push to `main`. `site/shared/` holds site-wide CSS and the generator-only stylesheet.
- `reference/` (repo root) — cross-game research that supports the shared mechanics (currently `transit-friction.md` on the academic literature behind the vehicle-stations mechanic). Per-game *original-rulebook* reference material stays under `<game>/reference/`.

The repo-root `.input/` is **gitignored** and serves as a personal-reference cache for scans, saved web pages, and PDFs of source material that we don't want in the repo. Never check anything into `.input/`, and don't suggest publishing its contents. It exists so we can read source material when verifying inventory or designing rules without committing it.

Tool scripts write outputs to `.output/` directories (also gitignored repo-wide). Don't commit anything from those folders.

## Domain conventions (important — easy to get wrong)

- **Vehicle-agnostic "range" language.** Don't write "gas," "fuel," or "tank." Use "range" / "driving distance" / "vehicle range" so the rules work for EVs, ICE, hybrids, etc. This was an explicit cleanup (commit `0feb3a6`).
- **Investigation book ≠ card deck.** Seekers ask yes/no geographic questions from a pre-printed *booklet* (some locked until "end game" is declared). Don't model it as a deck of cards. The cost mechanic is inverted from what you might assume: each Seeker question triggers a **card draw for the Hider team** — there is no travel/range budget for Seekers.
- **Rural variant defers to the official rulebook for everything except transportation.** The hider deck, hiding zone, Investigation Book, end-game trigger, and scoring are all unchanged from the official Hide + Seek rules. The only addition is the artificial "vehicle stations" + departure-roll mechanic in `hide-and-seek/rules.md`. Don't redesign mechanics that the rural variant explicitly inherits — including curses we previously thought might need replacement, which work as printed under the cars-as-trains framing.
- **Reference subtree is non-reproducing.** `<game>/reference/` holds analytical and structural commentary on the original game, not verbatim source text. Card and question *names* are factual inventory and fine to list; *mechanics* get paraphrased into our own words; *card text and rulebook prose* never get copied in. The one exception is `<game>/reference/wiki/` — that subtree is licensed CC BY-SA 4.0 (separate from the repo-default CC BY 4.0) and hosts wiki imports under that license with attribution. See `hide-and-seek/reference/README.md` for the full posture.
- **Two licenses, applied by file type.** Code (`tools/`, scripts) → MIT (`LICENSE`). Content (rules, card designs, assets, docs) → CC BY 4.0 (`LICENSE-ASSETS`). The `<game>/reference/wiki/` subtree carves out a CC BY-SA 4.0 region for wiki-sourced content. When adding a new file, make sure it lands in a directory whose README already declares the right license, or add the declaration.

## Tooling

The repo has two language ecosystems, side by side:

- **JS** — npm workspaces rooted at the repo root (`stations-generator/core`, `stations-generator/cli`, `site`). Node 20+. Common commands, all run from the repo root:

  ```bash
  npm install              # one-time
  npm run dev              # Vite dev server for the site (with HMR)
  npm run build            # produces site/dist/ for Netlify
  npm run preview          # serve the built dist locally
  npm run cli -- --help    # invoke the Node vehicle-stations CLI
  npm test                 # regression test for the vehicle-stations pipeline
  ```

  When changing algorithm behavior in `stations-generator/core/`, the regression test will fail; see `stations-generator/test/README.md` for how to bless a new baseline.

  The site's markdown pipeline (`site/plugins/markdown.js`) reads source `.md` files from outside `site/` (e.g. `hide-and-seek/rules.md`) at build time and inlines the rendered HTML into each page's `<main>`. Relative links in those sources are rewritten to in-site routes where one exists, falling back to canonical GitHub URLs otherwise. Don't duplicate rules content into `site/` — keep the source `.md` files as the single source of truth and let the pipeline render them.

- **Python** under `hide-and-seek/tools/` — the OCR pipeline for processing scanned rulebook material. Single root `pyproject.toml`; managed with [uv](https://github.com/astral-sh/uv). Per-game directory names contain hyphens, so scripts aren't installable as console commands; invoke directly:

  ```bash
  uv sync                                              # install
  uv run python hide-and-seek/tools/<script>.py        # direct script invocation
  ```

There are no lint configs yet — add them when the first non-trivial tool needs them, not preemptively. `stations-generator/test/` is currently the only automated test suite — `npm test` from the repo root runs it and exits non-zero on any regression.
