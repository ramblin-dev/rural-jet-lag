# Setup — Rural Hide and Seek

> Part of [Rural Hide and Seek](./README.md). For the rules themselves see [`rules.md`](./rules.md).

How to set up a Rural Hide + Seek game from scratch. Nothing here changes the official setup steps — it just adds the rural-specific ones (drawing a play area, generating vehicle stations, importing them to a map app).

---

## What you'll need

- Your physical Hide + Seek box (base game and the Vol. 1 expansion). See the [Before you play](../README.md#before-you-play) section of the top-level README for where to buy it.
- A vehicle for each team.
- Phones with location sharing enabled — the original game's live-tracking convention applies unchanged.
- A computer to run the vehicle-stations tool. Python 3.12, [uv](https://github.com/astral-sh/uv), and a clone of this repo. See [`tools/README.md`](./tools/README.md) for the tool's full usage and options.

---

## Step 1 — Pick your play area

Draw a polygon over your intended play area in [geojson.io](https://geojson.io) (easiest) or [felt.com](https://felt.com). Save the result as a GeoJSON file. Either the polygon tool or the line tool works — the vehicle-stations tool accepts both.

For ready-to-run examples, see [`tools/geojson-samples/`](./tools/geojson-samples/).

A few notes on choosing the area:

- The **size tier** (Small / Medium / Large) you'll use later should roughly match the map's footprint and the time you have. The official rulebook's S/M/L guidance applies.
- POI density inside the polygon drives how many stations the tool generates. Very sparse rural areas (few towns, few amenities) will give you very few stations — the game still works, but you'll have a small handful of forced-stop chokepoints.

---

## Step 2 — Generate vehicle stations

From the repo root:

```bash
uv run vehicle-stations --polygon-file path/to/polygon.geojson --name my-game
```

Two files appear in `hide-and-seek/tools/.output/`:

- `my-game-{timestamp}.csv` — for spreadsheets and reference. Includes name, category, cluster id, lat / lon, wait-time range, density tier, nearby-POI count.
- `my-game-{timestamp}.kml` — for upload to a mapping app. Single Folder containing all stations.

The two-tier spacing defaults (300 m within a cluster, 1000 m between clusters) come from the transit research notes. Override with `--min-station-spacing-m` / `--min-cluster-spacing-m` if you want denser or sparser station layouts. Full options: `uv run vehicle-stations --help`.

---

## Step 3 — Import the stations to a map

Upload the `.kml` to **Google My Maps** at <https://mymaps.google.com>:

1. *Create a new map* → *Import* → drop the `.kml`.
2. Each station becomes a pin in a single map layer named after `--name`. The whole layer can be deleted in one click after the game is over.
3. Share the map with both teams so seekers and the hider can reference it during play.

Google Earth, OsmAnd, GAIA, and QGIS also read the file natively if you'd rather use one of those.

---

## Step 4 — Pick a game size

Use the official S/M/L choice based on your map's footprint and the time you have. The wait-time tiers in the tool's output (dense / moderate / sparse) are independent of game size — they reflect local POI density at each station, not the size of the game.

---

## Step 5 — Pre-validate the Investigation Book

Skim the Investigation Book questions and pre-mark any whose subjects don't exist in your area — most commonly "transit line," "high-speed train line," "rail station," or "station-name length" in rural play. Treat those as missing subjects during the game, the same way the official rulebook handles any subject your map doesn't have.

Commercial airports, museums, libraries, hospitals, and similar subjects often *do* exist in rural game areas. Don't pre-cull questions that *might* find a match.

---

## Step 6 — Play

Follow the official Hide + Seek rulebook for everything except seeker / hider transportation, which uses the rules in [`rules.md`](./rules.md). The hiding zone is centered on a vehicle station; everything else (deck, Investigation Book, end-game trigger, found condition, scoring) plays as printed.
