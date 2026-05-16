"""Generate vehicle-station coordinates for a rural Jet Lag game.

Game-agnostic — produces the station map that the cars-as-trains framing
in /vehicle-stations.md needs, regardless of which Jet Lag format is
being adapted (Hide + Seek, Tag, etc.).

Given a polygon of geographic coordinates, queries OpenStreetMap (via the
Overpass API) for points of interest, clusters them by seed-and-grow with
a fixed radius, applies an intra-cluster spacing filter, and derives a
per-station wait-time range based on local POI density.

If you pass none of --game-size / --cluster-radius-m / --max-stations-per-cluster,
the tool auto-infers them from the polygon: it computes area (subtracting
OSM water polygons by default), bins into the rulebook's S/M/L tier, sets
the cluster radius to the official hiding-zone radius for that tier
(¼ mile for S/M, ½ mile for L), and auto-tunes the per-cluster cap so the
total station count lands inside the rulebook's S/M/L station band.

Real public-transit stations from OSM (train stations, tram stops, bus
stations, ferry terminals, etc.) are included alongside the generated POI
stations by default. They're exempt from the per-cluster cap (additive) and
from the closed-hours penalty (always-accessible meeting points). Pass
--no-include-transit-stations to skip them.

Manual overrides:
    --game-size {S,M,L}        skip area binning; use this tier
    --cluster-radius-m         skip game-size mapping; use this radius
    --max-stations-per-cluster skip cap auto-tuning; use this cap
    --min-station-spacing-m    within-cluster minimum (default 300m,
                               average local urban bus stop spacing)
    --no-water-subtract        skip the Overpass water query during area calc
    --subtract-polygon FILE    additional polygon to subtract from play area
    --no-include-transit-stations  skip real OSM transit stations entirely

Clusters are grown by repeatedly picking the highest-priority unassigned
POI as a seed and absorbing every unassigned POI within the cluster radius.
This avoids single-linkage chaining: two distinct real-world commercial
nodes connected by a strip of cafés stay as separate clusters, instead of
collapsing into one giant cluster as union-find would.

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
import shlex
import sys
import time as wall_time  # avoid collision with datetime.time
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import requests
from opening_hours import OpeningHours
from shapely.geometry import Polygon
from shapely.ops import unary_union

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "rural-jet-lag/generate_vehicle_stations (github: rural-jet-lag)"
OVERPASS_TIMEOUT_SEC = 90
# Spacing parameters — see /vehicle-stations.md and hide-and-seek/reference/transit-friction.md.
MIN_STATION_SPACING_M = 300   # within a cluster; average local urban bus stop spacing
CLUSTER_RADIUS_M = 1000       # max distance from a cluster's seed POI to any of its members
                              # (general default; --game-size overrides per official hiding-zone radii)
DENSITY_RADIUS_M = 1609  # 1 mile

# Hiding-zone radii from the official Hide + Seek home-game rulebook ("Hiding
# Zones" article): S/M = ¼ mile, L = ½ mile. Converted to whole meters.
# Used when --game-size is passed to make our cluster radius match the
# legal roaming area a hider has once they pick a station inside a cluster.
HIDING_ZONE_RADIUS_M_BY_GAME_SIZE = {
    "S": 402,  # ¼ mile = 402.336 m
    "M": 402,  # ¼ mile = 402.336 m
    "L": 805,  # ½ mile = 804.672 m
}
# Map-size area bands from the rulebook's "Choosing a Transit System" article.
# Imperial source figures: S = 10–100 sq mi, M = 100–1000 sq mi, L = 1000+ sq mi.
# Converted: 10 sq mi ≈ 26 km², 100 ≈ 259 km², 1000 ≈ 2590 km². Used to infer
# the game size from polygon area when --game-size is not set.
GAME_SIZE_AREA_FLOOR_KM2 = {
    "S": 0.0,
    "M": 259.0,   # 100 sq mi
    "L": 2590.0,  # 1000 sq mi
}
# Station-count bands from the same rulebook article (S/M closed range; L lower-bounded).
# Used to auto-tune --max-stations-per-cluster when neither --max-stations-per-cluster
# nor the cap is otherwise pinned.
GAME_SIZE_STATION_BANDS = {
    "S": (30, 100),
    "M": (100, 500),
    "L": (500, float("inf")),
}
# Cap values to sweep when auto-tuning. Caps are tiny ints; full linear search.
AUTO_TUNE_CAP_RANGE = range(1, 13)
# Per-cluster station cap. Anchored to empirical urban bus-stop density:
# Liu et al. 2022 report ~11 stops/km² as the Shanghai optimum for bus-metro
# transfer ridership; Liu et al. 2025 find a ~15 stops/km² diminishing-returns
# threshold in Beijing. Inside a 400m walking-access radius (≈ 0.5 km²) those
# translate to ~5–6 (optimum) and ~7–8 (saturation). A cap of 4 lands at the
# upper end of "typical urban" without modeling Shanghai/Beijing densities,
# which fits the rural variant's framing. See transit-friction.md for cites.
MAX_STATIONS_PER_CLUSTER = 4

# Playing-hours check. POIs whose OSM `opening_hours` tag indicates they're
# closed throughout the playing window get a flat priority penalty so any
# open place wins over any closed place in the same base category, but
# closed places still appear if there's nothing better nearby.
DEFAULT_PLAYING_HOURS = "7am-7pm"
DEFAULT_PLAYING_DAYS = "sat,sun"
CLOSED_PRIORITY_PENALTY = 100  # >> max base priority (7); closed always loses

DAY_NAME_TO_INT = {
    "mo": 0, "mon": 0, "monday": 0,
    "tu": 1, "tue": 1, "tues": 1, "tuesday": 1,
    "we": 2, "wed": 2, "weds": 2, "wednesday": 2,
    "th": 3, "thu": 3, "thurs": 3, "thursday": 3,
    "fr": 4, "fri": 4, "friday": 4,
    "sa": 5, "sat": 5, "saturday": 5,
    "su": 6, "sun": 6, "sunday": 6,
}

# Category priority — lower number wins when two POIs are within MIN_STATION_SPACING_M.
# Priority bands favor places that are free, low-cost, and welcoming to either
# brief or extended visits — which is what makes a station pleasant to wait at
# without committing to a meal or a bar tab.
# (priority, osm_key, osm_value, label)
POI_CATEGORIES: list[tuple[int, str, str, str]] = [
    # Tier 1: low-cost cultural / browseable retail.
    # `shop=anime` is the standard OSM tag for manga/anime shops, the closest
    # documented match for comic-book stores; many comic stores are tagged
    # `shop=books` instead and get picked up there.
    (1, "tourism", "museum", "museum"),
    (1, "tourism", "attraction", "attraction"),
    (1, "shop", "books", "bookstore"),
    (1, "shop", "anime", "comic_store"),
    (1, "shop", "games", "board_game_store"),
    # Tier 2: flexible-visit hangouts — small ongoing cost, but a 5-minute
    # stop or a 90-minute session both feel normal here.
    (2, "amenity", "cafe", "cafe"),
    (2, "leisure", "amusement_arcade", "arcade"),
    # Tier 3: free-to-browse retail with foot traffic.
    (3, "shop", "mall", "mall"),
    (3, "shop", "department_store", "department_store"),
    # Tier 4: free, comfortable to linger. Demoted from the top tier because
    # OSM has these tagged densely — every neighborhood park, picnic area,
    # and highway rest stop otherwise crowds out the more distinctive
    # cultural categories above.
    (4, "leisure", "park", "park"),
    (4, "leisure", "nature_reserve", "nature_reserve"),
    (4, "boundary", "national_park", "national_park"),
    (4, "highway", "rest_area", "rest_area"),
    (4, "highway", "services", "rest_area"),
    # Tier 5: in-and-out essentials (cheap, brief, no pressure to stay or buy much).
    (5, "shop", "convenience", "convenience_store"),
    (5, "shop", "supermarket", "supermarket"),
    (5, "amenity", "fuel", "gas_station"),
    (5, "amenity", "fast_food", "fast_food"),
    # Tier 6: bars and pubs. Welcoming to linger, but only with a purchase
    # commitment — and many are closed during daytime play.
    (6, "amenity", "bar", "bar"),
    (6, "amenity", "pub", "pub"),
    # Tier 7: restaurants. The natural visit shape ("buy a meal, eat through
    # it, leave") matches neither the in-and-out nor the comfortable-linger
    # pattern, so they only win when nothing else is nearby.
    (7, "amenity", "restaurant", "restaurant"),
]

# Real public-transit stations always get included alongside generated POIs:
# if a play area has actual bus terminals, train stations, ferry terminals,
# etc., those are obvious meeting points and the rural cars-as-trains layer
# is meant to coexist with them (not replace them). All entries here use
# priority 0 — above any POI tier — and they are exempted from the per-
# cluster cap (they're additive, not competing). Spacing still applies so
# duplicates / very close stations get deduplicated.
#
# Skipped intentionally: `highway=bus_stop`. Those tag individual on-street
# stops, often every 200m in urban areas, which would flood the output; the
# game's "vehicle station" abstraction wants meeting points (stations and
# terminals), not every flag-stop along a route.
TRANSIT_STATION_CATEGORIES: list[tuple[int, str, str, str]] = [
    (0, "railway", "station", "train_station"),
    (0, "railway", "halt", "train_halt"),
    (0, "railway", "tram_stop", "tram_stop"),
    (0, "amenity", "bus_station", "bus_station"),
    (0, "amenity", "ferry_terminal", "ferry_terminal"),
    (0, "aerialway", "station", "cable_car_station"),
    (0, "public_transport", "station", "transit_station"),
]
TRANSIT_CATEGORY_LABELS = frozenset(label for _, _, _, label in TRANSIT_STATION_CATEGORIES)

ALL_CATEGORIES: list[tuple[int, str, str, str]] = TRANSIT_STATION_CATEGORIES + POI_CATEGORIES
LABEL_BY_KV = {(k, v): label for _, k, v, label in ALL_CATEGORIES}
PRIORITY_BY_KV = {(k, v): p for p, k, v, _ in ALL_CATEGORIES}


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


def _polygon_centroid(ring: list[tuple[float, float]]) -> tuple[float, float]:
    """Simple unweighted centroid of (lat, lon) points. Good enough for picking
    a projection origin; not a true centroid of an area on a sphere."""
    n = len(ring) - 1 if ring[0] == ring[-1] else len(ring)
    lat = sum(p[0] for p in ring[:n]) / n
    lon = sum(p[1] for p in ring[:n]) / n
    return lat, lon


def project_ring_to_km(
    ring: list[tuple[float, float]], lat0: float, lon0: float,
) -> list[tuple[float, float]]:
    """Equirectangular projection of a (lat, lon) ring to local (x, y) km
    coordinates centered at (lat0, lon0). Accurate to ~1% for polygons up to
    ~100 km across, ~5% at ~500 km — sufficient for binning into S/M/L tiers."""
    cos_lat0 = math.cos(math.radians(lat0))
    return [((lon - lon0) * 111.0 * cos_lat0, (lat - lat0) * 111.0) for lat, lon in ring]


@dataclass(frozen=True)
class POI:
    osm_id: int
    osm_type: str
    name: str
    category: str
    priority: int
    lat: float
    lon: float
    opening_hours: str | None  # raw OSM tag value, or None if absent
    open_during_play: bool | None  # True / False, or None if unknown / unparseable


@dataclass(frozen=True)
class PlayingWindow:
    """Days and hours during which the game will be played."""
    start: time
    end: time
    days: tuple[int, ...]  # weekday integers, 0=Monday … 6=Sunday


def parse_game_size(spec: str) -> str:
    """Parse 'S' / 'M' / 'L' (or 'small'/'medium'/'large', case-insensitive)."""
    s = spec.strip().lower()
    if s in ("s", "small"):
        return "S"
    if s in ("m", "medium"):
        return "M"
    if s in ("l", "large"):
        return "L"
    raise ValueError(f"unknown game size {spec!r}; use S/M/L or small/medium/large")


def parse_playing_hours(spec: str) -> tuple[time, time]:
    """Parse '7am-7pm' or '07:00-19:00' into (start, end) time-of-day pairs."""
    s = spec.strip().lower()
    if "-" not in s:
        raise ValueError(f"--playing-hours must contain '-', got {spec!r}")
    start_s, end_s = (p.strip() for p in s.split("-", 1))
    return _parse_one_time(start_s), _parse_one_time(end_s)


def _parse_one_time(s: str) -> time:
    """Parse '7', '7:30', '07:00', '7am', '7:30pm' into a datetime.time."""
    s = s.strip().lower().replace(" ", "")
    suffix = ""
    if s.endswith(("am", "pm")):
        suffix, s = s[-2:], s[:-2]
    if ":" in s:
        h_s, m_s = s.split(":", 1)
        hour, minute = int(h_s), int(m_s)
    else:
        hour, minute = int(s), 0
    if suffix == "pm" and hour < 12:
        hour += 12
    elif suffix == "am" and hour == 12:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"invalid time-of-day: {s!r}")
    return time(hour, minute)


def parse_playing_days(spec: str) -> tuple[int, ...]:
    """Parse 'sat,sun' (case-insensitive, spaces ok) into a sorted tuple of weekdays."""
    parts = [p.strip().lower() for p in spec.split(",") if p.strip()]
    if not parts:
        raise ValueError("--playing-days-of-week must list at least one day")
    out: set[int] = set()
    for p in parts:
        if p not in DAY_NAME_TO_INT:
            raise ValueError(f"unknown day name {p!r}; use mon/tue/.../sun")
        out.add(DAY_NAME_TO_INT[p])
    return tuple(sorted(out))


def is_open_during_play(opening_hours_spec: str | None, window: PlayingWindow) -> bool | None:
    """Return True if the place is open at any sample point inside the playing
    window on any of the playing days, False if known closed throughout, or
    None if no spec / unparseable spec.

    Sampling: the start, midpoint, and end of the playing window on each
    playing day. Missing data is intentionally treated as 'unknown' (no
    penalty) — the user can verify in person and many real-world POIs
    simply lack opening_hours tags.
    """
    if not opening_hours_spec:
        return None
    try:
        oh = OpeningHours(opening_hours_spec)
    except Exception:
        return None
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    start_min = window.start.hour * 60 + window.start.minute
    end_min = window.end.hour * 60 + window.end.minute
    mid_min = (start_min + end_min) // 2
    sample_times = (
        window.start,
        time(mid_min // 60, mid_min % 60),
        window.end,
    )
    for day_int in window.days:
        date = monday + timedelta(days=day_int)
        for t in sample_times:
            try:
                if oh.is_open(datetime.combine(date, t)):
                    return True
            except Exception:
                return None
    return False


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


def build_overpass_query(
    polygon: list[tuple[float, float]],
    include_transit: bool = True,
) -> str:
    poly_str = " ".join(f"{lat} {lon}" for lat, lon in polygon)
    categories = TRANSIT_STATION_CATEGORIES + POI_CATEGORIES if include_transit else POI_CATEGORIES
    parts: list[str] = []
    seen_filters: set[tuple[str, str]] = set()
    for _, key, value, _ in categories:
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


def query_overpass_cached(query: str, fixture_path: Path | None) -> list[dict]:
    """Like ``query_overpass`` but reads/writes a JSON fixture file when given.

    If ``fixture_path`` is provided and the file exists, the cached elements
    are returned with no network call. If the file does not exist, the live
    query runs and the response is written to the file before returning.
    This is used by the parity test to freeze a known Overpass response so
    the JS port can be diffed against the Python output without OSM drift.
    """
    if fixture_path is not None and fixture_path.exists():
        return json.loads(fixture_path.read_text())
    elements = query_overpass(query)
    if fixture_path is not None:
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text(json.dumps(elements))
    return elements


# Tags that mark a polygon as a body of water / non-playable land cover.
# Subtracted from the play area when computing map size for game-size inference.
WATER_TAG_FILTERS: list[tuple[str, str]] = [
    ("natural", "water"),
    ("natural", "bay"),
    ("waterway", "riverbank"),
    ("waterway", "dock"),
    ("landuse", "reservoir"),
    ("landuse", "basin"),
]


def query_water_polygons(
    polygon: list[tuple[float, float]],
    fixture_path: Path | None = None,
) -> list[list[tuple[float, float]]]:
    """Query Overpass for water polygons inside the play polygon.

    Returns a list of (lat, lon) outer-ring polylines, one per water way.
    Multipolygon relations are skipped — most water bodies in OSM are tagged
    on the way level, and relation handling adds complexity disproportionate
    to the value (areas already subtracted from intersection are correct;
    skipping a few coastline relations underestimates water slightly, which
    biases the game-size inference toward larger, not smaller).
    """
    poly_str = " ".join(f"{lat} {lon}" for lat, lon in polygon)
    parts: list[str] = []
    for key, value in WATER_TAG_FILTERS:
        parts.append(f'  way["{key}"="{value}"](poly:"{poly_str}");')
    body = "\n".join(parts)
    query = f"[out:json][timeout:{OVERPASS_TIMEOUT_SEC}];\n(\n{body}\n);\nout geom;"
    elements = query_overpass_cached(query, fixture_path)
    rings: list[list[tuple[float, float]]] = []
    for el in elements:
        geom = el.get("geometry") or []
        if len(geom) < 3:
            continue
        ring = [(g["lat"], g["lon"]) for g in geom]
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        rings.append(ring)
    return rings


@dataclass(frozen=True)
class PlayArea:
    gross_km2: float          # polygon area, no subtractions
    net_km2: float            # after all subtractions
    water_km2: float          # area subtracted as water (0 if disabled)
    user_excl_km2: float      # area subtracted from --subtract-polygon (0 if not used)


def compute_play_area(
    polygon: list[tuple[float, float]],
    subtract_water: bool,
    extra_subtract_ring: list[tuple[float, float]] | None,
    water_fixture_path: Path | None = None,
) -> PlayArea:
    """Compute play area in km², optionally subtracting water and a user polygon.

    Uses an equirectangular projection centered on the polygon centroid so
    shapely's planar `.area` returns km². Distortion is < 1% up to ~100 km
    across and ~5% at ~500 km — enough resolution to bin into S/M/L tiers.
    """
    lat0, lon0 = _polygon_centroid(polygon)
    play_xy = project_ring_to_km(polygon, lat0, lon0)
    play = Polygon(play_xy)
    if not play.is_valid:
        play = play.buffer(0)  # repair common self-touching issues
    gross_km2 = float(play.area)

    excl_polys = []
    water_km2 = 0.0
    user_excl_km2 = 0.0

    if subtract_water:
        try:
            rings = query_water_polygons(polygon, fixture_path=water_fixture_path)
            print(f"Water polygons fetched: {len(rings)}", file=sys.stderr)
            water_geoms = []
            for ring in rings:
                p = Polygon(project_ring_to_km(ring, lat0, lon0))
                if not p.is_valid:
                    p = p.buffer(0)
                if p.is_empty:
                    continue
                water_geoms.append(p)
            if water_geoms:
                water_union = unary_union(water_geoms)
                water_inside = water_union.intersection(play)
                water_km2 = float(water_inside.area)
                excl_polys.append(water_union)
        except Exception as e:
            print(f"warning: water subtraction failed ({e}); using gross area", file=sys.stderr)

    if extra_subtract_ring is not None:
        try:
            user_poly = Polygon(project_ring_to_km(extra_subtract_ring, lat0, lon0))
            if not user_poly.is_valid:
                user_poly = user_poly.buffer(0)
            user_excl_km2 = float(user_poly.intersection(play).area)
            excl_polys.append(user_poly)
        except Exception as e:
            print(f"warning: --subtract-polygon failed ({e})", file=sys.stderr)

    if excl_polys:
        net = play.difference(unary_union(excl_polys))
        net_km2 = float(net.area)
    else:
        net_km2 = gross_km2

    return PlayArea(
        gross_km2=gross_km2,
        net_km2=max(0.0, net_km2),
        water_km2=water_km2,
        user_excl_km2=user_excl_km2,
    )


def infer_game_size(area_km2: float) -> str:
    """Map a polygon area in km² to an S/M/L game size per the rulebook's
    'Choosing a Transit System' bands."""
    if area_km2 >= GAME_SIZE_AREA_FLOOR_KM2["L"]:
        return "L"
    if area_km2 >= GAME_SIZE_AREA_FLOOR_KM2["M"]:
        return "M"
    return "S"


def auto_tune_cap(
    candidates: list[POI],
    min_station_m: float,
    cluster_radius_m: float,
    target_band: tuple[float, float],
    cap_range: range = AUTO_TUNE_CAP_RANGE,
) -> tuple[list[tuple[POI, int]], list[Rejection], int, list[tuple[int, int]]]:
    """Sweep cap values in ``cap_range`` and return the smallest cap whose
    station count falls inside ``target_band``. If no cap fits, return the
    one whose count is closest to the band.

    Returns ``(kept, rejected, chosen_cap, trail)`` where ``trail`` is a list
    of ``(cap, count)`` pairs for stderr/debug attribution.
    """
    lo, hi = target_band
    best = None  # (diff, cap, count, kept, rejected)
    trail: list[tuple[int, int]] = []
    for cap in cap_range:
        kept, rejected = filter_two_tier(
            candidates, min_station_m, cluster_radius_m, max_per_cluster=cap,
        )
        count = len(kept)
        trail.append((cap, count))
        if lo <= count <= hi:
            return kept, rejected, cap, trail
        diff = max(lo - count, 0.0, count - hi)  # gap to nearest band edge
        if best is None or diff < best[0]:
            best = (diff, cap, count, kept, rejected)
    _, cap, _, kept, rejected = best  # type: ignore[misc]
    return kept, rejected, cap, trail


def parse_pois(elements: list[dict], window: PlayingWindow) -> list[POI]:
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
        category, base_priority = _classify(tags)
        if category is None:
            continue
        name = tags.get("name") or f"unnamed {category}"
        opening_hours_spec = tags.get("opening_hours") or None
        open_during = is_open_during_play(opening_hours_spec, window)
        # Real transit stations skip the closed-hours penalty: they're
        # functionally always accessible as physical meeting points, even
        # when scheduled service hours vary. The tag's opening_hours, when
        # present, usually means the ticket office or terminal building.
        is_transit = category in TRANSIT_CATEGORY_LABELS
        if is_transit or open_during is not False:
            priority = base_priority
        else:
            priority = base_priority + CLOSED_PRIORITY_PENALTY
        pois.append(
            POI(
                osm_id=osm_id,
                osm_type=osm_type,
                name=name,
                category=category,
                priority=priority,
                lat=lat,
                lon=lon,
                opening_hours=opening_hours_spec,
                open_during_play=open_during,
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


@dataclass(frozen=True)
class Rejection:
    """A POI that was filtered out, with structured reason for debugging."""
    poi: POI
    cluster_id: int
    reason: str               # "spacing" or "cluster_cap"
    conflict_with: str | None  # name of the kept station that blocked it (spacing only)


def filter_two_tier(
    pois: list[POI],
    min_station_m: float,
    cluster_radius_m: float,
    max_per_cluster: int | None = None,
) -> tuple[list[tuple[POI, int]], list[Rejection]]:
    """Seed-and-grow clustering, then intra-cluster spacing filter + cap.

    Step 1 — cluster by seed-and-grow:
        a. Sort all POIs by (priority, name) so the highest-priority unassigned
           POI is always picked next.
        b. Pop the next unassigned POI as a cluster seed.
        c. Assign every unassigned POI within ``cluster_radius_m`` of the seed
           to that seed's cluster.
        d. Repeat until every POI is assigned.

    This avoids the single-linkage chaining that union-find suffered from in
    dense commercial corridors: every cluster has a *hard radius* around a
    meaningful seed (the highest-priority POI in the cluster), so two distinct
    real-world commercial nodes can't collapse into one giant cluster just
    because a strip of cafés connects them.

    Step 2 — within each cluster, sort by (priority, name) and greedy-keep:
    drop any candidate within ``min_station_m`` of an already-kept station;
    stop adding after ``max_per_cluster`` if set.

    Returns ``(kept, rejected)``: the list of ``(POI, cluster_id)`` pairs that
    survived, and the list of ``Rejection`` records for the rest. Cluster IDs
    are assigned in seed-priority order — cluster 1 is centered on the
    highest-priority POI in the input.
    """
    # Step 1: seed-and-grow clustering.
    ordered_by_priority = sorted(pois, key=lambda p: (p.priority, p.name.lower()))
    cluster_id_of: dict[tuple[str, int], int] = {}
    cluster_members: dict[int, list[POI]] = {}
    next_id = 1
    for seed in ordered_by_priority:
        seed_key = (seed.osm_type, seed.osm_id)
        if seed_key in cluster_id_of:
            continue
        cid = next_id
        next_id += 1
        members: list[POI] = []
        for p in ordered_by_priority:
            pkey = (p.osm_type, p.osm_id)
            if pkey in cluster_id_of:
                continue
            if haversine_m(seed.lat, seed.lon, p.lat, p.lon) <= cluster_radius_m:
                cluster_id_of[pkey] = cid
                members.append(p)
        cluster_members[cid] = members

    # Step 2: intra-cluster spacing filter + per-cluster cap.
    out: list[tuple[POI, int]] = []
    rejected: list[Rejection] = []
    for cid in sorted(cluster_members):
        ordered = sorted(cluster_members[cid], key=lambda p: (p.priority, p.name.lower()))
        kept: list[POI] = []
        non_transit_kept = 0
        cap_hit = False  # only blocks non-transit; transit is additive
        for p in ordered:
            is_transit = p.category in TRANSIT_CATEGORY_LABELS
            if cap_hit and not is_transit:
                rejected.append(Rejection(p, cid, "cluster_cap", None))
                continue
            blocker: POI | None = None
            for k in kept:
                if haversine_m(p.lat, p.lon, k.lat, k.lon) < min_station_m:
                    blocker = k
                    break
            if blocker is not None:
                rejected.append(Rejection(p, cid, "spacing", blocker.name))
                continue
            kept.append(p)
            if not is_transit:
                non_transit_kept += 1
                if max_per_cluster is not None and non_transit_kept >= max_per_cluster:
                    cap_hit = True
        out.extend((p, cid) for p in kept)
    return out, rejected


def _hours_known(p: POI) -> str:
    return "yes" if p.opening_hours else "no"


def _open_during_play_str(p: POI) -> str:
    if p.open_during_play is True:
        return "yes"
    if p.open_during_play is False:
        return "no"
    return "unknown"


def emit_debug_candidates(
    kept_with_cluster: list[tuple[POI, int]],
    rejections: list[Rejection],
    out=sys.stdout,
) -> None:
    """Write one line per candidate POI in shell-style key=value format.

    Output goes to ``out`` (stdout by default), one POI per line, sorted by
    cluster_id then kept-status (kept first, then rejected). Status messages
    stay on stderr so the user can pipe stdout directly to grep without
    losing progress info.

    Format example::

        poi cluster=1 kept=yes name='Sioux Falls Museum' category=museum priority=2 lat=43.547000 lon=-96.730800 osm=node/123 hours_known=yes open_during_play=yes
        poi cluster=1 kept=no  reason=spacing conflict_with='Sioux Falls Museum' name='Joe Coffee' category=cafe priority=2 lat=43.547100 lon=-96.730900 osm=node/789 hours_known=no  open_during_play=unknown
    """
    rows: list[tuple[int, int, list[str]]] = []  # (cluster_id, kept_rank, fields)
    for p, cid in kept_with_cluster:
        fields = [
            "poi",
            f"cluster={cid}",
            "kept=yes",
            f"name={shlex.quote(p.name)}",
            f"category={p.category}",
            f"priority={p.priority}",
            f"lat={p.lat:.6f}",
            f"lon={p.lon:.6f}",
            f"osm={p.osm_type}/{p.osm_id}",
            f"hours_known={_hours_known(p)}",
            f"open_during_play={_open_during_play_str(p)}",
        ]
        rows.append((cid, 0, fields))
    for r in rejections:
        p = r.poi
        fields = [
            "poi",
            f"cluster={r.cluster_id}",
            "kept=no",
            f"reason={r.reason}",
        ]
        if r.conflict_with is not None:
            fields.append(f"conflict_with={shlex.quote(r.conflict_with)}")
        fields += [
            f"name={shlex.quote(p.name)}",
            f"category={p.category}",
            f"priority={p.priority}",
            f"lat={p.lat:.6f}",
            f"lon={p.lon:.6f}",
            f"osm={p.osm_type}/{p.osm_id}",
            f"hours_known={_hours_known(p)}",
            f"open_during_play={_open_during_play_str(p)}",
        ]
        rows.append((r.cluster_id, 1, fields))
    rows.sort(key=lambda x: (x[0], x[1]))
    for _, _, fields in rows:
        print(" ".join(fields), file=out)


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
        "open_during_play",
        "opening_hours",
        "osm_type",
        "osm_id",
    ]
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_kml(out_path: Path, layer_name: str, rows: list[dict], generated_at: str | None = None) -> None:
    """Write a KML file with all stations in a single Folder.

    Google My Maps imports the file as one map layer named ``layer_name``,
    which the user can delete in one click to remove all pins. Google Earth,
    OsmAnd, GAIA, and QGIS also read the file natively.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if generated_at is None:
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
    ap.add_argument("--game-size", type=parse_game_size, default=None,
                    help="Official Hide + Seek game size (S, M, or L; also accepts small/medium/large). "
                         "When set, defaults --cluster-radius-m to the official hiding-zone "
                         f"radius for that size: S/M → {HIDING_ZONE_RADIUS_M_BY_GAME_SIZE['S']}m "
                         f"(¼ mile), L → {HIDING_ZONE_RADIUS_M_BY_GAME_SIZE['L']}m (½ mile). "
                         "If --cluster-radius-m is also set explicitly, that wins.")
    ap.add_argument("--cluster-radius-m", type=float, default=None,
                    help=f"Maximum distance from a cluster's seed POI to any of its members, "
                         f"in meters. Clusters are grown by picking the highest-priority "
                         f"unassigned POI as a seed and absorbing every unassigned POI within "
                         f"this radius, repeating until none remain. Default: {CLUSTER_RADIUS_M} "
                         f"(or the official hiding-zone radius if --game-size is set).")
    ap.add_argument("--density-radius-m", type=float, default=DENSITY_RADIUS_M,
                    help=f"Radius for local POI density count (default: {DENSITY_RADIUS_M})")
    ap.add_argument("--max-stations-per-cluster", type=int, default=None,
                    help=f"Maximum stations per cluster — keeps the highest-priority N after "
                         f"the spacing filter. If unset and the game size is known (explicit or "
                         f"inferred), the tool auto-tunes this cap to land the total station "
                         f"count inside the rulebook's S/M/L band. Otherwise defaults to "
                         f"{MAX_STATIONS_PER_CLUSTER}. Pass 0 to disable the cap entirely.")
    ap.add_argument("--water-subtract", action=argparse.BooleanOptionalAction, default=True,
                    help="Subtract OSM water polygons (lakes, rivers, reservoirs) from the play "
                         "polygon when computing area for game-size inference. Adds one extra "
                         "Overpass call. Pass --no-water-subtract to skip.")
    ap.add_argument("--include-transit-stations", action=argparse.BooleanOptionalAction, default=True,
                    help="Include actual public-transit stations from OSM (train stations, tram "
                         "stops, bus stations, ferry terminals, etc.) alongside generated POI "
                         "stations. Transit stations are exempt from the per-cluster cap (they're "
                         "additive) and from the closed-hours penalty (they're always-accessible "
                         "meeting points). Pass --no-include-transit-stations to skip.")
    ap.add_argument("--subtract-polygon", type=Path, default=None,
                    help="Additional GeoJSON/text polygon to subtract from the play area before "
                         "inferring game size (e.g. a national-forest boundary you're skipping, "
                         "a closed military range). Same format as --polygon-file.")
    ap.add_argument("--playing-hours", type=str, default=DEFAULT_PLAYING_HOURS,
                    help=f"Time-of-day window during which the game will be played. Used to "
                         f"deprioritize POIs whose OSM `opening_hours` tag indicates they're "
                         f"closed throughout the window. Format: '7am-7pm' or '07:00-19:00'. "
                         f"Default: {DEFAULT_PLAYING_HOURS}.")
    ap.add_argument("--playing-days-of-week", type=str, default=DEFAULT_PLAYING_DAYS,
                    help=f"Comma-delimited weekdays during which the game will be played. "
                         f"Used together with --playing-hours. Default: {DEFAULT_PLAYING_DAYS}.")
    ap.add_argument("--overpass-fixture-dir", type=Path, default=None,
                    help="Directory holding cached Overpass responses ('pois.json', "
                         "'water.json'). If the files exist, they're read instead of "
                         "calling Overpass. If not, the live queries run and responses "
                         "are written to this directory. Used by the parity test to "
                         "freeze a known Overpass response so the JS port can be diffed "
                         "against the Python output without OSM drift.")
    ap.add_argument("--output-dir", type=Path, default=None,
                    help="Directory to write CSV/KML output to (default: tools/.output/).")
    ap.add_argument("--no-timestamp", action="store_true",
                    help="Omit the UTC timestamp from output filenames. With this set, "
                         "output is '{name}.csv' and '{name}.kml' (overwrites prior runs); "
                         "without it, '{name}-{timestamp}.{ext}'.")
    ap.add_argument("--debug-candidates", action="store_true",
                    help="Print one line per candidate POI to stdout in shell-style "
                         "key=value format (kept and rejected, with reason). Designed to "
                         "stream into grep — status messages stay on stderr so "
                         "`uv run vehicle-stations … --debug-candidates | grep cluster=5` works.")
    args = ap.parse_args()

    if args.max_stations_per_cluster is not None and args.max_stations_per_cluster < 0:
        ap.error("--max-stations-per-cluster must be 0 or a positive integer")

    try:
        play_start, play_end = parse_playing_hours(args.playing_hours)
    except ValueError as e:
        ap.error(f"--playing-hours: {e}")
    try:
        play_days = parse_playing_days(args.playing_days_of_week)
    except ValueError as e:
        ap.error(f"--playing-days-of-week: {e}")
    playing_window = PlayingWindow(start=play_start, end=play_end, days=play_days)

    polygon = load_polygon(args.polygon_file)
    print(f"Polygon: {len(polygon) - 1} unique points", file=sys.stderr)

    # Resolve game size: explicit --game-size wins; else infer from polygon area.
    extra_excl_ring = None
    if args.subtract_polygon is not None:
        extra_excl_ring = load_polygon(args.subtract_polygon)
    if args.game_size is not None:
        game_size = args.game_size
        game_size_source = "explicit"
        area_info = None
    else:
        try:
            water_fixture = (
                args.overpass_fixture_dir / "water.json"
                if args.overpass_fixture_dir is not None else None
            )
            area_info = compute_play_area(
                polygon,
                subtract_water=args.water_subtract,
                extra_subtract_ring=extra_excl_ring,
                water_fixture_path=water_fixture,
            )
            game_size = infer_game_size(area_info.net_km2)
            chain = f"{area_info.gross_km2:.0f} km² gross"
            if area_info.water_km2 > 0:
                chain += f" − {area_info.water_km2:.0f} km² water"
            if area_info.user_excl_km2 > 0:
                chain += f" − {area_info.user_excl_km2:.0f} km² user-excluded"
            if area_info.water_km2 > 0 or area_info.user_excl_km2 > 0:
                chain += f" = {area_info.net_km2:.0f} km² net"
            game_size_source = f"inferred from area ({chain})"
        except Exception as e:
            print(f"warning: area calc failed ({e}); falling back to defaults", file=sys.stderr)
            area_info = None
            game_size = None
            game_size_source = None

    # Resolve cluster radius: explicit > game-size mapping > default.
    if args.cluster_radius_m is not None:
        cluster_radius_m = args.cluster_radius_m
        radius_source = "explicit"
    elif game_size is not None:
        cluster_radius_m = HIDING_ZONE_RADIUS_M_BY_GAME_SIZE[game_size]
        radius_source = f"game-size {game_size}"
    else:
        cluster_radius_m = CLUSTER_RADIUS_M
        radius_source = "default"
    if cluster_radius_m <= args.min_station_spacing_m:
        ap.error("--cluster-radius-m must be greater than --min-station-spacing-m")

    if game_size is not None:
        print(f"Game size: {game_size} ({game_size_source})", file=sys.stderr)
    print(f"Cluster radius: {cluster_radius_m:.0f}m ({radius_source})", file=sys.stderr)

    query = build_overpass_query(polygon, include_transit=args.include_transit_stations)
    pois_fixture = (
        args.overpass_fixture_dir / "pois.json"
        if args.overpass_fixture_dir is not None else None
    )
    print("Querying Overpass for POIs…", file=sys.stderr)
    t0 = wall_time.time()
    elements = query_overpass_cached(query, pois_fixture)
    print(f"Got {len(elements)} elements in {wall_time.time() - t0:.1f}s", file=sys.stderr)

    candidates = parse_pois(elements, playing_window)
    n_transit = sum(1 for p in candidates if p.category in TRANSIT_CATEGORY_LABELS)
    n_poi = len(candidates) - n_transit
    poi_candidates = [p for p in candidates if p.category not in TRANSIT_CATEGORY_LABELS]
    n_open = sum(1 for p in poi_candidates if p.open_during_play is True)
    n_closed = sum(1 for p in poi_candidates if p.open_during_play is False)
    n_unknown = sum(1 for p in poi_candidates if p.open_during_play is None)
    if args.include_transit_stations:
        transit_clause = f"{n_transit} real transit stations (always included)"
    else:
        transit_clause = "transit stations skipped (--no-include-transit-stations)"
    print(
        f"Recognized {len(candidates)} candidates: "
        f"{n_poi} POIs (open during play: {n_open}, closed: {n_closed}, hours unknown: {n_unknown}); "
        f"{transit_clause}",
        file=sys.stderr,
    )
    if not candidates:
        print("No POIs found — check the polygon and tag list.", file=sys.stderr)
        return 1

    # Resolve cap: explicit > auto-tune (if game size known) > default.
    if args.max_stations_per_cluster is not None:
        max_per_cluster = args.max_stations_per_cluster or None
        cap_source = "explicit"
        stations_with_cluster, rejections = filter_two_tier(
            candidates, args.min_station_spacing_m, cluster_radius_m,
            max_per_cluster=max_per_cluster,
        )
    elif game_size is not None:
        target_band = GAME_SIZE_STATION_BANDS[game_size]
        stations_with_cluster, rejections, max_per_cluster, trail = auto_tune_cap(
            candidates, args.min_station_spacing_m, cluster_radius_m, target_band,
        )
        lo, hi = target_band
        hi_str = "∞" if hi == float("inf") else f"{hi:.0f}"
        in_band = lo <= len(stations_with_cluster) <= hi
        cap_source = (
            f"auto-tuned for game-size {game_size} (target {lo:.0f}–{hi_str} stations, "
            f"swept {trail[0][0]}..{trail[-1][0]})"
        )
        if not in_band:
            print(
                f"warning: could not fit station count into band {lo:.0f}–{hi_str}; "
                f"closest was {len(stations_with_cluster)} at cap={max_per_cluster}. "
                f"Try a tighter polygon or override --max-stations-per-cluster.",
                file=sys.stderr,
            )
    else:
        max_per_cluster = MAX_STATIONS_PER_CLUSTER
        cap_source = "default"
        stations_with_cluster, rejections = filter_two_tier(
            candidates, args.min_station_spacing_m, cluster_radius_m,
            max_per_cluster=max_per_cluster,
        )

    cluster_count = len({cid for _, cid in stations_with_cluster})
    cap_note = f", cap {max_per_cluster}/cluster ({cap_source})" if max_per_cluster else ", no cap"
    kept_transit = sum(1 for p, _ in stations_with_cluster if p.category in TRANSIT_CATEGORY_LABELS)
    kept_poi = len(stations_with_cluster) - kept_transit
    transit_note = f" ({kept_poi} POI + {kept_transit} real transit)" if kept_transit else ""
    print(
        f"Selected {len(stations_with_cluster)} stations{transit_note} across {cluster_count} clusters "
        f"(intra-cluster ≥ {args.min_station_spacing_m:.0f}m, "
        f"cluster radius ≤ {cluster_radius_m:.0f}m [{radius_source}]{cap_note}); "
        f"{len(rejections)} candidates rejected",
        file=sys.stderr,
    )

    if args.debug_candidates:
        emit_debug_candidates(stations_with_cluster, rejections)

    rows: list[dict] = []
    for st, cid in stations_with_cluster:
        nearby = count_nearby(st, candidates, args.density_radius_m)
        wmin, wmax, tier = wait_range_for_density(nearby)
        if st.open_during_play is True:
            open_status = "yes"
        elif st.open_during_play is False:
            open_status = "no"
        else:
            open_status = "unknown"
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
                "open_during_play": open_status,
                "opening_hours": st.opening_hours or "",
                "osm_type": st.osm_type,
                "osm_id": st.osm_id,
            }
        )

    out_dir = args.output_dir if args.output_dir is not None else Path(__file__).resolve().parent / ".output"
    if args.no_timestamp:
        stem = args.name
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        stem = f"{args.name}-{timestamp}"
    csv_path = out_dir / f"{stem}.csv"
    kml_path = out_dir / f"{stem}.kml"
    write_csv(csv_path, rows)
    kml_generated_at = "fixture" if args.no_timestamp else None
    write_kml(kml_path, args.name, rows, generated_at=kml_generated_at)
    print(f"Wrote {csv_path}", file=sys.stderr)
    print(f"Wrote {kml_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
