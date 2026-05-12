# Rural Jet Lag

An unofficial fan project adapting **Jet Lag: The Game** for rural areas with little to no public transit.

> **Disclaimer:** This repository is an unofficial fan project. It is not affiliated with, endorsed by, or connected to the official Jet Lag: The Game, Nebula, or Wendover Productions. All rights to the original game concept belong to their respective owners.

---

Hide + Seek (and most Jet Lag formats) leans on the friction of public transit — schedule waits, transfers, station topology — to shape interesting decisions. In rural areas where transit is thin or absent, that friction disappears the moment a player gets in a car. This project introduces rules that make **personal vehicles behave like buses and trains**: a generated map of "vehicle stations" plus a 2d6 departure roll on every trip, preserving the original game's pacing. Real bus and train lines in your play area, if any, still play per the official rulebook alongside vehicle stations — nothing is removed. Full write-up of the cars-as-trains mechanic in [`vehicle-stations.md`](./vehicle-stations.md).

---

## Set up and play a rural Hide + Seek game

1. **Get the official game.** Buy the [Hide + Seek home game and Vol. 1 expansion from Nebula](https://store.nebula.tv/collections/jetlag). This project is supplemental — it adapts the official rules, it doesn't replace them. The rulebooks, dice, hider deck, and Investigation Book all come in the box.
2. **Draw your play area.** Open [geojson.io](https://geojson.io), draw a polygon over your intended rural play area, and save as GeoJSON.
3. **Generate vehicle stations.** From the repo root, run:
   ```bash
   uv run vehicle-stations --polygon-file your-area.geojson --name my-game
   ```
   With no other flags, the tool infers the official S/M/L game size from polygon area, sets cluster radius to the hiding-zone radius for that size, and auto-tunes the per-cluster cap to land the station count inside the rulebook's band. Outputs a `.kml` you can import into Google My Maps as a single shareable map layer.
4. **Play.** Follow the official rulebook for everything *except* seeker / hider transportation, which uses the rural cars-as-trains mechanic in [`vehicle-stations.md`](./vehicle-stations.md). Per-format rules live in [`hide-and-seek/rules.md`](./hide-and-seek/rules.md); the full setup walkthrough is in [`hide-and-seek/setup.md`](./hide-and-seek/setup.md).

---

## Games

Each game format from the show gets its own directory with rules and any format-specific assets and tools. Cross-game tooling lives in [`/tools/`](./tools/).

| Directory | Game | Status |
|-----------|------|--------|
| [`/hide-and-seek`](./hide-and-seek/) | Hide and Seek — rural driving variant | ✅ Active |

---

## Contributing

Contributions are welcome! Card designs, tool improvements, and rule clarifications all help grow this resource. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## License

This project uses a dual-license approach:

- **Code** (scripts, tools): [MIT License](./LICENSE)
- **Content** (rules, card designs, assets, documentation): [CC BY 4.0](./LICENSE-ASSETS)

See each license file for full terms.

---

## Community

- **Subreddit:** [r/JetLagTheGame](https://www.reddit.com/r/JetLagTheGame/) — Discussions on rural play exist (search: "Hide and Seek Card Game in Rural Areas").
- **Curated resource list:** [jltg-community/awesome-jetlag-hide-and-seek](https://github.com/jltg-community/awesome-jetlag-hide-and-seek) — Maintained index of fan tools, decks, and rule variants.
- **Jet Lag Wiki:** [jetlag.fandom.com](https://jetlag.fandom.com/) — Card templates and game history.
