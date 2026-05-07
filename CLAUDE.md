# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

An **unofficial fan adaptation** of Jet Lag: The Game for rural environments where public transit doesn't exist (vehicles replace transit; county-scale maps replace metro maps). Not affiliated with Jet Lag: The Game, Nebula, or Wendover Productions — keep that disclaimer wording when touching top-level READMEs, and never reproduce copyrighted artwork from the show.

Today this repo is mostly **content scaffolding, not code**. Most rule and asset files are intentional placeholders with `<!-- TODO -->` comments describing what should eventually go there. Treat the skeleton as load-bearing: structure was deliberately stripped to placeholders rather than invented (see commit `8c0ed9c`), so don't fill in rules speculatively — wait for the user to dictate them.

## Repository layout

Top-level folders are **per-game**, not per-concern. Each Jet Lag format gets its own directory with the same internal shape:

```
<game>/
  rules/    # markdown ruleset, one file per topic
  assets/   # printable materials (e.g. investigation-book/)
  tools/    # Python utilities for game setup
```

Currently only `hide-and-seek/` exists. When adding a new format (e.g. `tag/`), mirror this structure and update both the root `README.md` and `CONTRIBUTING.md` tables.

## Domain conventions (important — easy to get wrong)

- **Vehicle-agnostic "range" language.** Don't write "gas," "fuel," or "tank." Use "range" / "driving distance" / "vehicle range" so the rules work for EVs, ICE, hybrids, etc. This was an explicit cleanup (commit `0feb3a6`).
- **Investigation book ≠ card deck.** Seekers ask yes/no geographic questions from a pre-printed *booklet* (some locked until "end game" is declared). Don't model it as a deck of cards. The cost mechanic is inverted from what you might assume: each Seeker question triggers a **card draw for the Hider team** — there is no travel/range budget for Seekers (see `hide-and-seek/rules/budgeting.md`).
- **Two licenses, applied by file type.** Code (`tools/`, scripts) → MIT (`LICENSE`). Content (rules, card designs, assets, docs) → CC BY 4.0 (`LICENSE-ASSETS`). When adding a new file, make sure it lands in a directory whose README already declares the right license, or add the declaration.

## Python tooling

Single root `pyproject.toml` manages dependencies for **all** game `tools/` directories — don't create per-game pyproject files. Managed with [uv](https://github.com/astral-sh/uv); Python pinned to 3.12 via `.python-version`. No dependencies are declared yet.

```bash
uv sync                              # install (once deps exist)
uv run python hide-and-seek/tools/<script>.py
```

There are no tests, lint config, or build pipeline yet — add them when the first real tool lands, not preemptively.
