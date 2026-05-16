# Parity test — Python vs JS

Pins the JS rewrite of `generate_vehicle_stations` against the original Python
implementation using a frozen Overpass response, so a parity-test failure
means an algorithmic drift between the two implementations — not OSM drift
between two runs.

## Files

- `polygon.geojson` — fixed play-area polygon (copy of the Sioux Falls metro
  sample, picked because it exercises clustering, the spacing filter, the
  per-cluster cap, water subtraction, and at least one real OSM transit
  station).
- `fixtures/pois.json` — snapshotted Overpass response for the POI query.
- `fixtures/water.json` — snapshotted Overpass response for the water-polygon
  query used by the area calc.
- `baseline/python-sioux.csv`, `baseline/python-sioux.kml` — frozen Python
  output for the fixture. The JS port targets byte-for-byte equality (modulo
  the normalized KML `generated_at`, which is forced to the literal string
  `"fixture"` when `--no-timestamp` is set).
- `run_python.py` — captures or re-runs the Python baseline.
- *(later)* `run_js.py` — mirrors `run_python.py` for the JS CLI.
- *(later)* `compare.py` — diffs `python-sioux.{csv,kml}` against
  `js-sioux.{csv,kml}`.

## Capturing / re-running the Python baseline

```bash
uv run python tools/parity-test/run_python.py
```

First run hits Overpass twice (POIs + water) and saves both responses into
`fixtures/`. Subsequent runs read from the fixtures and never touch the
network. To force a re-capture, delete `fixtures/*.json` and re-run.

## Why the Overpass snapshot is checked in

Overpass returns different data over time as OSM gets edited, and even
back-to-back runs can differ. Without a frozen snapshot, the parity diff
would conflate algorithm bugs with OSM drift and be flaky forever. The
checked-in snapshot is a feature, not a bug.
