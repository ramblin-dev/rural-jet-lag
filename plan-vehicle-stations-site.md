# Plan — Vehicle-stations static site + JS rewrite

Replace the Python `vehicle-stations` tool with a JS implementation that powers both a CLI and a static site, while keeping behavioral parity with the existing Python tool through a snapshotted-Overpass parity test.

## Goals

1. A static site where you draw a play-area polygon on a map, vehicle stations generate automatically, a sidebar lets you tweak settings, and a download button hands you a KML + instructions to upload to mymaps.google.com.
2. A JS CLI that produces the same CSV/KML outputs the Python tool produces today.
3. Maximum code reuse between the site and CLI (shared `core/`).
4. A parity test that pins the JS implementation against the Python implementation using a frozen Overpass response, so algorithm drift fails CI but OSM drift doesn't.

## Non-goals

- Pyodide / WASM / Rust core. Rejected during planning: the algorithmic core is ~200 lines, the I/O glue (~900 lines) is per-platform anyway, and the FFI/build-toolchain tax exceeds the savings.
- Keeping the Python tool long-term. It survives only as `old-tools/` during the transition and gets deleted in a cleanup commit after parity is established and docs are rewritten.

## Architecture

- **`tools/core/`** — pure JS, isomorphic (no Node-only or browser-only APIs). Owns clustering, spacing filter, cap auto-tune, wait-range tiers, area calc / projection (accepts a **list** of exclusion polygons — CLI passes `[oneFile]`, site passes the drawn array), Overpass query construction, POI parsing, KML rendering. Plain JS + JSDoc types.
- **`tools/cli/`** — Node-only. Owns argparse, filesystem I/O, fetch-to-Overpass, output paths, stderr status logging. Thin wrapper around `core/`.
- **`tools/site/`** — Browser-only. Vite app. Leaflet + Leaflet-draw for the map, sidebar form bound to settings, localStorage for polygon + settings + cached Overpass response, KML download button, mymaps upload instructions.
- **Runtime:** Node (stable LTS). **Package manager:** npm. **Bundler:** Vite (site only; CLI ships as plain ESM). **Module system:** ESM throughout (`"type": "module"`). **Types:** plain JS + JSDoc.

## Parity-test design

- **Fixture:** one chosen sample polygon from the existing `tools/geojson-samples/` collection, picked to exercise clustering, the spacing filter, the per-cluster cap, water subtraction, and at least one real OSM transit station.
- **Overpass snapshot:** captured once during step 1, checked into the repo. Both Python and JS CLIs accept a `--overpass-fixture FILE` flag (or env var) that short-circuits the HTTP call and reads the saved JSON instead.
- **Baseline output:** Python CSV + KML from running the parity script once against the fixture, checked in alongside the snapshot. Output files use a `python-<prefix>-` name prefix.
- **JS test:** mirrors the Python test exactly, same fixture, same args, `js-<prefix>-` name prefix, diff'd against the Python baseline.
- **Normalization for diff:** strip the `generated_at` timestamp from KML before comparison; CSV row ordering is already deterministic (sorted by cluster id) so direct diff works.
- **Why the snapshot is checked in:** freezes Overpass at a known state so the test catches algorithm drift, not OSM drift. Without this the test is flaky forever.

## Site behavior

- **Regeneration trigger:** cache the Overpass response client-side (in localStorage, keyed by polygon hash). Polygon edit → one Overpass call → response cached. Sidebar setting changes re-run only the clustering/spacing/cap step (instant, no network). No explicit "regenerate" button; results just update.
- **Exclusion polygons:** the site supports drawing **any number** of exclusion polygons in addition to the play-area polygon. A sidebar toggle ("Drawing: play area | exclusion zone") chooses which layer the next draw targets. Exclusion polygons render in a distinct color (e.g. red) so they're visually distinguishable from the play area (blue). Editing or adding an exclusion polygon does **not** invalidate the cached Overpass response — exclusions only feed the area calc + downstream clustering, which is cheap to re-run.
- **Reset:**
  - Deleting the play-area polygon (Leaflet-draw's built-in delete control) clears the drawn shape, all exclusion polygons, the cached Overpass response, and the generated stations. Settings persist.
  - Deleting an individual exclusion polygon leaves everything else alone; stations re-cluster against the updated exclusion set.
  - No separate trash button — relying on the draw tool's delete control is fewer lines.
- **localStorage contents:**
  - Drawn play-area polygon (GeoJSON)
  - Drawn exclusion polygons (GeoJSON, list)
  - Sidebar settings (all values)
  - Cached Overpass response (keyed by play-area polygon hash, invalidated on play-area edit)
  - Generated station list is *not* stored — recomputed on load from the cached response + settings (instant).
- **Download:** KML file with a filename the user chooses at save time via the browser's native save dialog. No `--name` setting in the site (the site doesn't need it because the user names the file at download).
- **Upload instructions:** short inline text + link explaining how to import the KML into mymaps.google.com as a new layer.

