import L from "leaflet";
import "leaflet-draw";
import {
  buildOverpassQuery,
  buildPlayingWindow,
  buildWaterQuery,
  generate,
  parseWaterRings,
  writeKML,
} from "@rural-jet-lag/core";
import { fetchOverpass } from "./overpass-browser.js";
import { loadJSON, polygonHash, removeKey, saveJSON } from "./storage.js";

// ----- DOM refs --------------------------------------------------------
const statusText = document.getElementById("status-text");
const settingsSection = document.getElementById("settings");
const downloadSection = document.getElementById("download");
const resetSection = document.getElementById("reset");
const drawHint = document.getElementById("draw-hint");
const downloadBtn = document.getElementById("download-btn");
const drawModeRadios = document.querySelectorAll('input[name="draw-mode"]');
const settingInputs = settingsSection.querySelectorAll("input, select");

// ----- State -----------------------------------------------------------
const state = {
  playPolygon: null,       // closed [lat, lon] ring or null
  exclPolygons: [],        // list of closed [lat, lon] rings
  settings: {
    gameSize: "",
    clusterRadiusM: "",
    maxStationsPerCluster: "",
    minStationSpacingM: 300,
    densityRadiusM: 1609,
    playingHours: "7am-7pm",
    playingDaysOfWeek: "sat,sun",
    waterSubtract: true,
    includeTransitStations: true,
  },
  stationsKml: null,       // last generated KML text
  drawMode: "play",
};

// Hydrate from localStorage.
const saved = loadJSON("session", null);
if (saved) {
  Object.assign(state, saved);
  // Validate shape; older saves may lack fields.
  state.exclPolygons ??= [];
  state.settings ??= {};
}

function persist() {
  saveJSON("session", {
    playPolygon: state.playPolygon,
    exclPolygons: state.exclPolygons,
    settings: state.settings,
    drawMode: state.drawMode,
  });
}

// ----- Map setup -------------------------------------------------------
const map = L.map("map").setView([43.55, -96.72], 11);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  maxZoom: 19,
}).addTo(map);

const playGroup = new L.FeatureGroup().addTo(map);
const exclGroup = new L.FeatureGroup().addTo(map);
const stationGroup = new L.FeatureGroup().addTo(map);

const PLAY_STYLE = { color: "#2c5fa8", weight: 2, fillColor: "#3498db", fillOpacity: 0.15 };
const EXCL_STYLE = { color: "#c0392b", weight: 2, fillColor: "#e74c3c", fillOpacity: 0.25 };

function addPlayLayer(latlngs) {
  playGroup.clearLayers();
  L.polygon(latlngs, PLAY_STYLE).addTo(playGroup);
}
function addExclLayer(latlngs) {
  L.polygon(latlngs, EXCL_STYLE).addTo(exclGroup);
}

// Restore drawn polygons from saved state.
if (state.playPolygon) addPlayLayer(state.playPolygon);
for (const ring of state.exclPolygons) addExclLayer(ring);
if (state.playPolygon) {
  map.fitBounds(L.polygon(state.playPolygon).getBounds(), { padding: [20, 20] });
}

// Leaflet.draw controls. The "edit/delete" toolbar operates over the
// currently-selected group, which changes with the draw-mode radio.
const drawControl = new L.Control.Draw({
  draw: {
    polygon: { allowIntersection: false, shapeOptions: PLAY_STYLE, showArea: true },
    polyline: false,
    rectangle: false,
    circle: false,
    marker: false,
    circlemarker: false,
  },
  edit: { featureGroup: playGroup, edit: false },
});
map.addControl(drawControl);

function setDrawMode(mode) {
  state.drawMode = mode;
  // Sync the radio buttons (they may be stale after a refresh that
  // restored drawMode from localStorage but left the HTML default checked).
  drawModeRadios.forEach((r) => { r.checked = r.value === mode; });
  // Swap which group the toolbar operates on, and the polygon's draw colour.
  const opts = mode === "excl" ? EXCL_STYLE : PLAY_STYLE;
  drawControl.setDrawingOptions({ polygon: { shapeOptions: opts } });
  map.removeControl(drawControl);
  drawControl.options.edit.featureGroup = mode === "excl" ? exclGroup : playGroup;
  map.addControl(drawControl);
  drawHint.textContent = mode === "play"
    ? "Click the polygon tool on the map to draw your play area."
    : "Click the polygon tool to draw an exclusion zone. Add as many as you like.";
  persist();
}

