# Tools — Rural Hide and Seek

This directory will contain scripts and utilities to help set up and run a Rural Hide and Seek game.

---

## Tools

### `generate_vehicle_stations.py`

Given a polygon of geographic coordinates, queries OpenStreetMap (via the Overpass API) for points of interest, enforces a 400m minimum spacing between selected stations (per the [transit-friction research notes](../reference/transit-friction.md)), and derives a per-station wait-time range based on local POI density.

**Usage** (from the repo root):

```bash
uv run vehicle-stations --polygon-file path/to/polygon.geojson --name my-game
```

Or invoke the script directly:

```bash
uv run python hide-and-seek/tools/generate_vehicle_stations.py \
  --polygon-file path/to/polygon.geojson --name my-game
```

Polygon input: GeoJSON (Feature / FeatureCollection / bare Polygon — uses the first polygon's outer ring) or plain-text (one `lat,lon` per line, blank lines and `#` comments allowed).

To draw a polygon on a map and export it as GeoJSON, the easiest option is **[geojson.io](https://geojson.io)** — pick the polygon tool, draw the outline, then `Save → GeoJSON` downloads a file you can pass directly to `--polygon-file`. Alternatives: **[felt.com](https://felt.com)** (modern web mapping), **Google My Maps** (exports KML — convert to GeoJSON via [mapshaper.org](https://mapshaper.org) or `togeojson`), or **QGIS** (desktop GIS, overkill for casual use).

For ready-to-run example inputs, see [`geojson-samples/`](./geojson-samples/) — a small-town polygon and a city-scale polygon, both drawn in geojson.io.

**Output:** CSV at `hide-and-seek/tools/.output/{name}-{timestamp}.csv` with one row per chosen station — name, category, lat/lon, wait-time range in minutes, density tier (dense / moderate / sparse), nearby-POI count, OSM type/id. The `.output/` folder is gitignored.

POI categories considered (in priority order — earlier categories beat later ones when two POIs are within the 400m spacing window): museums and tourist attractions; parks, nature reserves, and national parks; bars and pubs; restaurants and cafés; fast food; gas stations; convenience stores and supermarkets; malls and department stores. Categories and priorities are defined as constants near the top of the script.

Wait-time tier breakpoints (also tunable in the script) match the table in `transit-friction.md`: ≥15 nearby POIs → dense (5–15 min), 5–14 → moderate (10–30), 0–4 → sparse (20–60). The local-density radius is 1 mile.

**Etiquette:** the Overpass API is a free public service — be polite. Don't run this against giant polygons in tight loops. Set a meaningful `User-Agent` (the script does this).

<!-- TODO: Add map generation, investigation book helpers, or other game utilities here. -->

---

## Requirements

Python dependencies for all tools in this project are managed by the root [`pyproject.toml`](../../pyproject.toml) using [uv](https://github.com/astral-sh/uv).

---

## External Tools & Resources

- **[OpenRouteService Isochrones](https://maps.openrouteservice.org/)** — Web interface for generating isochrones without code.
- **[Google My Maps](https://mymaps.google.com/)** — Draw and share custom play area boundaries.
- **[Gaia GPS](https://www.gaiagps.com/)** — Offline maps; great for rural areas with poor cell service.

---

## License

Code in this directory is licensed under the [MIT License](../../LICENSE).