## Sidebar settings

Exposed (all Python CLI args except `--polygon-file`, `--name`, and `--debug-candidates`; the equivalent of `--subtract-polygon` is the on-map exclusion-polygon drawing described above, not a sidebar control):

- `min-station-spacing-m` — number, default 300
- `cluster-radius-m` — number, blank = auto from game-size
- `game-size` — S / M / L / auto
- `max-stations-per-cluster` — number, blank = auto-tune, 0 = no cap
- `density-radius-m` — number, default 1609
- `water-subtract` — checkbox, default on
- `include-transit-stations` — checkbox, default on
- `playing-hours` — text, default "7am-7pm"
- `playing-days-of-week` — text, default "sat,sun"

Group into "Auto-inferred (override if needed)" and "Tunable" sections so the user sees that the defaults are smart. The CLI keeps `--name` (CLI writes named output files); the site does not.

## Implementation phases (one commit each)

1. **Add the parity test infrastructure (Python side).** New `tools/parity-test/` with: a chosen sample polygon, a small Python test script that shells out to the current `vehicle-stations` CLI with fixed args and the `python-<prefix>-` name prefix, and a one-time capture of the Overpass response saved as a fixture. Run the script once, check in the baseline CSV/KML output plus the Overpass fixture. Add a `--overpass-fixture FILE` flag to the existing Python tool that short-circuits the HTTP call.

2. **Rename `tools/` to `old-tools/`.** `git mv tools/ old-tools/`. Update `pyproject.toml`: drop the `vehicle-stations` console script (or repoint it at `old-tools.generate_vehicle_stations:main` for the transition). Update internal doc links that point at `tools/...`. The repo still works; the parity baseline still runs from its new location.

3. **Scaffold the new JS workspace at `tools/`.** Root `package.json` with workspaces. `tools/core/`, `tools/cli/`, `tools/site/` skeletons. Vite config for the site. No logic yet — verify `npm install` and `npm run` work end-to-end.

4. **Port the algorithmic core to `tools/core/`.** Clustering (seed-and-grow), spacing filter, cap auto-tune, wait-range tiers, area calc + equirectangular projection, Overpass query construction, POI parsing, opening-hours evaluation, KML rendering. Plain JS + JSDoc types. No CLI or site wiring yet.

5. **Wire `tools/cli/` + run the parity test.** argparse equivalent (mirror the Python flags), filesystem I/O, fetch-to-Overpass with `--overpass-fixture FILE` support, output to `.output/`. Add the JS-side parity test mirroring the Python one (same fixture, same args, `js-<prefix>-` name prefix). Run both; diff the outputs after normalizing the KML timestamp. Fix discrepancies until clean.

6. **Wire `tools/site/`.** Leaflet + Leaflet-draw map with a draw-mode toggle (play area vs exclusion zone) and distinct colors per layer. Sidebar form bound to settings, persisted to localStorage along with the play-area polygon and all exclusion polygons. Overpass call on play-area edit only, response cached in localStorage keyed by play-area polygon hash; exclusion edits skip the network and just re-cluster. Auto-regenerate stations when any setting or exclusion changes (instant, no network). Download button → KML via Blob. Inline upload-to-mymaps instructions. Manual smoke test: draw → generate → add exclusion → tweak settings → download → import into mymaps.

7. **(Cleanup, separate commit after parity holds and docs are rewritten.)** Delete `old-tools/`. Rewrite top-level README, `vehicle-stations.md`, `CONTRIBUTING.md`, and `CLAUDE.md` to describe the JS-based tooling. Drop any remaining Python-tool references.

## Known risks / open items

- **Opening-hours parsing in JS.** Python uses the `opening_hours` package (a Rust binding). The JS equivalent is `opening_hours.js` (mature, widely used in OSM tooling) — confirm during step 4 that it handles the same input shapes the Python lib does, since real OSM `opening_hours` tags are notoriously varied.
- **Geometry library.** Python uses `shapely`. JS equivalent for the area calc and polygon ops will be `@turf/turf` or hand-rolled (the equirectangular projection + `Polygon.area` is small enough to hand-roll, which avoids a heavy dep). Decide during step 4.
- **CORS on Overpass from the browser.** The public Overpass endpoint sets permissive CORS headers, so direct browser fetch should work — confirm during step 6, fall back to a different mirror if not.
- **Leaflet-draw's delete UX.** Need to confirm the built-in delete control gives a single-click reset experience clean enough to skip the dedicated trash button. If it's awkward, add the trash button (still small).
- **Auto-tune cap in the browser.** The Python tool sweeps cap values 1..12 by re-running `filter_two_tier` each time. In the browser this runs against the cached Overpass response so it's fast, but worth measuring on a large polygon to make sure it stays under ~100ms.