drawModeRadios.forEach((r) => r.addEventListener("change", (e) => {
  if (e.target.checked) setDrawMode(e.target.value);
}));

map.on(L.Draw.Event.CREATED, (e) => {
  const ring = e.layer.getLatLngs()[0].map((ll) => [ll.lat, ll.lng]);
  ring.push(ring[0]); // close
  if (state.drawMode === "play") {
    state.playPolygon = ring;
    addPlayLayer(ring);
    // New play area invalidates the cached Overpass response.
    invalidateOverpassCache();
  } else {
    if (!state.playPolygon) {
      // Drawing an exclusion without a play area is meaningless; reset radio.
      exclGroup.clearLayers();
      drawModeRadios.forEach((r) => { r.checked = r.value === "play"; });
      setDrawMode("play");
      alert("Draw your play area first.");
      return;
    }
    state.exclPolygons.push(ring);
    addExclLayer(ring);
  }
  persist();
  scheduleRegenerate();
});

map.on(L.Draw.Event.DELETED, (e) => {
  // Re-derive both groups from layers still on the map; can't tell from
  // the event which originals were deleted.
  if (drawControl.options.edit.featureGroup === playGroup) {
    if (playGroup.getLayers().length === 0) {
      // Play area deleted → cascade-clear everything.
      state.playPolygon = null;
      state.exclPolygons = [];
      exclGroup.clearLayers();
      stationGroup.clearLayers();
      invalidateOverpassCache();
      removeKey("stations");
    }
  } else {
    state.exclPolygons = exclGroup.getLayers().map((l) =>
      l.getLatLngs()[0].map((ll) => [ll.lat, ll.lng]).concat([
        [l.getLatLngs()[0][0].lat, l.getLatLngs()[0][0].lng],
      ]),
    );
  }
  persist();
  scheduleRegenerate();
});

// ----- Settings binding ------------------------------------------------
function applySettingsToForm() {
  for (const input of settingInputs) {
    const k = input.name;
    if (k in state.settings) {
      if (input.type === "checkbox") input.checked = !!state.settings[k];
      else input.value = state.settings[k] ?? "";
    }
  }
}
function readSettingsFromForm() {
  const next = { ...state.settings };
  for (const input of settingInputs) {
    const k = input.name;
    if (input.type === "checkbox") next[k] = input.checked;
    else next[k] = input.value;
  }
  state.settings = next;
}
applySettingsToForm();
settingInputs.forEach((input) => input.addEventListener("change", () => {
  readSettingsFromForm();
  persist();
  scheduleRegenerate();
}));

// ----- Overpass cache + regenerate -------------------------------------
function overpassCacheKey() {
  if (!state.playPolygon) return null;
  return `overpass.${polygonHash(state.playPolygon)}`;
}
function invalidateOverpassCache() {
  // Drop ALL overpass.* cache entries; only the current polygon's is
  // relevant and the old one would just leak storage.
  for (let i = localStorage.length - 1; i >= 0; i -= 1) {
    const k = localStorage.key(i);
    if (k && k.includes("vehicle-stations.overpass.")) localStorage.removeItem(k);
  }
}

async function loadOverpass(polygon, { includeTransit, includeWater }) {
  const cacheKey = `overpass.${polygonHash(polygon)}`;
  const cached = loadJSON(cacheKey, null);
  if (cached) return cached;
  setStatus("Fetching POIs from Overpass…");
  const poisQuery = buildOverpassQuery(polygon, { includeTransit });
  const poisElements = await fetchOverpass(poisQuery);
  let waterElements = [];
  if (includeWater) {
    setStatus(`Fetched ${poisElements.length} POIs. Fetching water polygons…`);
    waterElements = await fetchOverpass(buildWaterQuery(polygon));
  }
  const payload = { poisElements, waterElements };
  saveJSON(cacheKey, payload);
  return payload;
}

