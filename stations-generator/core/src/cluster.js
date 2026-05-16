// Seed-and-grow clustering + intra-cluster spacing filter + per-cluster cap.
// Mirrors old-tools/generate_vehicle_stations.py:filter_two_tier exactly so
// the parity test passes.

import {
  AUTO_TUNE_CAP_RANGE,
  TRANSIT_CATEGORY_LABELS,
} from "./constants.js";
import { haversineM } from "./geo.js";

function poiKey(p) {
  return `${p.osmType}/${p.osmId}`;
}

function comparePriority(a, b) {
  if (a.priority !== b.priority) return a.priority - b.priority;
  // Python: name.lower(); JS localeCompare is locale-dependent. Use
  // case-insensitive lex sort with the C locale to match Python's
  // .lower() ordering on ASCII content (the only thing that matters for
  // the parity fixture; non-ASCII names tie-break the same in both langs
  // since both compare on lowercased UCS code points).
  const an = a.name.toLowerCase();
  const bn = b.name.toLowerCase();
  if (an < bn) return -1;
  if (an > bn) return 1;
  return 0;
}

export function filterTwoTier(pois, { minStationM, clusterRadiusM, maxPerCluster = null }) {
  // Step 1: seed-and-grow clustering.
  const orderedByPriority = [...pois].sort(comparePriority);
  const clusterIdOf = new Map();
  const clusterMembers = new Map();
  let nextId = 1;
  for (const seed of orderedByPriority) {
    if (clusterIdOf.has(poiKey(seed))) continue;
    const cid = nextId;
    nextId += 1;
    const members = [];
    for (const p of orderedByPriority) {
      const k = poiKey(p);
      if (clusterIdOf.has(k)) continue;
      if (haversineM(seed.lat, seed.lon, p.lat, p.lon) <= clusterRadiusM) {
        clusterIdOf.set(k, cid);
        members.push(p);
      }
    }
    clusterMembers.set(cid, members);
  }

  // Step 2: intra-cluster spacing filter + per-cluster cap.
  const kept = [];
  const rejected = [];
  const sortedCids = [...clusterMembers.keys()].sort((a, b) => a - b);
  for (const cid of sortedCids) {
    const ordered = [...clusterMembers.get(cid)].sort(comparePriority);
    const keptInCluster = [];
    let nonTransitKept = 0;
    let capHit = false;
    for (const p of ordered) {
      const isTransit = TRANSIT_CATEGORY_LABELS.has(p.category);
      if (capHit && !isTransit) {
        rejected.push({ poi: p, clusterId: cid, reason: "cluster_cap", conflictWith: null });
        continue;
      }
      let blocker = null;
      for (const k of keptInCluster) {
        if (haversineM(p.lat, p.lon, k.lat, k.lon) < minStationM) {
          blocker = k;
          break;
        }
      }
      if (blocker) {
        rejected.push({ poi: p, clusterId: cid, reason: "spacing", conflictWith: blocker.name });
        continue;
      }
      keptInCluster.push(p);
      if (!isTransit) {
        nonTransitKept += 1;
        if (maxPerCluster !== null && nonTransitKept >= maxPerCluster) capHit = true;
      }
    }
    for (const p of keptInCluster) kept.push({ poi: p, clusterId: cid });
  }
  return { kept, rejected };
}

// Sweep cap values in capRange and return the smallest cap whose station
// count falls inside targetBand. If no cap fits, return the one whose
// count is closest to the band.
export function autoTuneCap(pois, { minStationM, clusterRadiusM, targetBand, capRange = AUTO_TUNE_CAP_RANGE }) {
  const [lo, hi] = targetBand;
  let best = null;
  const trail = [];
  for (const cap of capRange) {
    const { kept, rejected } = filterTwoTier(pois, {
      minStationM,
      clusterRadiusM,
      maxPerCluster: cap,
    });
    const count = kept.length;
    trail.push([cap, count]);
    if (count >= lo && count <= hi) {
      return { kept, rejected, cap, trail };
    }
    const diff = Math.max(lo - count, 0, count - hi);
    if (best === null || diff < best.diff) {
      best = { diff, cap, count, kept, rejected };
    }
  }
  return { kept: best.kept, rejected: best.rejected, cap: best.cap, trail };
}
