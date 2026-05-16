// Parse Overpass elements into POI records.

import {
  CLOSED_PRIORITY_PENALTY,
  LABEL_BY_KV,
  PRIORITY_BY_KV,
  TRANSIT_CATEGORY_LABELS,
} from "./constants.js";
import { isOpenDuringPlay } from "./opening-hours.js";

function classify(tags) {
  let best = null;
  for (const [kv, label] of LABEL_BY_KV) {
    const [k, v] = kv.split("=");
    if (tags[k] === v) {
      const p = PRIORITY_BY_KV.get(kv);
      if (best === null || p < best.priority) best = { priority: p, label };
    }
  }
  return best ? { category: best.label, basePriority: best.priority }
              : { category: null, basePriority: 99 };
}

export function parsePOIs(elements, playingWindow) {
  const pois = [];
  const seen = new Set();
  for (const el of elements) {
    const osmType = el.type;
    const osmId = el.id;
    if (osmId === undefined || osmId === null) continue;
    const key = `${osmType}/${osmId}`;
    if (seen.has(key)) continue;
    seen.add(key);

    let lat;
    let lon;
    if (osmType === "node") {
      lat = el.lat;
      lon = el.lon;
    } else {
      const c = el.center ?? {};
      lat = c.lat;
      lon = c.lon;
    }
    if (lat === undefined || lon === undefined) continue;

    const tags = el.tags ?? {};
    const { category, basePriority } = classify(tags);
    if (category === null) continue;
    const name = tags.name ?? `unnamed ${category}`;
    const openingHours = tags.opening_hours ?? null;
    const openDuringPlay = isOpenDuringPlay(openingHours, playingWindow);
    const isTransit = TRANSIT_CATEGORY_LABELS.has(category);
    const priority = (isTransit || openDuringPlay !== false)
      ? basePriority
      : basePriority + CLOSED_PRIORITY_PENALTY;
    pois.push({
      osmType,
      osmId,
      name,
      category,
      priority,
      lat,
      lon,
      openingHours,
      openDuringPlay,
    });
  }
  return pois;
}
