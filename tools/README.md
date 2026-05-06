# Tools — Rural Jet Lag

This directory contains scripts and utilities to help set up and run a Rural Jet Lag game.

---

## Tools

| File | Description |
|------|-------------|
| [`driving_isochrone.py`](./driving_isochrone.py) | Generates driving-time isochrone maps for a given starting point using the OpenRouteService API |

---

## Requirements

The tools in this directory require Python 3.8+. Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## driving_isochrone.py

Generates driving-time isochrone maps — areas reachable within a set drive time from a given point.

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

The script produces an interactive HTML map (using [Folium](https://python-visualization.github.io/folium/)) showing colored zones around the starting point:

- 🟢 **Zone 1:** 0–15 min drive (innermost)
- 🟡 **Zone 2:** 15–30 min drive
- 🟠 **Zone 3:** 30–60 min drive
- 🔴 **Zone 4:** 60–90 min drive (outer boundary)

Open the output file in any web browser to view or screenshot the map for game setup.

---

## External Tools & Resources

These external tools are also useful for rural game setup:

- **[OpenRouteService Isochrones](https://maps.openrouteservice.org/)** — Web interface for generating isochrones without code.
- **[Google My Maps](https://mymaps.google.com/)** — Draw and share custom play area boundaries.
- **[Gaia GPS](https://www.gaiagps.com/)** — Offline maps; great for rural areas with poor cell service.
- **[Atlas Obscura](https://www.atlasobscura.com/)** — Find roadside oddities and unique landmarks for challenges.
- **[Roadsideamerica.com](https://www.roadsideamerica.com/)** — US roadside attraction database, searchable by state/county.
- **[Census Gazetteer](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html)** — Official list of incorporated places by population (useful for "Smallest Town" rule).

---

## License

Code in this directory is licensed under the [MIT License](../LICENSE).
