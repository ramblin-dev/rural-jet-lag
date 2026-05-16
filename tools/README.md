# Vehicle-stations tooling

JS workspace that powers the rural-jet-lag vehicle-stations generator in two
forms — a Node CLI and a browser-based static site. Both share an
isomorphic algorithmic core. The Python reference implementation lives at
[`/old-tools/`](../old-tools/) during the transition and gets deleted once
the JS port has reached parity and the surrounding docs have been rewritten.

## Layout

| Workspace | Purpose |
|---|---|
| [`core/`](./core/) | Isomorphic algorithmic core — clustering, spacing filter, cap auto-tune, wait-range tiers, area calc, Overpass query construction, POI parsing, KML rendering. No filesystem or browser-only deps. |
| [`cli/`](./cli/) | Node CLI. Mirrors the legacy Python CLI's flags so the parity test can diff outputs. |
| [`site/`](./site/) | Vite-built static site. Draw a polygon, auto-generate stations, tweak settings, download KML for Google My Maps. |

## Setup

```bash
cd tools
npm install
```

## Common commands

```bash
npm run dev:site         # Vite dev server with HMR
npm run build:site       # produces site/dist/ for GitHub Pages
npm run cli -- --help    # invoke the CLI through the workspace
```

## Parity test

A frozen Overpass response + Python baseline live in
[`../old-tools/parity-test/`](../old-tools/parity-test/). The JS CLI's parity
runner reads the same fixture and writes a `js-sioux.{csv,kml}` baseline
that's diff'd against `python-sioux.{csv,kml}`. See that directory's README
for details.
