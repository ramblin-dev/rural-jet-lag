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
- `tools/` (repo root) — Python utilities that work across formats (currently the vehicle-stations generator and its GeoJSON samples). Game-specific scripts still live in `<game>/tools/`. New utilities go in whichever folder matches their scope.
- `reference/` (repo root) — cross-game research that supports the shared mechanics (currently `transit-friction.md` on the academic literature behind the vehicle-stations mechanic). Per-game *original-rulebook* reference material stays under `<game>/reference/`.

Console scripts are registered in `[project.scripts]` in `pyproject.toml` and point directly at the underlying tool's `main()` function (e.g. `vehicle-stations = "tools.generate_vehicle_stations:main"`). The `tools/` directory has an `__init__.py` so hatch can package it and the entry points resolve. There is no shim layer — to register a new console command, add an entry in `[project.scripts]` pointing at the script's module path. (Game-specific tools under `<game>/tools/` can't currently be exposed as console scripts because the directory names contain hyphens, which aren't valid in Python module paths; invoke those scripts directly with `uv run python <game>/tools/<script>.py`.)

The repo-root `.input/` is **gitignored** and serves as a personal-reference cache for scans, saved web pages, and PDFs of source material that we don't want in the repo. Never check anything into `.input/`, and don't suggest publishing its contents. It exists so we can read source material when verifying inventory or designing rules without committing it.

Tool scripts write outputs to `.output/` directories (also gitignored repo-wide). Don't commit anything from those folders.

## Domain conventions (important — easy to get wrong)

- **Vehicle-agnostic "range" language.** Don't write "gas," "fuel," or "tank." Use "range" / "driving distance" / "vehicle range" so the rules work for EVs, ICE, hybrids, etc. This was an explicit cleanup (commit `0feb3a6`).
- **Investigation book ≠ card deck.** Seekers ask yes/no geographic questions from a pre-printed *booklet* (some locked until "end game" is declared). Don't model it as a deck of cards. The cost mechanic is inverted from what you might assume: each Seeker question triggers a **card draw for the Hider team** — there is no travel/range budget for Seekers.
- **Rural variant defers to the official rulebook for everything except transportation.** The hider deck, hiding zone, Investigation Book, end-game trigger, and scoring are all unchanged from the official Hide + Seek rules. The only addition is the artificial "vehicle stations" + departure-roll mechanic in `hide-and-seek/rules.md`. Don't redesign mechanics that the rural variant explicitly inherits — including curses we previously thought might need replacement, which work as printed under the cars-as-trains framing.
- **Reference subtree is non-reproducing.** `<game>/reference/` holds analytical and structural commentary on the original game, not verbatim source text. Card and question *names* are factual inventory and fine to list; *mechanics* get paraphrased into our own words; *card text and rulebook prose* never get copied in. The one exception is `<game>/reference/wiki/` — that subtree is licensed CC BY-SA 4.0 (separate from the repo-default CC BY 4.0) and hosts wiki imports under that license with attribution. See `hide-and-seek/reference/README.md` for the full posture.
- **Two licenses, applied by file type.** Code (`tools/`, scripts) → MIT (`LICENSE`). Content (rules, card designs, assets, docs) → CC BY 4.0 (`LICENSE-ASSETS`). The `<game>/reference/wiki/` subtree carves out a CC BY-SA 4.0 region for wiki-sourced content. When adding a new file, make sure it lands in a directory whose README already declares the right license, or add the declaration.

## Python tooling

Single root `pyproject.toml` manages dependencies for **all** tool directories (cross-game `tools/` and per-game `<game>/tools/`) — don't create per-game pyproject files. Managed with [uv](https://github.com/astral-sh/uv); Python pinned to 3.12 via `.python-version`. The build backend is `hatchling`, configured to package the cross-game `tools/` directory so `[project.scripts]` console commands resolve via `uv run`.

```bash
uv add <package>                     # add a dep (preferred over editing pyproject.toml by hand)
uv sync                              # install (rebuilds the project package automatically)
uv run vehicle-stations --help       # registered console command
uv run python hide-and-seek/tools/<script>.py   # direct script invocation
```

There are no tests or lint config yet — add them when the first non-trivial tool lands, not preemptively.
