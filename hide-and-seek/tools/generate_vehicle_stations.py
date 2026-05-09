"""Generate vehicle-station coordinates for a rural Hide+Seek game.

Given a polygon of geographic coordinates, queries OpenStreetMap (via the
Overpass API) for points of interest, enforces a 400m minimum spacing
between chosen stations (per the transit-friction research notes), and
derives a per-station wait-time range based on local POI density.

Output: CSV at hide-and-seek/tools/.output/{name}-{timestamp}.csv

Usage (from the repo root):
    uv run vehicle-stations --polygon-file path/to/polygon.geojson --name my-game

Or run the script directly:
    uv run python hide-and-seek/tools/generate_vehicle_stations.py \\
        --polygon-file path/to/polygon.geojson --name my-game

Polygon input formats:
    GeoJSON     — Feature, FeatureCollection, Polygon, MultiPolygon, or
                  LineString geometry. Uses the outer ring of the first
                  polygonal geometry found. (LineString is accepted because
                  geojson.io's line tool exports drawn shapes as LineString
                  even when the user closed the loop visually.)
    Plain text  — one "lat,lon" per line, blank lines and #-comments ok.

Sample polygons:
    See hide-and-seek/tools/geojson-samples/ for example inputs.

Drawing a polygon on a map and exporting as GeoJSON:
    https://geojson.io       — easiest. Click the polygon tool, draw the
                               outline, then "Save → GeoJSON" downloads
                               a .geojson file you can pass directly to
                               --polygon-file.
    https://felt.com         — Felt; draw a polygon and export as GeoJSON.
    Google My Maps           — works but exports as KML; convert to
                               GeoJSON first (e.g. with `mapshaper.org`
                               or `togeojson`).
    QGIS                     — desktop GIS; overkill for casual use but
                               supports any input/output format.

The wait-time tiers and category priorities used here are the
starting-point values from hide-and-seek/reference/transit-friction.md.
They are tunable via the constants near the top of this file.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "rural-jet-lag/generate_vehicle_stations (github: rural-jet-lag)"
OVERPASS_TIMEOUT_SEC = 90
MIN_STATION_SPACING_M = 400
DENSITY_RADIUS_M = 1609  # 1 mile

# Category priority — lower number wins when two POIs are within MIN_STATION_SPACING_M.
# (priority, osm_key, osm_value, label)
POI_CATEGORIES: list[tuple[int, str, str, str]] = [
    (1, "tourism", "museum", "museum"),
    (1, "tourism", "attraction", "attraction"),
    (2, "leisure", "park", "park"),
    (2, "leisure", "nature_reserve", "nature_reserve"),
    (2, "boundary", "national_park", "national_park"),
    (3, "amenity", "bar", "bar"),
    (3, "amenity", "pub", "pub"),
    (4, "amenity", "restaurant", "restaurant"),
    (4, "amenity", "cafe", "cafe"),
    (5, "amenity", "fast_food", "fast_food"),
    (6, "amenity", "fuel", "gas_station"),
    (7, "shop", "convenience", "convenience_store"),
    (7, "shop", "supermarket", "supermarket"),
    (8, "shop", "mall", "mall"),
    (8, "shop", "department_store", "department_store"),
]
LABEL_BY_KV = {(k, v): label for _, k, v, label in POI_CATEGORIES}
PRIORITY_BY_KV = {(k, v): p for p, k, v, _ in POI_CATEGORIES}


def wait_range_for_density(nearby_count: int) -> tuple[int, int, str]:
    """Wait-time range (min_minutes, max_minutes, tier) by local POI density.

    Tier breakpoints align with the transit-friction reference table
    (dense / moderate / sparse). Tunable.
    """
    if nearby_count >= 15:
        return 5, 15, "dense"
    if nearby_count >= 5:
        return 10, 30, "moderate"
    return 20, 60, "sparse"


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


@dataclass(frozen=True)
class POI:
    osm_id: int
    osm_type: str
    name: str
    category: str
    priority: int
    lat: float
    lon: float


def load_polygon(path: Path) -> list[tuple[float, float]]:
    """Return polygon outer ring as a list of (lat, lon) pairs (closed)."""
    text = path.read_text().strip()
    coords: list[tuple[float, float]]

    if path.suffix.lower() in (".geojson", ".json"):
        data = json.loads(text)
        ring = _extract_geojson_ring(data)
        # GeoJSON is [lon, lat]; we use (lat, lon).
        coords = [(lat, lon) for lon, lat in ring]
    else:
        coords = []
        for line in text.splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            lat_s, lon_s = (x.strip() for x in line.split(","))
            coords.append((float(lat_s), float(lon_s)))

    if len(coords) < 3:
        raise ValueError(f"polygon must have at least 3 points, got {len(coords)}")
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords


def _extract_geojson_ring(data: dict) -> list[list[float]]:
    """Walk a GeoJSON object and return the outer ring of the first polygonal geometry.

    Accepts Polygon, MultiPolygon, and LineString. LineString is allowed because
    geojson.io's line tool exports drawn shapes as LineString rather than Polygon
    even when the user closed the loop visually.
    """
    if data.get("type") == "FeatureCollection":
        for feat in data.get("features", []):
            try:
                return _extract_geojson_ring(feat)
            except ValueError:
                continue
        raise ValueError("no usable geometry found in FeatureCollection")
    if data.get("type") == "Feature":
        return _extract_geojson_ring(data["geometry"])
    if data.get("type") == "Polygon":
        return data["coordinates"][0]
    if data.get("type") == "MultiPolygon":
        return data["coordinates"][0][0]
    if data.get("type") == "LineString":
        return data["coordinates"]
    raise ValueError(f"unsupported GeoJSON type: {data.get('type')}")


def build_overpass_query(polygon: list[tuple[float, float]]) -> str:
    poly_str = " ".join(f"{lat} {lon}" for lat, lon in polygon)
    parts: list[str] = []
    seen_filters: set[tuple[str, str]] = set()
    for _, key, value, _ in POI_CATEGORIES:
        if (key, value) in seen_filters:
            continue
        seen_filters.add((key, value))
        f = f'["{key}"="{value}"]'
        parts.append(f'  node{f}(poly:"{poly_str}");')
        parts.append(f'  way{f}(poly:"{poly_str}");')
        parts.append(f'  relation{f}(poly:"{poly_str}");')
    body = "\n".join(parts)
    return f"[out:json][timeout:{OVERPASS_TIMEOUT_SEC}];\n(\n{body}\n);\nout center tags;"


def query_overpass(query: str) -> list[dict]:
    headers = {"User-Agent": USER_AGENT}
    r = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers=headers,
        timeout=OVERPASS_TIMEOUT_SEC + 10,
    )
    r.raise_for_status()
    return r.json().get("elements", [])


def parse_pois(elements: list[dict]) -> list[POI]:
    pois: list[POI] = []
    seen: set[tuple[str, int]] = set()
    for el in elements:
        osm_type = el.get("type")
        osm_id = el.get("id")
        if osm_id is None or (osm_type, osm_id) in seen:
            continue
        seen.add((osm_type, osm_id))

        if osm_type == "node":
            lat, lon = el.get("lat"), el.get("lon")
        else:  # way / relation — Overpass `out center` returns center coords
            center = el.get("center") or {}
            lat, lon = center.get("lat"), center.get("lon")
        if lat is None or lon is None:
            continue

        tags = el.get("tags", {})
        category, priority = _classify(tags)
        if category is None:
            continue
        name = tags.get("name") or f"unnamed {category}"
        pois.append(
            POI(
                osm_id=osm_id,
                osm_type=osm_type,
                name=name,
                category=category,
                priority=priority,
                lat=lat,
                lon=lon,
            )
        )
    return pois


def _classify(tags: dict) -> tuple[str | None, int]:
    """Return the (label, priority) for the highest-priority recognized tag."""
    best: tuple[int, str] | None = None
    for (key, value), label in LABEL_BY_KV.items():
        if tags.get(key) == value:
            p = PRIORITY_BY_KV[(key, value)]
            if best is None or p < best[0]:
                best = (p, label)
    if best is None:
        return None, 99
    return best[1], best[0]


def filter_min_spacing(pois: list[POI], min_m: float) -> list[POI]:
    ordered = sorted(pois, key=lambda p: (p.priority, p.name.lower()))
    kept: list[POI] = []
    for p in ordered:
        if all(haversine_m(p.lat, p.lon, k.lat, k.lon) >= min_m for k in kept):
            kept.append(p)
    return kept


def count_nearby(p: POI, candidates: list[POI], radius_m: float) -> int:
    return sum(
        1
        for c in candidates
        if (c.osm_type, c.osm_id) != (p.osm_type, p.osm_id)
        and haversine_m(p.lat, p.lon, c.lat, c.lon) <= radius_m
    )


def write_csv(out_path: Path, rows: list[dict]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "name",
        "category",
        "latitude",
        "longitude",
        "wait_min_minutes",
        "wait_max_minutes",
        "density_tier",
        "nearby_poi_count",
        "osm_type",
        "osm_id",
    ]
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--polygon-file", type=Path, required=True,
                    help="GeoJSON or plain-text polygon (lat,lon per line)")
    ap.add_argument("--name", type=str, default="game-area",
                    help="Output filename stem (default: game-area)")
    ap.add_argument("--min-spacing-m", type=float, default=MIN_STATION_SPACING_M,
                    help=f"Minimum spacing between stations in meters (default: {MIN_STATION_SPACING_M})")
    ap.add_argument("--density-radius-m", type=float, default=DENSITY_RADIUS_M,
                    help=f"Radius for local POI density count (default: {DENSITY_RADIUS_M})")
    args = ap.parse_args()

    polygon = load_polygon(args.polygon_file)
    print(f"Polygon: {len(polygon) - 1} unique points", file=sys.stderr)

    query = build_overpass_query(polygon)
    print("Querying Overpass…", file=sys.stderr)
    t0 = time.time()
    elements = query_overpass(query)
    print(f"Got {len(elements)} elements in {time.time() - t0:.1f}s", file=sys.stderr)

    candidates = parse_pois(elements)
    print(f"Recognized {len(candidates)} POIs", file=sys.stderr)
    if not candidates:
        print("No POIs found — check the polygon and tag list.", file=sys.stderr)
        return 1

    stations = filter_min_spacing(candidates, args.min_spacing_m)
    print(
        f"Selected {len(stations)} stations after {args.min_spacing_m:.0f}m spacing filter",
        file=sys.stderr,
    )

    rows: list[dict] = []
    for st in stations:
        nearby = count_nearby(st, candidates, args.density_radius_m)
        wmin, wmax, tier = wait_range_for_density(nearby)
        rows.append(
            {
                "name": st.name,
                "category": st.category,
                "latitude": f"{st.lat:.6f}",
                "longitude": f"{st.lon:.6f}",
                "wait_min_minutes": wmin,
                "wait_max_minutes": wmax,
                "density_tier": tier,
                "nearby_poi_count": nearby,
                "osm_type": st.osm_type,
                "osm_id": st.osm_id,
            }
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(__file__).resolve().parent / ".output"
    out_path = out_dir / f"{args.name}-{timestamp}.csv"
    write_csv(out_path, rows)
    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
