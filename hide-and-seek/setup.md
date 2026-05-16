# Setup — Rural Hide and Seek

> Part of [Rural Hide and Seek](./README.md). For the rules themselves see [`rules.md`](./rules.md).

How to set up a Rural Hide + Seek game from scratch. Nothing here changes the official setup steps — it just adds the rural-specific ones (drawing a play area, generating vehicle stations, importing them to a map app).

---

## What you'll need

- Your physical Hide + Seek box (base game and the Vol. 1 expansion). See the [Before you play](../README.md#before-you-play) section of the top-level README for where to buy it.
- A vehicle for each team.
- Phones with location sharing enabled — the original game's live-tracking convention applies unchanged.
- A device with a modern browser to run the vehicle-stations generator. The full tool is in [`/stations-generator/`](../stations-generator/) — either the in-browser site (most convenient) or the Node CLI. See [`/vehicle-stations.md`](../vehicle-stations.md) for what stations are and how the in-game mechanic uses them.

---

## Step 1 — Generate vehicle stations

From the repo root, start the site:

```bash
cd stations-generator
npm install        # one-time
npm run dev:site
```

Open the printed URL. Use the polygon tool on the map to draw your play area. Stations generate automatically once the polygon closes.

A few notes on choosing the area:

- The **size tier** (Small / Medium / Large) the tool infers should roughly match the map's footprint and the time you have. The official rulebook's S/M/L guidance applies. You can override the inferred tier in the sidebar.
- POI density inside the polygon drives how many stations get generated. Very sparse rural areas (few towns, few amenities) will give you very few stations — the game still works, but you'll have a small handful of forced-stop chokepoints.
- If parts of your polygon are unplayable (a closed military range, private land, a national-forest boundary you're skipping), switch to **Exclusion zone** mode in the sidebar and draw a red polygon over each. Stations inside any exclusion are removed automatically.

The sidebar shows the inferred game size, the cluster radius, the per-cluster cap, and the total station count. Tweak any sidebar setting and stations re-render instantly without re-hitting Overpass.

Prefer the command line? `npm run cli -- --polygon-file path/to/polygon.geojson --name my-game` produces a `.csv` (for spreadsheets and reference) and a `.kml` (for upload to a mapping app) under `stations-generator/.output/`. Same flags as the sidebar settings — see `npm run cli -- --help`.

---

## Step 2 — Import the stations to a map

Click **Download KML** in the sidebar (or use the file the CLI wrote). Then upload it to **Google My Maps** at <https://mymaps.google.com>:

1. *Create a new map* → *Import* → drop the `.kml`.
2. Each station becomes a pin in a single map layer. The whole layer can be deleted in one click after the game is over.
3. Share the map with both teams so seekers and the hider can reference it during play.

Google Earth, OsmAnd, GAIA, and QGIS also read the file natively if you'd rather use one of those.

---

## Step 3 — Confirm the game size

Look at the sidebar (or CLI stderr) summary — it shows the inferred game size and the area chain (e.g. `Game size: M (inferred from area (330 km² gross − 2 km² water = 329 km² net))`). Double-check the S/M/L tier matches your map's footprint and the time you have. The same tier drives both the cluster radius the tool used and the in-game hiding-zone radius (¼ mile for S/M, ½ mile for L). If the inference is wrong (e.g. the tool couldn't subtract water for a coastal polygon and over-estimated area), override the game size in the sidebar (or re-run the CLI with `--game-size`).

The wait-time tiers in the tool's output (dense / moderate / sparse) are independent of game size — they reflect local POI density at each station, not the size of the game.

---

## Step 4 — Pre-validate the Investigation Book

Skim the Investigation Book questions and pre-mark any whose subjects don't exist in your area — most commonly "transit line," "high-speed train line," "rail station," or "station-name length" in rural play. Treat those as missing subjects during the game, the same way the official rulebook handles any subject your map doesn't have.

Commercial airports, museums, libraries, hospitals, and similar subjects often *do* exist in rural game areas. Don't pre-cull questions that *might* find a match.

---

## Step 5 — Play

Follow the official Hide + Seek rulebook for everything except seeker / hider transportation, which uses the rules in [`rules.md`](./rules.md). The hiding zone is centered on a vehicle station; everything else (deck, Investigation Book, end-game trigger, found condition, scoring) plays as printed.
