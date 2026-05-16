// Hand-rolled arg parser mirroring the Python CLI's flag set. Boring is
// fine — the flag list is fixed and well-defined, and a dep-free parser
// keeps the CLI install footprint tiny.

const SPEC = {
  "--polygon-file": { type: "string", required: true },
  "--name": { type: "string", default: "game-area" },
  "--min-station-spacing-m": { type: "number", default: 300 },
  "--game-size": { type: "gameSize", default: null },
  "--cluster-radius-m": { type: "number", default: null },
  "--density-radius-m": { type: "number", default: 1609 },
  "--max-stations-per-cluster": { type: "int", default: null },
  "--water-subtract": { type: "bool", default: true },
  "--include-transit-stations": { type: "bool", default: true },
  "--subtract-polygon": { type: "string", default: null },
  "--playing-hours": { type: "string", default: "7am-7pm" },
  "--playing-days-of-week": { type: "string", default: "sat,sun" },
  "--overpass-fixture-dir": { type: "string", default: null },
  "--output-dir": { type: "string", default: null },
  "--no-timestamp": { type: "flag", default: false },
};

function parseGameSize(s) {
  const t = s.trim().toLowerCase();
  if (t === "s" || t === "small") return "S";
  if (t === "m" || t === "medium") return "M";
  if (t === "l" || t === "large") return "L";
  throw new Error(`unknown game size '${s}'; use S/M/L or small/medium/large`);
}

function coerce(spec, raw) {
  if (spec.type === "string" || spec.type === "gameSize") {
    return spec.type === "gameSize" ? parseGameSize(raw) : raw;
  }
  if (spec.type === "number") {
    const n = Number(raw);
    if (!Number.isFinite(n)) throw new Error(`expected number, got '${raw}'`);
    return n;
  }
  if (spec.type === "int") {
    const n = Number.parseInt(raw, 10);
    if (!Number.isInteger(n)) throw new Error(`expected integer, got '${raw}'`);
    return n;
  }
  throw new Error(`internal: cannot coerce type ${spec.type}`);
}

export function parseArgs(argv) {
  const out = {};
  for (const [flag, spec] of Object.entries(SPEC)) {
    out[flagToKey(flag)] = spec.default;
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "-h" || arg === "--help") {
      printHelp();
      process.exit(0);
    }
    // Handle --no-foo for bool flags
    if (arg.startsWith("--no-") && SPEC[`--${arg.slice(5)}`]?.type === "bool") {
      out[flagToKey(`--${arg.slice(5)}`)] = false;
      continue;
    }
    const spec = SPEC[arg];
    if (!spec) throw new Error(`unknown flag: ${arg}`);
    if (spec.type === "flag") {
      out[flagToKey(arg)] = true;
      continue;
    }
    if (spec.type === "bool") {
      out[flagToKey(arg)] = true; // --water-subtract turns it on; --no-water-subtract turns off
      continue;
    }
    const next = argv[i + 1];
    if (next === undefined) throw new Error(`${arg} requires a value`);
    out[flagToKey(arg)] = coerce(spec, next);
    i += 1;
  }
  for (const [flag, spec] of Object.entries(SPEC)) {
    if (spec.required && out[flagToKey(flag)] == null) {
      throw new Error(`missing required flag: ${flag}`);
    }
  }
  if (out.maxStationsPerCluster !== null && out.maxStationsPerCluster < 0) {
    throw new Error("--max-stations-per-cluster must be 0 or a positive integer");
  }
  return out;
}

function flagToKey(flag) {
  // --foo-bar-baz → fooBarBaz
  return flag
    .slice(2)
    .split("-")
    .map((p, i) => (i === 0 ? p : p[0].toUpperCase() + p.slice(1)))
    .join("");
}

function printHelp() {
  const lines = ["vehicle-stations — generate vehicle-station coordinates", ""];
  for (const flag of Object.keys(SPEC)) {
    const s = SPEC[flag];
    const def = s.default === null ? "" : `  (default: ${s.default})`;
    const req = s.required ? "  (required)" : "";
    lines.push(`  ${flag.padEnd(34)} ${s.type}${req}${def}`);
  }
  lines.push("");
  lines.push(
    "Bool flags: use --water-subtract / --no-water-subtract, " +
    "--include-transit-stations / --no-include-transit-stations.",
  );
  process.stdout.write(`${lines.join("\n")}\n`);
}
