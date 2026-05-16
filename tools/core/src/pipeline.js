// Orchestrator. Pure (no I/O): takes the polygon + already-fetched Overpass
// responses + settings, returns the generated rows plus stats. Both the
// Node CLI and the browser site call this same function — they only differ
// in how they fetch Overpass and where they write output.

import { computePlayArea } from "./area.js";
import { autoTuneCap, filterTwoTier } from "./cluster.js";
import {
  CLUSTER_RADIUS_M,
  DENSITY_RADIUS_M,
  GAME_SIZE_AREA_FLOOR_KM2,
  GAME_SIZE_STATION_BANDS,
  HIDING_ZONE_RADIUS_M_BY_GAME_SIZE,
  MAX_STATIONS_PER_CLUSTER,
  MIN_STATION_SPACING_M,
  TRANSIT_CATEGORY_LABELS,
} from "./constants.js";
import { countNearby, waitRangeForDensity } from "./density.js";
import { parsePOIs } from "./pois.js";

export function inferGameSize(areaKm2) {
  if (areaKm2 >= GAME_SIZE_AREA_FLOOR_KM2.L) return "L";
  if (areaKm2 >= GAME_SIZE_AREA_FLOOR_KM2.M) return "M";
  return "S";
}

// settings shape (all optional; nullish = use default / auto):
//   { minStationSpacingM, clusterRadiusM, densityRadiusM, gameSize,
//     maxStationsPerCluster, waterSubtract, includeTransitStations }
// inputs:
//   polygon         — closed [lat, lon] ring
//   poisElements    — raw Overpass response elements for the POI query
//   waterRings      — already-parsed [lat, lon] rings (use parseWaterRings)
//   exclRings       — user-drawn exclusion rings, [lat, lon] each
//   playingWindow   — { startMin, endMin, days } (from buildPlayingWindow)
export function generate({
  polygon,
  poisElements,
  waterRings = [],
  exclRings = [],
  playingWindow,
  settings = {},
}) {
  const minStationSpacingM = settings.minStationSpacingM ?? MIN_STATION_SPACING_M;
  const densityRadiusM = settings.densityRadiusM ?? DENSITY_RADIUS_M;
  const waterSubtract = settings.waterSubtract ?? true;

  // Resolve game size.
  let gameSize = settings.gameSize ?? null;
  let gameSizeSource = null;
  let areaInfo = null;
  if (gameSize !== null) {
    gameSizeSource = "explicit";
  } else {
    areaInfo = computePlayArea(polygon, {
      waterRings: waterSubtract ? waterRings : [],
      extraExclRings: exclRings,
    });
    gameSize = inferGameSize(areaInfo.netKm2);
    let chain = `${areaInfo.grossKm2.toFixed(0)} km² gross`;
    if (areaInfo.waterKm2 > 0) chain += ` − ${areaInfo.waterKm2.toFixed(0)} km² water`;
    if (areaInfo.userExclKm2 > 0) chain += ` − ${areaInfo.userExclKm2.toFixed(0)} km² user-excluded`;
    if (areaInfo.waterKm2 > 0 || areaInfo.userExclKm2 > 0) {
      chain += ` = ${areaInfo.netKm2.toFixed(0)} km² net`;
    }
    gameSizeSource = `inferred from area (${chain})`;
  }

  // Resolve cluster radius.
  let clusterRadiusM;
  let radiusSource;
  if (settings.clusterRadiusM != null) {
    clusterRadiusM = settings.clusterRadiusM;
    radiusSource = "explicit";
  } else if (gameSize !== null) {
    clusterRadiusM = HIDING_ZONE_RADIUS_M_BY_GAME_SIZE[gameSize];
    radiusSource = `game-size ${gameSize}`;
  } else {
    clusterRadiusM = CLUSTER_RADIUS_M;
    radiusSource = "default";
  }
  if (clusterRadiusM <= minStationSpacingM) {
    throw new Error("clusterRadiusM must be greater than minStationSpacingM");
  }

  // Parse POIs.
  const candidates = parsePOIs(poisElements, playingWindow);

  // Resolve cap.
  let maxPerCluster;
  let capSource;
  let kept;
  let rejected;
  let capTrail = null;
  let capInBand = null;
  if (settings.maxStationsPerCluster != null) {
    maxPerCluster = settings.maxStationsPerCluster === 0 ? null : settings.maxStationsPerCluster;
    capSource = "explicit";
    ({ kept, rejected } = filterTwoTier(candidates, {
      minStationM: minStationSpacingM,
      clusterRadiusM,
      maxPerCluster,
    }));
  } else if (gameSize !== null) {
    const targetBand = GAME_SIZE_STATION_BANDS[gameSize];
    const tuned = autoTuneCap(candidates, {
      minStationM: minStationSpacingM,
      clusterRadiusM,
      targetBand,
    });
    ({ kept, rejected, cap: maxPerCluster, trail: capTrail } = tuned);
    const [lo, hi] = targetBand;
    capInBand = kept.length >= lo && kept.length <= hi;
    const hiStr = hi === Infinity ? "∞" : `${hi.toFixed(0)}`;
    capSource =
      `auto-tuned for game-size ${gameSize} (target ${lo.toFixed(0)}–${hiStr} stations, ` +
      `swept ${capTrail[0][0]}..${capTrail[capTrail.length - 1][0]})`;
  } else {
    maxPerCluster = MAX_STATIONS_PER_CLUSTER;
    capSource = "default";
    ({ kept, rejected } = filterTwoTier(candidates, {
      minStationM: minStationSpacingM,
      clusterRadiusM,
      maxPerCluster,
    }));
  }

  // Build output rows.
  const rows = kept.map(({ poi, clusterId }) => {
    const nearby = countNearby(poi, candidates, densityRadiusM);
    const { min, max, tier } = waitRangeForDensity(nearby);
    const openStatus =
      poi.openDuringPlay === true ? "yes"
      : poi.openDuringPlay === false ? "no"
      : "unknown";
    return {
      name: poi.name,
      category: poi.category,
      cluster_id: clusterId,
      latitude: poi.lat.toFixed(6),
      longitude: poi.lon.toFixed(6),
      wait_min_minutes: min,
      wait_max_minutes: max,
      density_tier: tier,
      nearby_poi_count: nearby,
      open_during_play: openStatus,
      opening_hours: poi.openingHours ?? "",
      osm_type: poi.osmType,
      osm_id: poi.osmId,
    };
  });

  const transitKept = kept.filter(({ poi }) => TRANSIT_CATEGORY_LABELS.has(poi.category)).length;
  const clusterCount = new Set(kept.map(({ clusterId }) => clusterId)).size;
  const candidateTransit = candidates.filter((p) => TRANSIT_CATEGORY_LABELS.has(p.category)).length;
  const candidatePois = candidates.length - candidateTransit;
  const nOpen = candidates.filter((p) => !TRANSIT_CATEGORY_LABELS.has(p.category) && p.openDuringPlay === true).length;
  const nClosed = candidates.filter((p) => !TRANSIT_CATEGORY_LABELS.has(p.category) && p.openDuringPlay === false).length;
  const nUnknown = candidates.filter((p) => !TRANSIT_CATEGORY_LABELS.has(p.category) && p.openDuringPlay == null).length;

  return {
    rows,
    rejected,
    stats: {
      gameSize,
      gameSizeSource,
      areaInfo,
      clusterRadiusM,
      radiusSource,
      minStationSpacingM,
      densityRadiusM,
      maxPerCluster,
      capSource,
      capTrail,
      capInBand,
      candidateCount: candidates.length,
      candidatePois,
      candidateTransit,
      candidateOpen: nOpen,
      candidateClosed: nClosed,
      candidateUnknown: nUnknown,
      clusterCount,
      keptCount: kept.length,
      keptPoi: kept.length - transitKept,
      keptTransit: transitKept,
      rejectedCount: rejected.length,
    },
  };
}
