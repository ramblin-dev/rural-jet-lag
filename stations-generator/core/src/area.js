// Play-area calc with optional water + user-exclusion subtraction. Uses
// polygon-clipping in equirectangular-projected space (km units) so the
// area math matches the Python implementation (shapely planar area on
// the same projection). Results carry < 1% distortion up to ~100 km
// across, ~5% at ~500 km — enough resolution to bin into S/M/L tiers.

import polygonClipping from "polygon-clipping";
import {
  polygonCentroid,
  projectRingToKm,
  shoelaceArea,
} from "./geo.js";

// polygon-clipping wants [x, y] rings. Our projectRingToKm already returns
// [x, y] pairs (x = lon-derived, y = lat-derived). Each polygon-clipping
// "polygon" is [outerRing, ...holes]; a multipolygon is a list of those.
function toClipPoly(xyRing) {
  return [xyRing];
}

function multiPolyArea(multi) {
  let total = 0;
  for (const poly of multi) {
    for (const [i, ring] of poly.entries()) {
      const a = shoelaceArea(ring);
      total += i === 0 ? a : -a;
    }
  }
  return total;
}

// playPolygon: closed [lat, lon] ring.
// waterRings: array of closed [lat, lon] rings (from parseWaterRings).
// extraExclRings: array of closed [lat, lon] rings (user-drawn exclusions).
// Returns { grossKm2, netKm2, waterKm2, userExclKm2 }.
export function computePlayArea(playPolygon, { waterRings = [], extraExclRings = [] } = {}) {
  const [lat0, lon0] = polygonCentroid(playPolygon);
  const playXY = projectRingToKm(playPolygon, lat0, lon0);
  const playMulti = [toClipPoly(playXY)];
  const grossKm2 = multiPolyArea(playMulti);

  let waterKm2 = 0;
  let userExclKm2 = 0;
  let excl = null; // polygon-clipping multipoly

  if (waterRings.length) {
    const waterPolys = waterRings.map((r) =>
      toClipPoly(projectRingToKm(r, lat0, lon0)),
    );
    // Union all water polygons, then intersect with play to get the inside-play area.
    const waterUnion = polygonClipping.union(...waterPolys);
    const waterInside = polygonClipping.intersection(playMulti, waterUnion);
    waterKm2 = multiPolyArea(waterInside);
    excl = waterUnion;
  }

  for (const ring of extraExclRings) {
    const userPoly = toClipPoly(projectRingToKm(ring, lat0, lon0));
    const userInside = polygonClipping.intersection(playMulti, [userPoly]);
    userExclKm2 += multiPolyArea(userInside);
    excl = excl ? polygonClipping.union(excl, [userPoly]) : [userPoly];
  }

  let netKm2 = grossKm2;
  if (excl) {
    const net = polygonClipping.difference(playMulti, excl);
    netKm2 = multiPolyArea(net);
  }
  return {
    grossKm2,
    netKm2: Math.max(0, netKm2),
    waterKm2,
    userExclKm2,
  };
}
