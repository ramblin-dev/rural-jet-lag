// CSV emission. Returns a string. Mirrors Python csv.DictWriter behavior
// with QUOTE_MINIMAL (default): quote a field iff it contains the
// delimiter, the quote char, \r, or \n. Double-up inner quotes.

const FIELDNAMES = [
  "name",
  "category",
  "cluster_id",
  "latitude",
  "longitude",
  "wait_min_minutes",
  "wait_max_minutes",
  "density_tier",
  "nearby_poi_count",
  "open_during_play",
  "opening_hours",
  "osm_type",
  "osm_id",
];

function quote(val) {
  const s = val === null || val === undefined ? "" : String(val);
  if (/[",\r\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export function writeCSV(rows) {
  const lines = [FIELDNAMES.join(",")];
  for (const r of rows) {
    lines.push(FIELDNAMES.map((f) => quote(r[f])).join(","));
  }
  // Python csv writes with '\r\n' line terminators by default. Match.
  return `${lines.join("\r\n")}\r\n`;
}
