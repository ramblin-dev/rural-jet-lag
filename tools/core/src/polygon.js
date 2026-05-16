// GeoJSON ring extraction. Returns a closed ring of [lat, lon] pairs.
// Accepts the same shapes the Python version does (Feature, FeatureCollection,
// Polygon, MultiPolygon, LineString) so geojson.io's line-tool exports work
// directly.

function extractGeoJSONRing(data) {
  if (data.type === "FeatureCollection") {
    for (const feat of data.features ?? []) {
      try {
        return extractGeoJSONRing(feat);
      } catch {
        // try next
      }
    }
    throw new Error("no usable geometry found in FeatureCollection");
  }
  if (data.type === "Feature") return extractGeoJSONRing(data.geometry);
  if (data.type === "Polygon") return data.coordinates[0];
  if (data.type === "MultiPolygon") return data.coordinates[0][0];
  if (data.type === "LineString") return data.coordinates;
  throw new Error(`unsupported GeoJSON type: ${data.type}`);
}

// Returns a closed ring of [lat, lon] pairs. Input is either a parsed
// GeoJSON object or the raw text of a plain-text "lat,lon per line" file
// (CLI only — the site never sees plain-text input).
export function loadPolygonFromGeoJSON(data) {
  const ring = extractGeoJSONRing(data);
  // GeoJSON is [lon, lat]; we use [lat, lon].
  const coords = ring.map(([lon, lat]) => [lat, lon]);
  return closeRing(coords);
}

export function loadPolygonFromPlainText(text) {
  const coords = [];
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.split("#", 1)[0].trim();
    if (!line) continue;
    const [latS, lonS] = line.split(",").map((s) => s.trim());
    coords.push([Number(latS), Number(lonS)]);
  }
  return closeRing(coords);
}

function closeRing(coords) {
  if (coords.length < 3) {
    throw new Error(`polygon must have at least 3 points, got ${coords.length}`);
  }
  const [lat0, lon0] = coords[0];
  const [latN, lonN] = coords[coords.length - 1];
  if (lat0 !== latN || lon0 !== lonN) coords.push([lat0, lon0]);
  return coords;
}
