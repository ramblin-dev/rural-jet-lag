"""
driving_isochrone.py — Rural Jet Lag Map Tool

Generates a driving-time isochrone map for a given starting point using the
OpenRouteService (ORS) API. Outputs an interactive HTML map showing zones
reachable within defined drive times.

Usage:
    python driving_isochrone.py --lat 39.7684 --lon -86.1581 --output game_map.html

Requirements:
    pip install -r requirements.txt

API Key:
    Set the ORS_API_KEY environment variable or pass via --api-key.
    Free API keys available at https://openrouteservice.org/
"""

import argparse
import os
import sys

try:
    import folium
    import requests
except ImportError:
    sys.exit(
        "Missing dependencies. Run: pip install -r requirements.txt"
    )

# Driving-time zones: (seconds, label, color)
DEFAULT_ZONES = [
    (900, "Zone 1: 0–15 min", "#2ecc71"),    # green
    (1800, "Zone 2: 15–30 min", "#f1c40f"),   # yellow
    (3600, "Zone 3: 30–60 min", "#e67e22"),   # orange
    (5400, "Zone 4: 60–90 min", "#e74c3c"),   # red
]

ORS_ISOCHRONE_URL = "https://api.openrouteservice.org/v2/isochrones/driving-car"


def fetch_isochrones(lat: float, lon: float, ranges_seconds: list[int], api_key: str) -> dict:
    """Fetch isochrone GeoJSON from the OpenRouteService API."""
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "locations": [[lon, lat]],
        "range": ranges_seconds,
        "range_type": "time",
        "attributes": ["reachfactor"],
    }
    response = requests.post(ORS_ISOCHRONE_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def build_map(lat: float, lon: float, geojson: dict, zones: list[tuple]) -> folium.Map:
    """Build a Folium map with isochrone overlays."""
    m = folium.Map(location=[lat, lon], zoom_start=9, tiles="OpenStreetMap")

    # Add isochrone polygons (largest first so smaller ones render on top)
    features = geojson.get("features", [])
    sorted_features = sorted(
        features,
        key=lambda f: f.get("properties", {}).get("value", 0),
        reverse=True,
    )

    zone_by_value = {z[0]: z for z in zones}

    for feature in sorted_features:
        value = feature.get("properties", {}).get("value", 0)
        zone = zone_by_value.get(int(value), (value, f"{value // 60} min", "#95a5a6"))
        _, label, color = zone

        folium.GeoJson(
            feature,
            name=label,
            style_function=lambda _feature, c=color: {
                "fillColor": c,
                "color": c,
                "weight": 2,
                "fillOpacity": 0.25,
            },
            tooltip=label,
        ).add_to(m)

    # Add a marker for the starting point
    folium.Marker(
        location=[lat, lon],
        popup="Starting Point",
        icon=folium.Icon(color="blue", icon="flag"),
    ).add_to(m)

    # Add a layer control
    folium.LayerControl().add_to(m)

    # Add a legend
    legend_html = _build_legend_html(zones)
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def _build_legend_html(zones: list[tuple]) -> str:
    """Build an HTML legend for the map."""
    items = "".join(
        f'<li><span style="background:{color};display:inline-block;'
        f'width:16px;height:16px;margin-right:6px;border-radius:3px;'
        f'opacity:0.7;"></span>{label}</li>'
        for _, label, color in zones
    )
    return f"""
    <div style="
        position: fixed;
        bottom: 30px; left: 30px;
        z-index: 1000;
        background: white;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        font-family: sans-serif;
        font-size: 13px;
    ">
        <strong>Driving Time Zones</strong>
        <ul style="list-style:none;margin:6px 0 0;padding:0;">
            {items}
        </ul>
    </div>
    """


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a driving-time isochrone map for Rural Jet Lag game setup."
    )
    parser.add_argument("--lat", type=float, required=True, help="Latitude of starting point")
    parser.add_argument("--lon", type=float, required=True, help="Longitude of starting point")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("ORS_API_KEY", ""),
        help="OpenRouteService API key (or set ORS_API_KEY env var)",
    )
    parser.add_argument(
        "--ranges",
        default="900,1800,3600,5400",
        help="Comma-separated drive times in seconds (default: 900,1800,3600,5400)",
    )
    parser.add_argument(
        "--output",
        default="isochrone_map.html",
        help="Output HTML file (default: isochrone_map.html)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.api_key:
        sys.exit(
            "Error: No API key provided. Set ORS_API_KEY environment variable "
            "or pass --api-key. Get a free key at https://openrouteservice.org/"
        )

    ranges_seconds = [int(r.strip()) for r in args.ranges.split(",")]

    # Build zone metadata for provided ranges
    default_labels = {z[0]: z for z in DEFAULT_ZONES}
    zones = []
    colors = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c", "#9b59b6", "#1abc9c"]
    for i, r in enumerate(ranges_seconds):
        if r in default_labels:
            zones.append(default_labels[r])
        else:
            minutes = r // 60
            color = colors[i % len(colors)]
            zones.append((r, f"Zone {i + 1}: {minutes} min", color))

    print(f"Fetching isochrones from OpenRouteService for ({args.lat}, {args.lon})...")
    try:
        geojson = fetch_isochrones(args.lat, args.lon, ranges_seconds, args.api_key)
    except requests.HTTPError as exc:
        sys.exit(f"API error: {exc}\nCheck your API key and rate limits.")
    except requests.ConnectionError:
        sys.exit("Connection error. Check your internet connection.")

    print("Building map...")
    m = build_map(args.lat, args.lon, geojson, zones)
    m.save(args.output)
    print(f"Map saved to: {args.output}")
    print("Open this file in any web browser to view your game area.")


if __name__ == "__main__":
    main()
