# Contributing to Rural Jet Lag

Thank you for your interest in contributing! This project is community-driven, and contributions of all kinds are welcome — whether you're fixing typos, designing cards, or improving tools.

---

## Repository Structure

Each Jet Lag game format has its own top-level directory. When contributing, work within the relevant game folder:

| Directory | Game |
|-----------|------|
| [`/hide-and-seek`](./hide-and-seek/) | Hide and Seek — rural driving variant |

Cross-game material — the shared cars-as-trains mechanic write-up at [`/vehicle-stations.md`](./vehicle-stations.md) and any tools that work across formats in [`/tools/`](./tools/) — lives at the repo root.

---

## Ways to Contribute

### 📋 Rules Clarifications
Found an ambiguity in the ruleset? Open an issue or submit a PR to the game's `rules.md` file.

### 🃏 Card Designs
- Add printable card templates or updated designs to the game's `assets/cards/` directory.
- Preferred formats: SVG, PDF, or high-resolution PNG.
- Please ensure your designs don't reproduce copyrighted artwork from the official show.

### 🛠️ Tools & Scripts
- Cross-game tooling lives in the top-level [`/tools/`](./tools/) npm workspace (`core/` shared logic, `cli/` Node CLI, `site/` static site). Run `npm install` in `tools/` to get set up; `npm run dev:site` for the dev server, `npm run parity:js` to verify the regression test still passes.
- Tools specific to a single format belong in that game's `tools/` directory and may be in Python (`uv run python <game>/tools/<script>.py`) since per-game directories aren't packaged.
- All code contributions are covered by the [MIT License](./LICENSE).
- Include a docstring or `README.md` section explaining how to use your tool.

### 🎮 New Game Formats
Adding support for a new Jet Lag game type? Create a new top-level folder (e.g., `/tag/`) following the same structure as `/hide-and-seek/`: a `README.md`, `rules.md`, `setup.md`, and `assets/`, `tools/`, `reference/` subdirectories.

---

## Pull Request Guidelines

1. **Fork** the repository and create a branch from `main`.
2. Keep changes focused — one logical change per PR.
3. Update the relevant `README.md` if you add a new file or directory.
4. Open a draft PR early if you want feedback before finishing.

---

## Code of Conduct

Be kind and inclusive. This is a fan project for people who love games and the outdoors. Harassment, gatekeeping, or disrespectful behavior will not be tolerated.

---

## License

By contributing, you agree that:
- **Code contributions** are licensed under the [MIT License](./LICENSE).
- **Content contributions** (rules, cards, documentation) are licensed under [CC BY 4.0](./LICENSE-ASSETS).

---

## Questions?

Open an issue on GitHub.