let regenToken = 0;
function scheduleRegenerate() {
  if (!state.playPolygon) {
    stationGroup.clearLayers();
    setStatus("No play area drawn yet.");
    settingsSection.hidden = true;
    downloadSection.hidden = true;
    resetSection.hidden = true;
    return;
  }
  settingsSection.hidden = false;
  resetSection.hidden = false;
  const myToken = ++regenToken;
  regenerate(myToken).catch((e) => {
    if (myToken === regenToken) setStatus(`Error: ${e.message}`);
    console.error(e);
  });
}

function settingToNumber(v) {
  if (v === "" || v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

async function regenerate(token) {
  const s = state.settings;
  // Game size influences whether we need the water query at all.
  const needWater = (s.gameSize === "" || s.gameSize == null) && s.waterSubtract;
  const { poisElements, waterElements } = await loadOverpass(state.playPolygon, {
    includeTransit: s.includeTransitStations,
    includeWater: needWater,
  });
  if (token !== regenToken) return; // a newer regenerate started
  const waterRings = parseWaterRings(waterElements ?? []);
  const playingWindow = buildPlayingWindow({
    hoursSpec: s.playingHours, daysSpec: s.playingDaysOfWeek,
  });
  const settings = {
    minStationSpacingM: settingToNumber(s.minStationSpacingM) ?? 300,
    densityRadiusM: settingToNumber(s.densityRadiusM) ?? 1609,
    clusterRadiusM: settingToNumber(s.clusterRadiusM),
    gameSize: s.gameSize || null,
    maxStationsPerCluster: settingToNumber(s.maxStationsPerCluster),
    waterSubtract: !!s.waterSubtract,
  };
  const { rows, stats } = generate({
    polygon: state.playPolygon,
    poisElements,
    waterRings,
    exclRings: state.exclPolygons,
    playingWindow,
    settings,
  });

  // Render stations on the map.
  stationGroup.clearLayers();
  for (const r of rows) {
    L.circleMarker([Number(r.latitude), Number(r.longitude)], {
      radius: 5, color: "#222", weight: 1, fillColor: "#f1c40f", fillOpacity: 0.9,
    })
      .bindPopup(
        `<strong>${escapeHtml(r.name)}</strong><br>` +
        `${r.category} · cluster ${r.cluster_id}<br>` +
        `Wait: ${r.wait_min_minutes}–${r.wait_max_minutes} min (${r.density_tier})`,
      )
      .addTo(stationGroup);
  }

  const summary =
    `${stats.keptCount} stations` +
    (stats.keptTransit ? ` (${stats.keptPoi} POI + ${stats.keptTransit} real transit)` : "") +
    ` across ${stats.clusterCount} clusters.` +
    (stats.gameSize ? `\nGame size: ${stats.gameSize} (${stats.gameSizeSource}).` : "") +
    `\nCluster radius: ${stats.clusterRadiusM.toFixed(0)} m (${stats.radiusSource}).` +
    (stats.maxPerCluster
      ? `\nCap: ${stats.maxPerCluster}/cluster (${stats.capSource}).`
      : "\nNo per-cluster cap.");
  setStatus(summary);

  // Build the KML once and stash it for the download button.
  state.stationsKml = writeKML({
    layerName: "vehicle-stations",
    rows,
    generatedAt: new Date().toISOString().replace(/\.\d+Z$/, "+00:00"),
  });
  downloadSection.hidden = rows.length === 0;
}

function setStatus(text) { statusText.textContent = text; }

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

// ----- Download --------------------------------------------------------
downloadBtn.addEventListener("click", () => {
  if (!state.stationsKml) return;
  const blob = new Blob([state.stationsKml], { type: "application/vnd.google-earth.kml+xml" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "vehicle-stations.kml";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

// Kick off initial render.
setDrawMode(state.drawMode || "play");
if (state.playPolygon) scheduleRegenerate();
