// Geometric helpers. All polygon rings are arrays of [lat, lon] pairs
// (closed — first == last) to match the Python reference.

const EARTH_RADIUS_M = 6371000.0;

export function haversineM(lat1, lon1, lat2, lon2) {
  const p1 = (lat1 * Math.PI) / 180;
  const p2 = (lat2 * Math.PI) / 180;
  const dp = ((lat2 - lat1) * Math.PI) / 180;
  const dl = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dp / 2) ** 2 +
    Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(a));
}

// Simple unweighted centroid of a closed ring of [lat, lon] pairs.
export function polygonCentroid(ring) {
  const n = ring[0][0] === ring[ring.length - 1][0] &&
            ring[0][1] === ring[ring.length - 1][1]
    ? ring.length - 1
    : ring.length;
  let latSum = 0;
  let lonSum = 0;
  for (let i = 0; i < n; i += 1) {
    latSum += ring[i][0];
    lonSum += ring[i][1];
  }
  return [latSum / n, lonSum / n];
}

// Equirectangular projection of a [lat, lon] ring to local (x, y) km.
// Matches old-tools/generate_vehicle_stations.py:project_ring_to_km — same
// 111 km/° constant and same cos(lat0) scaling — so the regression test's area
// numbers come out identical.
export function projectRingToKm(ring, lat0, lon0) {
  const cosLat0 = Math.cos((lat0 * Math.PI) / 180);
  return ring.map(([lat, lon]) => [
    (lon - lon0) * 111.0 * cosLat0,
    (lat - lat0) * 111.0,
  ]);
}

// Shoelace area of a 2D polygon (signed, returns absolute value).
// Ring may be open or closed; first/last coincidence is handled.
export function shoelaceArea(xy) {
  const n = xy[0][0] === xy[xy.length - 1][0] &&
            xy[0][1] === xy[xy.length - 1][1]
    ? xy.length - 1
    : xy.length;
  let s = 0;
  for (let i = 0; i < n; i += 1) {
    const [x1, y1] = xy[i];
    const [x2, y2] = xy[(i + 1) % n];
    s += x1 * y2 - x2 * y1;
  }
  return Math.abs(s) / 2;
}
