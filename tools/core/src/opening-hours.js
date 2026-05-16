// Playing-window parsing + OSM opening_hours evaluation.
// Mirrors old-tools/generate_vehicle_stations.py:is_open_during_play.

import OpeningHoursLib from "opening_hours";
import { DAY_NAME_TO_INT } from "./constants.js";

// Returns { startMin, endMin } as minutes since midnight.
export function parsePlayingHours(spec) {
  const s = spec.trim().toLowerCase();
  if (!s.includes("-")) {
    throw new Error(`--playing-hours must contain '-', got '${spec}'`);
  }
  const [startS, endS] = s.split("-", 2).map((p) => p.trim());
  return { startMin: parseOneTime(startS), endMin: parseOneTime(endS) };
}

function parseOneTime(raw) {
  let s = raw.trim().toLowerCase().replace(/\s+/g, "");
  let suffix = "";
  if (s.endsWith("am") || s.endsWith("pm")) {
    suffix = s.slice(-2);
    s = s.slice(0, -2);
  }
  let hour;
  let minute;
  if (s.includes(":")) {
    const [hS, mS] = s.split(":", 2);
    hour = Number.parseInt(hS, 10);
    minute = Number.parseInt(mS, 10);
  } else {
    hour = Number.parseInt(s, 10);
    minute = 0;
  }
  if (suffix === "pm" && hour < 12) hour += 12;
  else if (suffix === "am" && hour === 12) hour = 0;
  if (!(hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59)) {
    throw new Error(`invalid time-of-day: '${s}'`);
  }
  return hour * 60 + minute;
}

// Returns a sorted tuple of weekday ints (0=Mon … 6=Sun).
export function parsePlayingDays(spec) {
  const parts = spec.split(",").map((p) => p.trim().toLowerCase()).filter(Boolean);
  if (parts.length === 0) {
    throw new Error("--playing-days-of-week must list at least one day");
  }
  const out = new Set();
  for (const p of parts) {
    if (!(p in DAY_NAME_TO_INT)) {
      throw new Error(`unknown day name '${p}'; use mon/tue/.../sun`);
    }
    out.add(DAY_NAME_TO_INT[p]);
  }
  return [...out].sort((a, b) => a - b);
}

export function buildPlayingWindow({ hoursSpec, daysSpec }) {
  const { startMin, endMin } = parsePlayingHours(hoursSpec);
  const days = parsePlayingDays(daysSpec);
  return { startMin, endMin, days };
}

// Returns true if open at any sample time inside the playing window on any
// playing day; false if known closed throughout; null if the spec is absent
// or unparseable. Sample times: start, midpoint, end of the window.
export function isOpenDuringPlay(spec, window) {
  if (!spec) return null;
  let oh;
  try {
    oh = new OpeningHoursLib(spec);
  } catch {
    return null;
  }
  // Anchor to the Monday of the current week so weekday math is local-tz safe.
  const today = new Date();
  const monday = new Date(today);
  // JS getDay: 0=Sun .. 6=Sat. Python weekday: 0=Mon .. 6=Sun. Convert.
  const todayPyDow = (today.getDay() + 6) % 7;
  monday.setDate(today.getDate() - todayPyDow);
  monday.setHours(0, 0, 0, 0);

  const { startMin, endMin, days } = window;
  const midMin = Math.floor((startMin + endMin) / 2);
  const sampleMinutes = [startMin, midMin, endMin];

  for (const dayInt of days) {
    const date = new Date(monday);
    date.setDate(monday.getDate() + dayInt);
    for (const tMin of sampleMinutes) {
      const probe = new Date(date);
      probe.setHours(Math.floor(tMin / 60), tMin % 60, 0, 0);
      try {
        if (oh.getState(probe)) return true;
      } catch {
        return null;
      }
    }
  }
  return false;
}
