# Parity / regression test

Frozen reference output for the vehicle-stations generator. The JS CLI runs
against checked-in Overpass snapshots and its output is diffed against a
blessed baseline per test case. A failure here means algorithmic drift in
the JS implementation — not OSM drift between two runs, because every
Overpass response is snapshotted.

## Layout

Each test case lives in `cases/<name>/`:

```
cases/<name>/
  polygon.geojson           # play-area polygon
  exclusion.geojson         # optional exclusion polygon (passed as --subtract-polygon)
  fixtures/
    pois.json               # frozen Overpass POI response
    water.json              # frozen Overpass water-polygon response
  baseline/
    expected.csv            # blessed reference CSV
    expected.kml            # blessed reference KML
```

## Cases

| Case | Polygon | Notable |
|---|---|---|
| `sioux` | Sioux Falls metro, ~330 km² | Exercises auto-tune, water subtraction, real OSM transit stations. Originally captured from the Python reference implementation that seeded the JS port. |
| `town-excl` | Dell Rapids, SD, ~33 km² | Small-town footprint with a hand-drawn exclusion polygon removing two POIs (Brown Memorial Park and County Fair Grocery) from the northern portion of town. Exercises the exclusion code path. |

## Running

```bash
cd stations-generator
npm run parity:js
```

Iterates every case, regenerates output into a tmp dir, diffs against the
case's `expected.{csv,kml}`. Exits non-zero on any drift.

## Adding a case

1. Create `cases/<new-name>/polygon.geojson` (and `exclusion.geojson` if
   you want one).
2. Run the CLI with `--overpass-fixture-dir cases/<new-name>/fixtures
   --output-dir cases/<new-name>/baseline --name expected --no-timestamp`
   (and `--subtract-polygon cases/<new-name>/exclusion.geojson` if applicable).
   The first run hits Overpass and saves both the fixture and the baseline.
3. Add the case to the `CASES` array in `stations-generator/cli/src/parity.js`.
4. Re-run `npm run parity:js` to confirm it passes.

## Updating a baseline

If you deliberately change algorithmic behavior in `stations-generator/core/`,
the diff will fail. To bless the new output for a case as the expected
baseline:

```bash
cd stations-generator
node cli/src/main.js \
  --polygon-file parity-test/cases/<case>/polygon.geojson \
  --overpass-fixture-dir parity-test/cases/<case>/fixtures \
  --output-dir parity-test/cases/<case>/baseline \
  --name expected --no-timestamp \
  --min-station-spacing-m 300 --density-radius-m 1609 \
  --playing-hours 7am-7pm --playing-days-of-week sat,sun
  # plus --subtract-polygon parity-test/cases/<case>/exclusion.geojson if the case has one
```

Commit the new baseline with a message explaining why the output changed.

## Why the Overpass snapshot is checked in

Overpass returns different data over time as OSM gets edited, and even
back-to-back runs can differ. Without a frozen snapshot, the parity diff
would conflate algorithm bugs with OSM drift and be flaky forever. The
checked-in snapshot is a feature, not a bug.
