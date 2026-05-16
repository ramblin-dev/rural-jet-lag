// Ray-cast point-in-polygon test on a closed ring of [lat, lon] pairs.
// Treats the ring as planar (degree units) — fine for the scale of a
// single play area; not a great fit for polygons that cross the antimeridian
// or include a pole, neither of which appear in this game.

export function pointInRing(lat, lon, ring) {
  let inside = false;
  const n = ring.length - (ring[0][0] === ring[ring.length - 1][0] &&
                           ring[0][1] === ring[ring.length - 1][1] ? 1 : 0);
  for (let i = 0, j = n - 1; i < n; j = i, i += 1) {
    const [latI, lonI] = ring[i];
    const [latJ, lonJ] = ring[j];
    const intersects = ((latI > lat) !== (latJ > lat)) &&
      (lon < ((lonJ - lonI) * (lat - latI)) / (latJ - latI) + lonI);
    if (intersects) inside = !inside;
  }
  return inside;
}

export function pointInAnyRing(lat, lon, rings) {
  for (const r of rings) if (pointInRing(lat, lon, r)) return true;
  return false;
}
