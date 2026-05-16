# Vehicle-stations tooling

JS workspace that powers the rural-jet-lag vehicle-stations generator in two
forms — a Node CLI and a browser-based static site. Both share an
isomorphic algorithmic core.

## Layout

| Workspace | Purpose |
|---|---|
| [`core/`](./core/) | Isomorphic algorithmic core — clustering, spacing filter, cap auto-tune, wait-range tiers, area calc, Overpass query construction, POI parsing, KML rendering. No filesystem or browser-only deps. |
| [`cli/`](./cli/) | Node CLI. Mirrors what the sidebar settings on the site let you tweak; useful for batch / scripted runs. |
| [`site/`](./site/) | Vite-built static site. Draw a polygon, auto-generate stations, tweak settings, download KML for Google My Maps. |
| [`test/`](./test/) | Frozen Overpass fixture + reference output for the regression test. |

## Setup

```bash
cd stations-generator
npm install
```

## Common commands

```bash
npm run dev:site         # Vite dev server with HMR
npm run build:site       # produces site/dist/ for GitHub Pages
npm run cli -- --help    # invoke the CLI through the workspace
npm test        # run the regression test against the frozen fixture
```

## Parity / regression test

The JS pipeline is pinned against a checked-in Overpass snapshot and a
reference CSV/KML originally captured from the Python implementation that
seeded this port. `npm test` regenerates the JS output and diffs
it against that baseline; a failure means algorithmic drift, not OSM drift.
See [`test/README.md`](./test/README.md) for how to bless a
new baseline when an intentional change lands.
