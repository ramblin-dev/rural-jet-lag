# Sources

Annotated index of where the original **Jet Lag: The Game — Hide + Seek** rules and cards have been digitized. Use these while drafting the rural adaptation; do not mirror their verbatim text into this repo (see [`README.md`](./README.md) for why).

---

## Official (publisher-hosted)

- **Hide + Seek Expansion Pack Vol. 1 Rules** — <https://rules.jetlagthegame.com/expansion/>
  - PDF: <https://rules.jetlagthegame.com/expansion/JLTG-Home-Game-Expansion-1-Rules.pdf>
  - Clarifications and rules for the expansion's 50 curses, 30 power-ups, and metric-unit cards. **Officially published by Jet Lag** — link to it rather than mirroring.
- **Base-game rulebook** — *no official online edition known.* The two-booklet rulebook ships only with the physical box.

---

## Community digitizations

### Comprehensive guides

- **lifack.ch** — <https://www.lifack.ch/docs/quick_start_guide/>
  - Most complete community docs site. Sections mirror the booklet: Quick Start, Rulebook, Cards, Investigation Book, Your Deck, Map Generator.
  - © 2025 Collin Jones (GitHub: `teakivy`). Source repo for the Docusaurus site is private. Site disclaims affiliation with Jet Lag / Nebula / Wendover.
  - WAF blocks non-browser clients (default UA → 403); use a real browser session if you need to revisit.
  - Notable for the **Experimental Game Designs** section, which includes a [Playing With Cars (Or On Foot)](https://www.lifack.ch/docs/experimental_game_designs/playing_with_cars_or_on_foot/) variant — the closest community precedent to what this repo is building. Summarized in [`notes.md`](./notes.md).
- **AJV6812/JetLagHideAndSeek (Sydney variant)** — <https://github.com/AJV6812/JetLagHideAndSeek>
  - 14-page TeX-typeset **Sydney variant** by Alex Varughese, credited "Wendover Productions and Alex Varughese." Localized rules for the NSW Opal transit network. Useful as a *structural model* for what a localized variant looks like — same six question categories and hider-deck card-type taxonomy as the base game, with locale-specific distances, stations, and photo subjects swapped in.
  - Deck composition diverges from lifack: Sydney lists 28 curses and 6 power-up types; lifack ships 24 curses and 7 power-ups (Move is on lifack but not Sydney). Different printings or different curators — when cross-referencing, don't assume curse rosters match.

### Wiki (CC BY-SA — reusable with attribution + share-alike)

- **Hide + Seek wiki** — <https://jetlag.fandom.com/wiki/Hide_%2B_Seek>
- **Curses list** — <https://jetlag.fandom.com/wiki/Hide_%2B_Seek/Curses>
- **Questions list** — <https://jetlag.fandom.com/wiki/Hide_%2B_Seek/Questions>
- Per-season variant pages (UK, Japan, NYC, Switzerland, etc.) under <https://jetlag.fandom.com/wiki/>

Anything imported from these pages goes in [`wiki/`](./wiki/) under CC BY-SA 4.0, not the repo-default CC BY 4.0.

### Interactive / web

- **jetlag.neocities.org** — <https://jetlag.neocities.org/> — interactive question selector; every category, cost, and distance bucket encoded.
- **butlerx/jetlag** — <https://github.com/butlerx/jetlag> (live: <https://butlerx.github.io/jetlag/>) — investigation-book web app (Rust/WASM); all questions encoded in source.
- **CornyPun/Jet-Lag-Hide-and-Seek-Card-Drawer** — <https://github.com/CornyPun/Jet-Lag-Hide-and-Seek-Card-Drawer> — card-drawer with deck data in source.
- **parthivapsani/jetlag-hideseek** — <https://github.com/parthivapsani/jetlag-hideseek> — Flutter PWA companion app (S12/S16 format).

### Of uncertain provenance

- **Scribd uploads** — <https://www.scribd.com/document/937613966/Jet-Lag-Hide-Seek-Rulebook> and <https://www.scribd.com/document/927518365/Fillable-Jet-Lag-Hide-and-Seek-Rules>
  - Scribd's TLS chain fails to validate from many clients (intermediate-cert misconfiguration), so direct fetching is unreliable. Authorship and provenance unverified — these may be fan derivatives or unauthorized scans of the official booklet. Treat as reference-of-last-resort and don't mirror.

---

## Tools, maps, and indexes

- **awesome-jetlag-hide-and-seek** — <https://github.com/jltg-community/awesome-jetlag-hide-and-seek> — curated index of everything below; check it before adding new resources here.
- **taibeled/JetLagHideAndSeek** — <https://github.com/taibeled/JetLagHideAndSeek> — automatic interactive map generation.
- **DahRealPandaaa/JetLagHideAndSeek** — <https://github.com/DahRealPandaaa/JetLagHideAndSeek> — fork of the map generator.
- **LordKnish/jet-lag-portal** — <https://github.com/LordKnish/jet-lag-portal> — coordination portal.
- **JackCampbell5/JetLag-Hide-And-Seek** — <https://github.com/JackCampbell5/JetLag-Hide-And-Seek> — fan web implementation.

---

## Community

- **r/JetLagTheGame** — <https://www.reddit.com/r/JetLagTheGame/>
- **The Layover** — official aftershow podcast; rule clarifications appear here.

---

## Adding a source

When adding a new entry: include the URL, one-line description, and (if relevant) its license. If the source is gated, geo-blocked, or has TLS issues, note that so future maintainers don't waste time on it.
