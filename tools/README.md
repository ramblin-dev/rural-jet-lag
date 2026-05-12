# Tools — cross-game utilities

Utilities shared across all rural Jet Lag formats. Game-specific tools live under `<game>/tools/` (e.g. [`hide-and-seek/tools/`](../hide-and-seek/tools/)).

For the *gameplay mechanic* these tools support — what vehicle stations are, how they replace bus/train lines, and how the departure roll works — see [`/vehicle-stations.md`](../vehicle-stations.md). This README covers tool usage only.

---

## `generate_vehicle_stations.py`

Given a polygon of geographic coordinates, queries OpenStreetMap (via the Overpass API) for points of interest, applies a two-tier spacing filter, and derives a per-station wait-time range based on local POI density. Game-agnostic — the output is a station map any rural Jet Lag format can use.

**Game-size inference** (the recommended path — zero flags needed):

If you pass none of `--game-size`, `--cluster-radius-m`, or `--max-stations-per-cluster`, the tool:

1. Computes the polygon area (subtracting OSM water bodies by default — pass `--no-water-subtract` to skip the extra Overpass call, or `--subtract-polygon FILE` to also remove other land you're excluding like a closed military range).
2. Bins that area into the rulebook's S/M/L map-size tiers (from "Choosing a Transit System": S ≤ 100 sq mi / 259 km²; M 100–1000 sq mi / 259–2590 km²; L 1000+ sq mi / 2590+ km²).
3. Sets `--cluster-radius-m` to the corresponding official hiding-zone radius (¼ mile for S/M, ½ mile for L).
4. Auto-tunes `--max-stations-per-cluster` to land the station count inside the rulebook's S/M/L station band (S 30–100, M 100–500, L 500+ — the L band only lower-bounds).

The stderr summary prints every step of the inference chain so it's auditable per run:

```
Polygon: 8 unique points
Water polygons fetched: 296
Game size: M (inferred from area (330 km² gross − 2 km² water = 329 km² net))
Cluster radius: 402m (game-size M)
...
Selected 182 stations across 182 clusters (..., cap 1/cluster (auto-tuned for game-size M (target 100–500 stations, swept 1..1)))
```

**Manual overrides** — any of these wins over inference, others stay auto:

- `--game-size {S,M,L}` (also accepts `small`/`medium`/`large`) — skip the area-bin step; use the official hiding-zone radius for that size (S/M → 402m / ¼ mile; L → 805m / ½ mile) and auto-tune cap to that size's station band.
- `--cluster-radius-m` — skip both the area-bin step (for radius) and the game-size mapping; use this value directly. Clustering uses **seed-and-grow**: pick the highest-priority unassigned POI as a seed, absorb every unassigned POI within `cluster-radius-m`, repeat until everything is assigned. This avoids single-linkage chaining — in a dense commercial corridor, two distinct real-world nodes (say, a mall and a downtown 3km apart, connected by a strip of cafés) stay as separate clusters instead of collapsing into one giant cluster.
- `--max-stations-per-cluster` — skip cap auto-tuning; use this value. Pass `0` to disable the cap entirely. (Default when nothing is inferable and this is unset: 4, anchored to empirical urban bus-stop density — see [`transit-friction.md`](../hide-and-seek/reference/transit-friction.md#stops-per-area-density-and-the-per-cluster-cap).)
- `--min-station-spacing-m` — within-cluster minimum spacing between kept stations, default **300m** (average local urban bus stop spacing). Not affected by `--game-size`.

**Real public-transit stations (always included by default):**

If the play area happens to contain real bus terminals, train stations, tram stops, ferry terminals, or other public-transit stations, the tool pulls them in alongside the generated POI stations. The rural cars-as-trains layer is meant to coexist with real transit, not displace it. Behavior:

- **Tags included** (priority 0, above all POI tiers): `railway=station`, `railway=halt`, `railway=tram_stop`, `amenity=bus_station`, `amenity=ferry_terminal`, `aerialway=station`, `public_transport=station`. Individual `highway=bus_stop` flag-stops are intentionally skipped — they'd flood urban output without adding game-meaningful meeting points.
- **Exempt from the per-cluster cap.** Real transit is additive: a downtown cluster capped at 4 POI stations can still gain its real bus terminal on top. Auto-tune still works — the total (POI + transit) is what's compared against the rulebook band.
- **Exempt from the closed-hours penalty.** Transit stations function as meeting points even when ticket-office hours are constrained; their `opening_hours` tag (if present) usually refers to the terminal building, not platform access.
- **Subject to the 300m intra-cluster spacing filter** so two transit stations within walking distance of each other get deduplicated to one pin.
- `--no-include-transit-stations` skips them entirely.

**Playing-hours check:**

- `--playing-hours` — time-of-day window during which the game will be played, default **`7am-7pm`**. Accepts `7am-7pm`, `7:30am-7:30pm`, `07:00-19:00`, etc.
- `--playing-days-of-week` — comma-delimited weekdays the game will run, default **`sat,sun`**. Accepts `sat,sun`, `Mon,Wed,Fri`, OSM-style `Mo,We,Fr`, full names like `saturday,sunday`.

POIs whose OSM `opening_hours` tag indicates they're closed throughout the entire playing window get a flat priority penalty (`+100`) so any open place wins over any closed place in the same base category, but closed places still appear if there's nothing better nearby. POIs without an `opening_hours` tag, or with a tag that doesn't parse, are treated as "unknown" and get no penalty (real-world OSM data is patchy; the user can verify in person). The CSV output includes `open_during_play` (`yes` / `no` / `unknown`) and the raw `opening_hours` string for transparency.

**Debug mode — investigating sparse clusters:**

- `--debug-candidates` — print one line per candidate POI to stdout in shell-style `key=value` format. Both kept and rejected stations appear; rejected lines include `reason=spacing|cluster_cap` and (for spacing) `conflict_with=<name>` showing which kept station blocked them. Status messages stay on stderr so the output streams cleanly into grep.

Use it when a cluster has fewer stations than you'd expect and you want to know whether the cause is OSM coverage or the spacing/cap filters:

```bash
# See everything that ended up in cluster 5 (kept + rejected with reasons).
uv run vehicle-stations --polygon-file area.geojson --debug-candidates 2>/dev/null | grep cluster=5

# Just the rejections.
uv run vehicle-stations --polygon-file area.geojson --debug-candidates 2>/dev/null | grep kept=no

# How many candidates the 300m spacing filter dropped.
uv run vehicle-stations --polygon-file area.geojson --debug-candidates 2>/dev/null | grep reason=spacing | wc -l
```

To independently sanity-check against the OSM source (no filtering at all), paste your polygon into [overpass-turbo.eu](https://overpass-turbo.eu) and run a raw category query — that's the upstream truth, and any difference between it and this tool's debug output is something this script did.

The result: groups of stations with bus-spaced internals around meaningful seed POIs (the highest-priority destination in each cluster), separated by walking-radius-scale gaps, mirroring how transit stops appear in real cities — clusters around towns and commercial areas, with quiet stretches between.

**Usage** (from the repo root):

```bash
uv run vehicle-stations --polygon-file path/to/polygon.geojson --name my-game
```

Or invoke the script directly:

```bash
uv run python tools/generate_vehicle_stations.py \
  --polygon-file path/to/polygon.geojson --name my-game
```

Polygon input: GeoJSON (Feature / FeatureCollection / bare Polygon — uses the first polygon's outer ring) or plain-text (one `lat,lon` per line, blank lines and `#` comments allowed).

To draw a polygon on a map and export it as GeoJSON, the easiest option is **[geojson.io](https://geojson.io)** — pick the polygon tool, draw the outline, then `Save → GeoJSON` downloads a file you can pass directly to `--polygon-file`. Alternatives: **[felt.com](https://felt.com)** (modern web mapping), **Google My Maps** (exports KML — convert to GeoJSON via [mapshaper.org](https://mapshaper.org) or `togeojson`), or **QGIS** (desktop GIS, overkill for casual use).

For ready-to-run example inputs, see [`geojson-samples/`](./geojson-samples/) — a small-town polygon and a city-scale polygon, both drawn in geojson.io.

**Outputs:** two files at `tools/.output/{name}-{timestamp}.{csv,kml}` (the `.output/` folder is gitignored):

- `.csv` — one row per chosen station: name, category, cluster id, lat/lon, wait-time range in minutes, density tier (dense / moderate / sparse), nearby-POI count, OSM type/id. Best for spreadsheets and follow-up scripting; group by `cluster_id` to inspect clusters.
- `.kml` — placemarks grouped under a single Folder named after `--name`. Upload to **Google My Maps** ([mymaps.google.com](https://mymaps.google.com) → "Create a new map" → "Import" → drop the file) to get all stations as a single map layer that can be deleted in one click. Google Earth, OsmAnd, GAIA, and QGIS also read the file natively.

POI categories considered, in priority order — earlier categories beat later ones when two POIs are within the spacing window. Priority bands favor places that are free, low-cost, and welcoming to either brief or extended visits:

1. **Low-cost cultural and browseable retail** — museums, tourist attractions, bookstores, comic / manga shops (`shop=anime`), board game shops (`shop=games`).
2. **Cafés / coffee shops and arcades** — flexible-visit hangouts where a 5-minute stop or a 90-minute session both feel normal. `amenity=cafe` covers sit-down coffee shops, espresso bars, tea houses, and the like; `leisure=amusement_arcade` covers arcades.
3. **Free-to-browse retail** — malls, department stores.
4. **Free, comfortable to linger** — parks, nature reserves, national parks, highway rest areas / service plazas. Demoted from the top tier because OSM tags these densely — every neighborhood park and rest stop otherwise crowds out the more distinctive cultural categories above. Still valuable when nothing else is nearby.
5. **In-and-out essentials** — convenience stores, supermarkets, gas stations, fast food.
6. **Bars and pubs** — welcoming to linger but with a purchase commitment, and often closed during daytime play.
7. **Restaurants** — the natural visit shape ("buy a meal, eat through it, leave") fits neither the in-and-out nor the comfortable-linger pattern, so they're last-resort fallback stations.

Categories and priorities are defined as constants near the top of the script and are easy to tweak.

Wait-time tier breakpoints (also tunable in the script) match the table in [`transit-friction.md`](../hide-and-seek/reference/transit-friction.md): ≥15 nearby POIs → dense (5–15 min), 5–14 → moderate (10–30), 0–4 → sparse (20–60). The local-density radius is 1 mile.

**Etiquette:** the Overpass API is a free public service — be polite. Don't run this against giant polygons in tight loops. Set a meaningful `User-Agent` (the script does this).

---

## Requirements

Python dependencies for all tools in this project are managed by the root [`pyproject.toml`](../pyproject.toml) using [uv](https://github.com/astral-sh/uv).

---

## External tools & resources

- **[OpenRouteService Isochrones](https://maps.openrouteservice.org/)** — Web interface for generating isochrones without code.
- **[Google My Maps](https://mymaps.google.com/)** — Draw and share custom play area boundaries.
- **[Gaia GPS](https://www.gaiagps.com/)** — Offline maps; great for rural areas with poor cell service.

---

## License

Code in this directory is licensed under the [MIT License](../LICENSE).
