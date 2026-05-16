#!/usr/bin/env node
// vehicle-stations CLI (JS port). Mirrors the Python flag set so the
// parity test can diff outputs byte-for-byte (modulo the KML
// `generated_at` literal under --no-timestamp).

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { performance } from "node:perf_hooks";
import { fileURLToPath } from "node:url";
import {
  buildOverpassQuery,
  buildPlayingWindow,
  buildWaterQuery,
  generate,
  loadPolygonFromGeoJSON,
  loadPolygonFromPlainText,
  parseWaterRings,
  writeCSV,
  writeKML,
} from "@rural-jet-lag/core";
import { parseArgs } from "./args.js";
import { fetchOverpassCached } from "./overpass-node.js";

const HERE = dirname(fileURLToPath(import.meta.url));
const DEFAULT_OUTPUT_DIR = resolve(HERE, "..", ".output");

async function loadPolygon(path) {
  const text = await readFile(path, "utf8");
  if (/\.(geojson|json)$/i.test(path)) return loadPolygonFromGeoJSON(JSON.parse(text));
  return loadPolygonFromPlainText(text);
}

async function main() {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (e) {
    process.stderr.write(`error: ${e.message}\n`);
    process.exit(2);
  }

  const playingWindow = buildPlayingWindow({
    hoursSpec: opts.playingHours,
    daysSpec: opts.playingDaysOfWeek,
  });

  const polygon = await loadPolygon(opts.polygonFile);
  process.stderr.write(`Polygon: ${polygon.length - 1} unique points\n`);

  const exclRings = [];
  if (opts.subtractPolygon) exclRings.push(await loadPolygon(opts.subtractPolygon));

  const fixtureDir = opts.overpassFixtureDir;

  // Water query (if needed for area inference). Only run if game-size is
  // not explicit AND water-subtract is on. Match Python's behavior: when
  // game-size is explicit, no area calc is done at all.
  let waterRings = [];
  if (opts.gameSize === null && opts.waterSubtract) {
    try {
      const waterElements = await fetchOverpassCached(
        buildWaterQuery(polygon),
        fixtureDir ? join(fixtureDir, "water.json") : null,
      );
      waterRings = parseWaterRings(waterElements);
      process.stderr.write(`Water polygons fetched: ${waterRings.length}\n`);
    } catch (e) {
      process.stderr.write(`warning: water subtraction failed (${e.message}); using gross area\n`);
    }
  }

  // POI query.
  const poisFixturePath = fixtureDir ? join(fixtureDir, "pois.json") : null;
  process.stderr.write("Querying Overpass for POIs…\n");
  const t0 = performance.now();
  const poisElements = await fetchOverpassCached(
    buildOverpassQuery(polygon, { includeTransit: opts.includeTransitStations }),
    poisFixturePath,
  );
  const dt = (performance.now() - t0) / 1000;
  process.stderr.write(`Got ${poisElements.length} elements in ${dt.toFixed(1)}s\n`);

  // Run the pipeline.
  const settings = {
    minStationSpacingM: opts.minStationSpacingM,
    clusterRadiusM: opts.clusterRadiusM,
    densityRadiusM: opts.densityRadiusM,
    gameSize: opts.gameSize,
    maxStationsPerCluster: opts.maxStationsPerCluster,
    waterSubtract: opts.waterSubtract,
  };
  const { rows, stats } = generate({
    polygon,
    poisElements,
    waterRings,
    exclRings,
    playingWindow,
    settings,
  });

  // Status logging — mirrors Python stderr lines (best-effort, not parity-checked).
  if (stats.gameSize !== null) {
    process.stderr.write(`Game size: ${stats.gameSize} (${stats.gameSizeSource})\n`);
  }
  process.stderr.write(`Cluster radius: ${stats.clusterRadiusM.toFixed(0)}m (${stats.radiusSource})\n`);
  const transitClause = opts.includeTransitStations
    ? `${stats.candidateTransit} real transit stations (always included)`
    : "transit stations skipped (--no-include-transit-stations)";
  process.stderr.write(
    `Recognized ${stats.candidateCount} candidates: ` +
    `${stats.candidatePois} POIs (open during play: ${stats.candidateOpen}, ` +
    `closed: ${stats.candidateClosed}, hours unknown: ${stats.candidateUnknown}); ` +
    `${transitClause}\n`,
  );
  const capNote = stats.maxPerCluster
    ? `, cap ${stats.maxPerCluster}/cluster (${stats.capSource})`
    : ", no cap";
  const transitNote = stats.keptTransit
    ? ` (${stats.keptPoi} POI + ${stats.keptTransit} real transit)`
    : "";
  process.stderr.write(
    `Selected ${stats.keptCount} stations${transitNote} across ${stats.clusterCount} clusters ` +
    `(intra-cluster ≥ ${stats.minStationSpacingM.toFixed(0)}m, ` +
    `cluster radius ≤ ${stats.clusterRadiusM.toFixed(0)}m [${stats.radiusSource}]${capNote}); ` +
    `${stats.rejectedCount} candidates rejected\n`,
  );

  // Output.
  const outDir = opts.outputDir ? resolve(opts.outputDir) : DEFAULT_OUTPUT_DIR;
  await mkdir(outDir, { recursive: true });
  const stem = opts.noTimestamp
    ? opts.name
    : `${opts.name}-${new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z")}`;
  const csvPath = join(outDir, `${stem}.csv`);
  const kmlPath = join(outDir, `${stem}.kml`);
  const generatedAt = opts.noTimestamp
    ? "fixture"
    : new Date().toISOString().replace(/\.\d+Z$/, "+00:00");
  await writeFile(csvPath, writeCSV(rows), "utf8");
  await writeFile(kmlPath, writeKML({ layerName: opts.name, rows, generatedAt }), "utf8");
  process.stderr.write(`Wrote ${csvPath}\n`);
  process.stderr.write(`Wrote ${kmlPath}\n`);
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e.stack ?? e.message}\n`);
  process.exit(1);
});
