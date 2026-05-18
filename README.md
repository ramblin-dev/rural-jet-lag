# Rural Jet Lag

An unofficial fan project adapting **Jet Lag: The Game** for rural areas with little to no public transit.

**Site:** [ruralhs.ramblin.dev](https://ruralhs.ramblin.dev) — rendered rules, setup walkthrough, and the in-browser vehicle-stations generator.

> **Disclaimer:** This repository is an unofficial fan project. It is not affiliated with, endorsed by, or connected to the official Jet Lag: The Game, Nebula, or Wendover Productions. All rights to the original game concept belong to their respective owners.

---

Hide + Seek (and most Jet Lag formats) leans on the friction of public transit — schedule waits, transfers, station topology — to shape interesting decisions. In rural areas where transit is thin or absent, that friction disappears the moment a player gets in a car or hails a ride. This project introduces rules that make **personal vehicles, ride-sharing, and taxis behave like buses and trains**: a generated map of "vehicle stations" plus a 2d6 departure roll on every trip, preserving the original game's pacing. By-request transport (Uber, Lyft, taxis, hotel shuttles) plays under the same roll, with the allowance that you can time the ride request so the vehicle arrives at the end of your wait. Real bus and train lines in your play area, if any, still play per the official rulebook alongside vehicle stations — modes can be mixed freely. Full write-up of the cars-as-trains mechanic (and the by-request variant) in [`vehicle-stations.md`](./vehicle-stations.md).

---

## Set up and play a rural Hide + Seek game

1. **Get the official game.** Buy the [Hide + Seek home game and Vol. 1 expansion from Nebula](https://store.nebula.tv/collections/jetlag). This project is supplemental — it adapts the official rules, it doesn't replace them. The rulebooks, dice, hider deck, and Investigation Book all come in the box.
2. **Generate vehicle stations.** Open the [in-browser generator](https://ruralhs.ramblin.dev/stations/), draw a polygon over your intended rural play area, and download the auto-generated KML. (Prefer the command line? See [`stations-generator/cli/`](./stations-generator/cli/).)
3. **Import the stations to a map.** Upload the KML to [Google My Maps](https://mymaps.google.com) — one click creates a shareable map layer the whole table can see during play.
4. **Play.** Follow the official rulebook for everything *except* seeker / hider transportation, which uses the rural cars-as-trains mechanic in [`vehicle-stations.md`](./vehicle-stations.md). Per-format rules live in [`hide-and-seek/rules.md`](./hide-and-seek/rules.md); the full setup walkthrough is in [`hide-and-seek/setup.md`](./hide-and-seek/setup.md).

---

## Games

Each game format from the show gets its own directory with rules and any format-specific assets and tools. The cross-game vehicle-stations algorithm (core + Node CLI + regression test) lives in [`/stations-generator/`](./stations-generator/); the site that wraps it (and renders the rules) lives in [`/site/`](./site/).

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
