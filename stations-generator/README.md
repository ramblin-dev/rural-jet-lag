# Vehicle-stations tooling

The cross-game vehicle-stations algorithm and its Node CLI. The *browser*
form of the generator lives in the site (at [`/site/stations/`](../site/stations/),
served as the `/stations` route on [ruralhs.ramblin.dev](https://ruralhs.ramblin.dev))
and consumes `@rural-jet-lag/core` from this directory as a workspace
dependency.

## Layout

| Workspace | Purpose |
|---|---|
| [`core/`](./core/) | Isomorphic algorithmic core — clustering, spacing filter, cap auto-tune, wait-range tiers, area calc, Overpass query construction, POI parsing, KML rendering. No filesystem or browser-only deps. |
| [`cli/`](./cli/) | Node CLI. Mirrors what the sidebar settings on the site let you tweak; useful for batch / scripted runs. |
| [`test/`](./test/) | Frozen Overpass fixture + reference output for the regression test. |

## Setup

```bash
npm install              # from the repo root
```

## Common commands

All run from the repo root:

```bash
npm run dev              # Vite dev server for the site (the generator UI lives at /stations)
npm run build            # produces site/dist/ for Netlify
npm run cli -- --help    # invoke the Node CLI directly
npm test                 # run the regression test against the frozen fixture
```

## Parity / regression test

The JS pipeline is pinned against a checked-in Overpass snapshot and a
reference CSV/KML originally captured from the Python implementation that
seeded this port. `npm test` regenerates the JS output and diffs
it against that baseline; a failure means algorithmic drift, not OSM drift.
See [`test/README.md`](./test/README.md) for how to bless a
new baseline when an intentional change lands.
