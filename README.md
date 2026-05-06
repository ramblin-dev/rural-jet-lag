# Rural Jet Lag: Hide and Seek

An unofficial fan project adapting **Jet Lag: The Game — Hide and Seek** for rural environments where public transit is non-existent or insufficient.

> **Disclaimer:** This repository is an unofficial fan project. It is not affiliated with, endorsed by, or connected to the official Jet Lag: The Game, Nebula, or Wendover Productions. All rights to the original game concept belong to their respective owners.

---

## The Problem

The official fan game criteria and the original mechanics rely heavily on existing transportation infrastructure — subways, buses, trains. In rural America and similar regions, this infrastructure simply does not exist. County seats can be 30 miles apart, the nearest bus stop might be in the next state, and "walking distance" means something very different when the grocery store is 15 miles away.

## The Solution

This project substitutes public transit with **private vehicle driving** (cars), and adapts the rules, budgets, map scales, and challenges to fit a rural setting. Think county roads, grain silos, and water towers instead of metro lines and train stations.

---

## Repository Structure

| Directory | Contents |
|-----------|----------|
| [`/rules`](./rules/) | Markdown files detailing the Rural Variant ruleset |
| [`/assets`](./assets/) | Printable card templates for rural challenges, curses, and powerups |
| [`/tools`](./tools/) | Scripts for generating driving-time isochrones and other map utilities |
| [`/challenges`](./challenges/) | A crowdsourced database of rural-specific challenge ideas |

---

## Quick-Start Rules Summary

1. **Map Scale:** Play on a 50–100 mile radius (or use county boundaries) instead of a metro transit zone.
2. **Travel Mode:** All travel is by personal vehicle. No transit passes — buy **Gas Cards** instead.
3. **Budget:** Starting budget is set in gallons of gas (or a dollar equivalent at local prices). Challenges can award or cost gas.
4. **Hiding:** Use rural landmarks — water towers, grain silos, specific highway exits, post offices, historical markers, or the smallest incorporated town in your county.
5. **Boundaries:** Natural features (rivers, ridgelines) and county/state lines replace transit zone boundaries.

See the [`/rules`](./rules/) directory for the full ruleset.

---

## Existing Resources & Inspiration

These community projects were referenced when designing this adaptation:

### Map & Logistics Tools
- [taibeled/JetLagHideAndSeek](https://github.com/taibeled/JetLagHideAndSeek) — Automatic interactive map generation; rural users should switch isochrone mode from walking/transit to **driving**.
- [LordKnish/jet-lag-portal](https://github.com/LordKnish/jet-lag-portal) — Web portal for coordinating a private hide-and-seek game; card systems and progress tracking.
- [JackCampbell5/JetLag-Hide-And-Seek](https://github.com/JackCampbell5/JetLag-Hide-And-Seek) — Fan-made web implementation of the card game.
- [jltg-community/awesome-jetlag-hide-and-seek](https://github.com/jltg-community/awesome-jetlag-hide-and-seek) — Curated list of resources.

### Card Assets & Templates
- [Jet Lag Wiki — Challenge Card Templates](https://jetlag.fandom.com/) — Templates for customizing challenge cards.
- [lifack.ch Unofficial Card Recreation](https://lifack.ch/) — Fan-made recreation of Powerups, Curses, and Blanks.
- Community Canva templates shared in fan Discord servers for custom curses and challenges.

### Community
- **Subreddit:** [r/JetLagTheGame](https://www.reddit.com/r/JetLagTheGame/) — Discussions on rural play exist (search: "Hide and Seek Card Game in Rural Areas").
- **Jet Lag Wiki:** [jetlag.fandom.com](https://jetlag.fandom.com/) — Challenge card templates and game history.
- **Discord:** Check the subreddit sidebar for active community servers.

---

## Contributing

Contributions are welcome! Rural challenges, card designs, tool improvements, and rule clarifications all help grow this resource. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## License

This project uses a dual-license approach:

- **Code** (scripts, tools): [MIT License](./LICENSE)
- **Content** (rules, card designs, assets, documentation): [CC BY 4.0](./LICENSE-ASSETS)

See each license file for full terms.
