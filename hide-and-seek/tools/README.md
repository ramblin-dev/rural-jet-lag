# Tools — Rural Hide and Seek

This directory contains scripts and utilities to help set up and run a Rural Hide and Seek game.

---

## Tools

| File | Description |
|------|-------------|
| [`driving_isochrone.py`](./driving_isochrone.py) | Generates driving-time isochrone maps for a given starting point using the OpenRouteService API |

---

## Requirements

Requires Python 3.8+. Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## driving_isochrone.py

Generates driving-time isochrone maps — areas reachable within a set drive time from a given point. Use this before the game starts to visualize the driving zones that define the play area.

### Usage

```bash
python driving_isochrone.py --lat 39.7684 --lon -86.1581 --output game_map.html
```

Options:

| Flag | Description | Default |
|------|-------------|---------|
| `--lat` | Latitude of starting point | Required |
| `--lon` | Longitude of starting point | Required |
| `--api-key` | OpenRouteService API key | Reads from `ORS_API_KEY` env var |
| `--ranges` | Comma-separated drive times in seconds | `900,1800,3600,5400` (15m, 30m, 1h, 1.5h) |
| `--output` | Output HTML file | `isochrone_map.html` |

### Getting an API Key

1. Create a free account at [openrouteservice.org](https://openrouteservice.org/).
2. Go to your dashboard and create an API key.
3. Set the environment variable: `export ORS_API_KEY=your_key_here`

### Output

The script produces an interactive HTML map (using [Folium](https://python-visualization.github.io/folium/)) showing colored driving-time zones around the starting point:

- 🟢 **Zone 1:** 0–15 min drive (innermost)
- 🟡 **Zone 2:** 15–30 min drive
- 🟠 **Zone 3:** 30–60 min drive
- 🔴 **Zone 4:** 60–90 min drive (outer boundary)

Open the output file in any web browser. Screenshot the map and share with all players before the game starts.

---

## External Tools & Resources

- **[OpenRouteService Isochrones](https://maps.openrouteservice.org/)** — Web interface for generating isochrones without code.
- **[Google My Maps](https://mymaps.google.com/)** — Draw and share custom play area boundaries.
- **[Gaia GPS](https://www.gaiagps.com/)** — Offline maps; great for rural areas with poor cell service.
- **[Census Gazetteer](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html)** — Official list of incorporated places by population (useful for the "Smallest Town Shield" Evasion Card).

---

## License

Code in this directory is licensed under the [MIT License](../../LICENSE).
