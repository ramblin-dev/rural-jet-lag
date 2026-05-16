# Setup — Rural Hide and Seek

> Part of [Rural Hide and Seek](./README.md). For the rules themselves see [`rules.md`](./rules.md).

How to set up a Rural Hide + Seek game from scratch. Nothing here changes the official setup steps — it just adds the rural-specific ones (drawing a play area, generating vehicle stations, importing them to a map app).

---

## What you'll need

- Your physical Hide + Seek box (base game and the Vol. 1 expansion). See the [Before you play](../README.md#before-you-play) section of the top-level README for where to buy it.
- A vehicle for each team.
- Phones with location sharing enabled — the original game's live-tracking convention applies unchanged.
- A computer to run the vehicle-stations tool. Python 3.12, [uv](https://github.com/astral-sh/uv), and a clone of this repo. See [`/old-tools/README.md`](../old-tools/README.md) for the tool's full usage and options, and [`/vehicle-stations.md`](../vehicle-stations.md) for what stations are and how the in-game mechanic uses them.

---

## Step 1 — Pick your play area

Draw a polygon over your intended play area in [geojson.io](https://geojson.io) (easiest) or [felt.com](https://felt.com). Save the result as a GeoJSON file. Either the polygon tool or the line tool works — the vehicle-stations tool accepts both.

For ready-to-run examples, see [`/old-tools/geojson-samples/`](../old-tools/geojson-samples/).

A few notes on choosing the area:

- The **size tier** (Small / Medium / Large) you'll use later should roughly match the map's footprint and the time you have. The official rulebook's S/M/L guidance applies.
- POI density inside the polygon drives how many stations the tool generates. Very sparse rural areas (few towns, few amenities) will give you very few stations — the game still works, but you'll have a small handful of forced-stop chokepoints.

---

## Step 2 — Generate vehicle stations

From the repo root:

```bash
uv run python old-tools/generate_vehicle_stations.py --polygon-file path/to/polygon.geojson --name my-game
```

That's it. With no other flags, the tool computes the polygon's area (subtracting OSM water bodies), bins it into the rulebook's S/M/L map-size tier, sets the cluster radius to the official hiding-zone radius for that tier (¼ mile for S/M, ½ mile for L), and auto-tunes the per-cluster station cap so the total station count lands inside the rulebook's S/M/L station band (S 30–100, M 100–500, L 500+). Every inference step prints to stderr so you can see why the tool chose what it chose.

If you already know the tier you want, pass `--game-size {S,M,L}` to skip the area-binning step. To exclude additional land from the area calc (a national-forest boundary you're skipping, a closed military range), pass `--subtract-polygon FILE` with another GeoJSON. To skip the OSM water query entirely (faster on huge polygons where it can time out), pass `--no-water-subtract`.

Two files appear in `old-tools/.output/`:

- `my-game-{timestamp}.csv` — for spreadsheets and reference. Includes name, category, cluster id, lat / lon, wait-time range, density tier, nearby-POI count, open-during-play status, raw OSM `opening_hours` string.
- `my-game-{timestamp}.kml` — for upload to a mapping app. Single Folder containing all stations.

For finer control (intra-cluster spacing, manual cap, etc.), see `uv run python old-tools/generate_vehicle_stations.py --help` and the [old-tools README](../old-tools/README.md).

---

## Step 3 — Import the stations to a map

Upload the `.kml` to **Google My Maps** at <https://mymaps.google.com>:

1. *Create a new map* → *Import* → drop the `.kml`.
2. Each station becomes a pin in a single map layer named after `--name`. The whole layer can be deleted in one click after the game is over.
3. Share the map with both teams so seekers and the hider can reference it during play.

Google Earth, OsmAnd, GAIA, and QGIS also read the file natively if you'd rather use one of those.

---

## Step 4 — Confirm the game size

Look at the stderr summary from Step 2 — it prints the inferred game size and the area chain (e.g. `Game size: M (inferred from area (330 km² gross − 2 km² water = 329 km² net))`). Double-check the S/M/L tier matches your map's footprint and the time you have. The same tier drives both the cluster radius the tool used and the in-game hiding-zone radius (¼ mile for S/M, ½ mile for L). If the inference is wrong (e.g. the tool couldn't subtract water for a coastal polygon and over-estimated area), re-run Step 2 with an explicit `--game-size`.

The wait-time tiers in the tool's output (dense / moderate / sparse) are independent of game size — they reflect local POI density at each station, not the size of the game.

---

## Step 5 — Pre-validate the Investigation Book

Skim the Investigation Book questions and pre-mark any whose subjects don't exist in your area — most commonly "transit line," "high-speed train line," "rail station," or "station-name length" in rural play. Treat those as missing subjects during the game, the same way the official rulebook handles any subject your map doesn't have.

Commercial airports, museums, libraries, hospitals, and similar subjects often *do* exist in rural game areas. Don't pre-cull questions that *might* find a match.

---

## Step 6 — Play

Follow the official Hide + Seek rulebook for everything except seeker / hider transportation, which uses the rules in [`rules.md`](./rules.md). The hiding zone is centered on a vehicle station; everything else (deck, Investigation Book, end-game trigger, found condition, scoring) plays as printed.
