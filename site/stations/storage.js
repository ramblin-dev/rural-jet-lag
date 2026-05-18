// localStorage adapter. All values are JSON-stringified under namespaced
// keys. The Overpass response cache is keyed by a stable hash of the
// play-area polygon ring, so editing the play area invalidates the cache
// automatically.

const NS = "rural-jet-lag.vehicle-stations.";

export function loadJSON(key, fallback = null) {
  try {
    const raw = localStorage.getItem(NS + key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function saveJSON(key, value) {
  try {
    localStorage.setItem(NS + key, JSON.stringify(value));
  } catch (e) {
    // Most likely QuotaExceededError — Overpass cache for a large polygon
    // may push past the ~5 MB localStorage limit. Surface to the console
    // so the user can clear it; not worth a modal.
    console.warn("localStorage write failed:", e);
  }
}

export function removeKey(key) {
  localStorage.removeItem(NS + key);
}

// Stable, small hash of a polygon ring — collision-resistant enough for
// invalidating a per-polygon cache (not for security). Uses a 32-bit FNV-1a
// over the JSON form.
export function polygonHash(polygon) {
  const s = JSON.stringify(polygon);
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i += 1) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, "0");
}
