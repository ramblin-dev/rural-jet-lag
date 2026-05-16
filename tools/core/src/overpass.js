// Overpass query construction. Network I/O stays in per-platform callers
// (Node fetch in the CLI, browser fetch in the site).

import {
  OVERPASS_TIMEOUT_SEC,
  POI_CATEGORIES,
  TRANSIT_STATION_CATEGORIES,
  WATER_TAG_FILTERS,
} from "./constants.js";

// Polygon is a closed ring of [lat, lon] pairs.
function polyString(polygon) {
  return polygon.map(([lat, lon]) => `${lat} ${lon}`).join(" ");
}

export function buildOverpassQuery(polygon, { includeTransit = true } = {}) {
  const poly = polyString(polygon);
  const categories = includeTransit
    ? [...TRANSIT_STATION_CATEGORIES, ...POI_CATEGORIES]
    : POI_CATEGORIES;
  const seen = new Set();
  const parts = [];
  for (const [, key, value] of categories) {
    const k = `${key}=${value}`;
    if (seen.has(k)) continue;
    seen.add(k);
    const f = `["${key}"="${value}"]`;
    parts.push(`  node${f}(poly:"${poly}");`);
    parts.push(`  way${f}(poly:"${poly}");`);
    parts.push(`  relation${f}(poly:"${poly}");`);
  }
  return `[out:json][timeout:${OVERPASS_TIMEOUT_SEC}];\n(\n${parts.join("\n")}\n);\nout center tags;`;
}

export function buildWaterQuery(polygon) {
  const poly = polyString(polygon);
  const parts = WATER_TAG_FILTERS.map(
    ([key, value]) => `  way["${key}"="${value}"](poly:"${poly}");`,
  );
  return `[out:json][timeout:${OVERPASS_TIMEOUT_SEC}];\n(\n${parts.join("\n")}\n);\nout geom;`;
}

// Parse the water-polygon response into a list of closed [lat, lon] rings.
// Mirrors old-tools query_water_polygons's filter logic — skip rings with
// < 3 points; auto-close if not already closed; ignore multipolygon
// relations (way-level coverage is good enough; see the Python comment).
export function parseWaterRings(elements) {
  const rings = [];
  for (const el of elements) {
    const geom = el.geometry ?? [];
    if (geom.length < 3) continue;
    const ring = geom.map((g) => [g.lat, g.lon]);
    const [lat0, lon0] = ring[0];
    const [latN, lonN] = ring[ring.length - 1];
    if (lat0 !== latN || lon0 !== lonN) ring.push([lat0, lon0]);
    rings.push(ring);
  }
  return rings;
}
