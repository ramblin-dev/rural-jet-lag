"""Generate vehicle-station coordinates for a rural Jet Lag game.

Game-agnostic — produces the station map that the cars-as-trains framing
in /vehicle-stations.md needs, regardless of which Jet Lag format is
being adapted (Hide + Seek, Tag, etc.).

Given a polygon of geographic coordinates, queries OpenStreetMap (via the
Overpass API) for points of interest, applies a two-tier spacing filter
(close-together stations within a cluster, larger gaps between clusters),
and derives a per-station wait-time range based on local POI density.

Spacing has two parameters, both grounded in the transit-friction research:
    --min-station-spacing-m  intra-cluster (default 300m, avg local bus)
    --min-cluster-spacing-m  inter-cluster (default 1000m, avg metro/LRT)

Two POIs end up in the same cluster iff they're closer than the cluster
spacing or chained through other in-cluster POIs. The result is groups of
stations on the map separated by visible gaps, mirroring how transit stops
appear in real cities — bus-stop-spaced clusters around towns, with metro-
scale gaps between them.

Outputs (both written to tools/.output/{name}-{timestamp}.{ext}):
    .csv  — one row per station for spreadsheets / scripting.
    .kml  — one Folder of placemarks named after --name, ready to upload
            to Google My Maps (creates one layer that can be deleted as a
            unit), Google Earth, OsmAnd, GAIA, or QGIS.

Usage (from the repo root):
    uv run vehicle-stations --polygon-file path/to/polygon.geojson --name my-game

Or run the script directly:
    uv run python tools/generate_vehicle_stations.py \\
        --polygon-file path/to/polygon.geojson --name my-game

Polygon input formats:
    GeoJSON     — Feature, FeatureCollection, Polygon, MultiPolygon, or
                  LineString geometry. Uses the outer ring of the first
                  polygonal geometry found. (LineString is accepted because
                  geojson.io's line tool exports drawn shapes as LineString
                  even when the user closed the loop visually.)
    Plain text  — one "lat,lon" per line, blank lines and #-comments ok.

Sample polygons:
    See tools/geojson-samples/ for example inputs.

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
from xml.sax.saxutils import escape as xml_escape

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "rural-jet-lag/generate_vehicle_stations (github: rural-jet-lag)"
OVERPASS_TIMEOUT_SEC = 90
# Two-tier spacing — see /vehicle-stations.md and hide-and-seek/reference/transit-friction.md.
MIN_STATION_SPACING_M = 300   # within a cluster; average local urban bus stop spacing
MIN_CLUSTER_SPACING_M = 1000  # between clusters; average light-rail / metro spacing
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


def filter_two_tier(
    pois: list[POI], min_station_m: float, min_cluster_m: float
) -> list[tuple[POI, int]]:
    """Two-tier spacing filter.

    Step 1 — group POIs into connected components using ``min_cluster_m`` as
    the link threshold. Two POIs end up in the same cluster iff there is a
    chain of POIs between them where every consecutive pair is closer than
    ``min_cluster_m``. As a consequence, every cross-cluster pair is at
    least ``min_cluster_m`` apart.

    Step 2 — within each cluster, greedy-filter to ``min_station_m`` minimum
    spacing, sorting by category priority so museums beat cafés when they
    conflict.

    Returns a list of (POI, cluster_id) pairs. Cluster IDs are assigned in
    the order clusters first appear in the input list, starting at 1.
    """
    n = len(pois)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(n):
        for j in range(i + 1, n):
            if haversine_m(pois[i].lat, pois[i].lon, pois[j].lat, pois[j].lon) < min_cluster_m:
                union(i, j)

    cluster_id_of_root: dict[int, int] = {}
    next_id = 1
    cluster_members: dict[int, list[POI]] = {}
    for i, p in enumerate(pois):
        root = find(i)
        if root not in cluster_id_of_root:
            cluster_id_of_root[root] = next_id
            next_id += 1
        cid = cluster_id_of_root[root]
        cluster_members.setdefault(cid, []).append(p)

    out: list[tuple[POI, int]] = []
    for cid in sorted(cluster_members):
        ordered = sorted(cluster_members[cid], key=lambda p: (p.priority, p.name.lower()))
        kept: list[POI] = []
        for p in ordered:
            if all(haversine_m(p.lat, p.lon, k.lat, k.lon) >= min_station_m for k in kept):
                kept.append(p)
        out.extend((p, cid) for p in kept)
    return out


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
        "cluster_id",
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


def write_kml(out_path: Path, layer_name: str, rows: list[dict]) -> None:
    """Write a KML file with all stations in a single Folder.

    Google My Maps imports the file as one map layer named ``layer_name``,
    which the user can delete in one click to remove all pins. Google Earth,
    OsmAnd, GAIA, and QGIS also read the file natively.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    placemarks = []
    for r in rows:
        desc = (
            f"Category: {r['category']}\n"
            f"Cluster: {r['cluster_id']}\n"
            f"Wait time: {r['wait_min_minutes']}–{r['wait_max_minutes']} min "
            f"({r['density_tier']})\n"
            f"Nearby POI count: {r['nearby_poi_count']}\n"
            f"OSM: {r['osm_type']} {r['osm_id']}"
        )
        placemarks.append(
            "      <Placemark>\n"
            f"        <name>{xml_escape(str(r['name']))}</name>\n"
            f"        <description>{xml_escape(desc)}</description>\n"
            f"        <Point><coordinates>{r['longitude']},{r['latitude']},0</coordinates></Point>\n"
            "      </Placemark>"
        )
    body = "\n".join(placemarks)
    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "  <Document>\n"
        f"    <name>{xml_escape(layer_name)}</name>\n"
        f"    <description>Generated by rural-jet-lag vehicle-stations at "
        f"{generated_at}. {len(rows)} stations.</description>\n"
        "    <Folder>\n"
        f"      <name>{xml_escape(layer_name)}</name>\n"
        f"{body}\n"
        "    </Folder>\n"
        "  </Document>\n"
        "</kml>\n"
    )
    out_path.write_text(kml, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--polygon-file", type=Path, required=True,
                    help="GeoJSON or plain-text polygon (lat,lon per line)")
    ap.add_argument("--name", type=str, default="game-area",
                    help="Output filename stem (default: game-area)")
    ap.add_argument("--min-station-spacing-m", type=float, default=MIN_STATION_SPACING_M,
                    help=f"Minimum spacing between stations within a cluster, in meters "
                         f"(default: {MIN_STATION_SPACING_M} — average local urban bus stop spacing)")
    ap.add_argument("--min-cluster-spacing-m", type=float, default=MIN_CLUSTER_SPACING_M,
                    help=f"Minimum spacing between clusters, in meters (also the threshold for "
                         f"cluster membership — POIs closer than this are linked into the same "
                         f"cluster). Default: {MIN_CLUSTER_SPACING_M} — average light-rail / metro spacing.")
    ap.add_argument("--density-radius-m", type=float, default=DENSITY_RADIUS_M,
                    help=f"Radius for local POI density count (default: {DENSITY_RADIUS_M})")
    args = ap.parse_args()

    if args.min_cluster_spacing_m <= args.min_station_spacing_m:
        ap.error("--min-cluster-spacing-m must be greater than --min-station-spacing-m")

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

    stations_with_cluster = filter_two_tier(
        candidates, args.min_station_spacing_m, args.min_cluster_spacing_m
    )
    cluster_count = len({cid for _, cid in stations_with_cluster})
    print(
        f"Selected {len(stations_with_cluster)} stations across {cluster_count} clusters "
        f"(intra-cluster ≥ {args.min_station_spacing_m:.0f}m, "
        f"inter-cluster ≥ {args.min_cluster_spacing_m:.0f}m)",
        file=sys.stderr,
    )

    rows: list[dict] = []
    for st, cid in stations_with_cluster:
        nearby = count_nearby(st, candidates, args.density_radius_m)
        wmin, wmax, tier = wait_range_for_density(nearby)
        rows.append(
            {
                "name": st.name,
                "category": st.category,
                "cluster_id": cid,
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
    stem = f"{args.name}-{timestamp}"
    csv_path = out_dir / f"{stem}.csv"
    kml_path = out_dir / f"{stem}.kml"
    write_csv(csv_path, rows)
    write_kml(kml_path, args.name, rows)
    print(f"Wrote {csv_path}", file=sys.stderr)
    print(f"Wrote {kml_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
