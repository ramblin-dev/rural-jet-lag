import { haversineM } from "./geo.js";

// (minMinutes, maxMinutes, tier) by local POI density. Tier breakpoints
// align with the transit-friction reference table. Tunable.
export function waitRangeForDensity(nearbyCount) {
  if (nearbyCount >= 15) return { min: 5, max: 15, tier: "dense" };
  if (nearbyCount >= 5) return { min: 10, max: 30, tier: "moderate" };
  return { min: 20, max: 60, tier: "sparse" };
}

export function countNearby(poi, candidates, radiusM) {
  let n = 0;
  for (const c of candidates) {
    if (c.osmType === poi.osmType && c.osmId === poi.osmId) continue;
    if (haversineM(poi.lat, poi.lon, c.lat, c.lon) <= radiusM) n += 1;
  }
  return n;
}
