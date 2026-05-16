// Tunables ported from old-tools/generate_vehicle_stations.py. Source of
// truth for the "why" behind these numbers is /vehicle-stations.md and
// /reference/transit-friction.md.

export const OVERPASS_URL = "https://overpass-api.de/api/interpreter";
export const USER_AGENT = "rural-jet-lag/vehicle-stations (github: rural-jet-lag)";
export const OVERPASS_TIMEOUT_SEC = 90;

export const MIN_STATION_SPACING_M = 300;
export const CLUSTER_RADIUS_M = 1000;
export const DENSITY_RADIUS_M = 1609;

export const HIDING_ZONE_RADIUS_M_BY_GAME_SIZE = { S: 402, M: 402, L: 805 };
export const GAME_SIZE_AREA_FLOOR_KM2 = { S: 0.0, M: 259.0, L: 2590.0 };
export const GAME_SIZE_STATION_BANDS = {
  S: [30, 100],
  M: [100, 500],
  L: [500, Infinity],
};
export const AUTO_TUNE_CAP_RANGE = Array.from({ length: 12 }, (_, i) => i + 1);
export const MAX_STATIONS_PER_CLUSTER = 4;

export const DEFAULT_PLAYING_HOURS = "7am-7pm";
export const DEFAULT_PLAYING_DAYS = "sat,sun";
export const CLOSED_PRIORITY_PENALTY = 100;

export const DAY_NAME_TO_INT = {
  mo: 0, mon: 0, monday: 0,
  tu: 1, tue: 1, tues: 1, tuesday: 1,
  we: 2, wed: 2, weds: 2, wednesday: 2,
  th: 3, thu: 3, thurs: 3, thursday: 3,
  fr: 4, fri: 4, friday: 4,
  sa: 5, sat: 5, saturday: 5,
  su: 6, sun: 6, sunday: 6,
};

// (priority, osm_key, osm_value, label). Real transit categories use
// priority 0 — above any POI tier — and are exempted from the per-cluster
// cap and closed-hours penalty (see TRANSIT_CATEGORY_LABELS).
export const TRANSIT_STATION_CATEGORIES = [
  [0, "railway", "station", "train_station"],
  [0, "railway", "halt", "train_halt"],
  [0, "railway", "tram_stop", "tram_stop"],
  [0, "amenity", "bus_station", "bus_station"],
  [0, "amenity", "ferry_terminal", "ferry_terminal"],
  [0, "aerialway", "station", "cable_car_station"],
  [0, "public_transport", "station", "transit_station"],
];

export const POI_CATEGORIES = [
  // Tier 1: low-cost cultural / browseable retail.
  [1, "tourism", "museum", "museum"],
  [1, "tourism", "attraction", "attraction"],
  [1, "shop", "books", "bookstore"],
  [1, "shop", "anime", "comic_store"],
  [1, "shop", "games", "board_game_store"],
  // Tier 2: flexible-visit hangouts.
  [2, "amenity", "cafe", "cafe"],
  [2, "leisure", "amusement_arcade", "arcade"],
  // Tier 3: free-to-browse retail with foot traffic.
  [3, "shop", "mall", "mall"],
  [3, "shop", "department_store", "department_store"],
  // Tier 4: free, comfortable to linger.
  [4, "leisure", "park", "park"],
  [4, "leisure", "nature_reserve", "nature_reserve"],
  [4, "boundary", "national_park", "national_park"],
  [4, "highway", "rest_area", "rest_area"],
  [4, "highway", "services", "rest_area"],
  // Tier 5: in-and-out essentials.
  [5, "shop", "convenience", "convenience_store"],
  [5, "shop", "supermarket", "supermarket"],
  [5, "amenity", "fuel", "gas_station"],
  [5, "amenity", "fast_food", "fast_food"],
  // Tier 6: bars and pubs.
  [6, "amenity", "bar", "bar"],
  [6, "amenity", "pub", "pub"],
  // Tier 7: restaurants.
  [7, "amenity", "restaurant", "restaurant"],
];

export const TRANSIT_CATEGORY_LABELS = new Set(
  TRANSIT_STATION_CATEGORIES.map(([, , , label]) => label),
);

export const ALL_CATEGORIES = [...TRANSIT_STATION_CATEGORIES, ...POI_CATEGORIES];

export const LABEL_BY_KV = new Map(
  ALL_CATEGORIES.map(([, k, v, label]) => [`${k}=${v}`, label]),
);
export const PRIORITY_BY_KV = new Map(
  ALL_CATEGORIES.map(([p, k, v]) => [`${k}=${v}`, p]),
);

// Tags marking a polygon as water / non-playable land cover.
export const WATER_TAG_FILTERS = [
  ["natural", "water"],
  ["natural", "bay"],
  ["waterway", "riverbank"],
  ["waterway", "dock"],
  ["landuse", "reservoir"],
  ["landuse", "basin"],
];
