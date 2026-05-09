# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

An **unofficial fan adaptation** of Jet Lag: The Game for rural environments where public transit doesn't exist (vehicles replace transit; county-scale maps replace metro maps). Not affiliated with Jet Lag: The Game, Nebula, or Wendover Productions — keep that disclaimer wording when touching top-level READMEs, and never reproduce copyrighted text or artwork from the rulebooks, cards, Investigation Book, or show.

This repo is **supplemental material**, not a standalone game. The READMEs link to the [official Jet Lag store on Nebula](https://store.nebula.tv/collections/jetlag) and assume readers own both the base Hide + Seek home game and the Vol. 1 expansion. Rural-variant rules adapt the official mechanics; they don't replace them.

Today this repo is mostly **content scaffolding, not code**. Most rule and asset files are intentional placeholders with `<!-- TODO -->` comments describing what should eventually go there. Treat the skeleton as load-bearing: structure was deliberately stripped to placeholders rather than invented (see commit `8c0ed9c`), so don't fill in rules speculatively — wait for the user to dictate them.

## Repository layout

Top-level folders are **per-game**, not per-concern. Each Jet Lag format gets its own directory with the same internal shape:

```
<game>/
  rules/      # markdown ruleset, one file per topic
  assets/     # printable materials (e.g. investigation-book/)
  tools/      # Python utilities for game setup
  reference/  # structural notes about the original game (see Domain conventions)
```

Currently only `hide-and-seek/` exists. When adding a new format (e.g. `tag/`), mirror this structure and update both the root `README.md` and `CONTRIBUTING.md` tables.

There is also a top-level `rural_jet_lag/` Python package that holds **console-script shims only** — small wrappers that delegate to per-game tool scripts so they can be invoked as `uv run <command>` from the repo root via `[project.scripts]` in `pyproject.toml`. Real tool implementations live in `<game>/tools/`, not here. When adding a new console command, add a wrapper in `rural_jet_lag/` and an entry in `[project.scripts]`; don't move the underlying script out of its game folder.

The repo-root `.input/` is **gitignored** and serves as a personal-reference cache for scans, saved web pages, and PDFs of source material that we don't want in the repo. Never check anything into `.input/`, and don't suggest publishing its contents. It exists so we can read source material when verifying inventory or designing rules without committing it.

Tool scripts write outputs to `.output/` directories (also gitignored repo-wide). Don't commit anything from those folders.

## Domain conventions (important — easy to get wrong)

- **Vehicle-agnostic "range" language.** Don't write "gas," "fuel," or "tank." Use "range" / "driving distance" / "vehicle range" so the rules work for EVs, ICE, hybrids, etc. This was an explicit cleanup (commit `0feb3a6`).
- **Investigation book ≠ card deck.** Seekers ask yes/no geographic questions from a pre-printed *booklet* (some locked until "end game" is declared). Don't model it as a deck of cards. The cost mechanic is inverted from what you might assume: each Seeker question triggers a **card draw for the Hider team** — there is no travel/range budget for Seekers (see `hide-and-seek/rules/budgeting.md`).
- **Reference subtree is non-reproducing.** `<game>/reference/` holds analytical and structural commentary on the original game, not verbatim source text. Card and question *names* are factual inventory and fine to list; *mechanics* get paraphrased into our own words; *card text and rulebook prose* never get copied in. The one exception is `<game>/reference/wiki/` — that subtree is licensed CC BY-SA 4.0 (separate from the repo-default CC BY 4.0) and hosts wiki imports under that license with attribution. See `hide-and-seek/reference/README.md` for the full posture.
- **Two licenses, applied by file type.** Code (`tools/`, scripts) → MIT (`LICENSE`). Content (rules, card designs, assets, docs) → CC BY 4.0 (`LICENSE-ASSETS`). The `<game>/reference/wiki/` subtree carves out a CC BY-SA 4.0 region for wiki-sourced content. When adding a new file, make sure it lands in a directory whose README already declares the right license, or add the declaration.

## Python tooling

Single root `pyproject.toml` manages dependencies for **all** game `tools/` directories — don't create per-game pyproject files. Managed with [uv](https://github.com/astral-sh/uv); Python pinned to 3.12 via `.python-version`. The build backend is `hatchling`, configured to package the `rural_jet_lag/` shim package so `[project.scripts]` console commands work via `uv run`.

```bash
uv add <package>                     # add a dep (preferred over editing pyproject.toml by hand)
uv sync                              # install (rebuilds the project package automatically)
uv run vehicle-stations --help       # registered console command
uv run python hide-and-seek/tools/<script>.py   # direct script invocation
```

There are no tests or lint config yet — add them when the first non-trivial tool lands, not preemptively.
