# Parity / regression test

Frozen reference output for the vehicle-stations generator. The JS CLI runs
against a checked-in Overpass snapshot and its output is diffed against a
baseline that was originally captured from the Python reference
implementation (now removed; see git history at and before the deletion of
`old-tools/`).

A failure here means an algorithmic drift in the JS implementation — not
OSM drift between two runs, because the Overpass response is snapshotted.

## Files

- `polygon.geojson` — fixed Sioux Falls metro play area. Picked because it
  exercises clustering, the spacing filter, the per-cluster cap, water
  subtraction, and at least one real OSM transit station.
- `fixtures/pois.json` — snapshotted Overpass response for the POI query.
- `fixtures/water.json` — snapshotted Overpass response for the water-polygon
  query used by the area calc.
- `baseline/python-sioux.csv`, `baseline/python-sioux.kml` — frozen
  reference output. Named for the Python implementation that produced
  them; treated as the canonical expected output the JS port must match.

## Running the test

```bash
cd stations-generator
npm run parity:js
```

This runs the JS CLI against the fixture, writes `baseline/js-sioux.{csv,kml}`,
and diffs them against `baseline/python-sioux.{csv,kml}`. Exits non-zero on
any diff. The diff normalises the `--name` value (`python-sioux` vs
`js-sioux`) in the KML layer name; everything else must be byte-identical.

## Updating the baseline

If you deliberately change algorithmic behavior in `stations-generator/core/`, the diff
will fail. To bless the new output as the expected baseline:

```bash
cd stations-generator
npm run parity:js   # produces js-sioux.{csv,kml}
cp parity-test/baseline/js-sioux.csv parity-test/baseline/python-sioux.csv
cp parity-test/baseline/js-sioux.kml parity-test/baseline/python-sioux.kml
# Then in the new python-sioux.kml, change the two <name>js-sioux</name>
# occurrences back to <name>python-sioux</name> so the normaliser sees
# the python- prefix on the reference file.
```

Commit the new baseline with a message explaining why the output changed.

## Why the Overpass snapshot is checked in

Overpass returns different data over time as OSM gets edited, and even
back-to-back runs can differ. Without a frozen snapshot, the parity diff
would conflate algorithm bugs with OSM drift and be flaky forever. The
checked-in snapshot is a feature, not a bug.
