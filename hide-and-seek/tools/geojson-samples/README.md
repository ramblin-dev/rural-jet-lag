# GeoJSON sample polygons

Example inputs for [`generate_vehicle_stations.py`](../generate_vehicle_stations.py). Use them to test the tool or as starting points when you draw your own play area.

## Files

| File | Approx. center | Drawn area | Use case |
|------|----------------|------------|----------|
| [`town.geojson`](./town.geojson) | Dell Rapids, SD area (~43.82°N, 96.71°W) | Small-town footprint, ~7 km² | Sparse rural / small-town play |
| [`city.geojson`](./city.geojson) | Sioux Falls, SD area (~43.55°N, 96.70°W) | Larger metro footprint, ~250 km² | Mixed-density / city-scale play |

Both files were drawn in [geojson.io](https://geojson.io) and exported as `LineString` features. The tool accepts LineString as a polygon ring (auto-closing if needed) so geojson.io's line-tool exports work directly.

## Try it

```bash
uv run vehicle-stations \
  --polygon-file hide-and-seek/tools/geojson-samples/town.geojson \
  --name town-test
```

Output goes to `hide-and-seek/tools/.output/` (gitignored).
