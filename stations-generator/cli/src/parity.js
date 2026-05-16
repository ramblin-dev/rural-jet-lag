// JS-side regression runner. Iterates over checked-in test cases under
// stations-generator/parity-test/cases/, regenerates each case's output
// against its frozen Overpass fixture, and diffs against the case's
// blessed `expected.{csv,kml}` baseline.
//
// Each case lives in cases/<name>/ with:
//   - polygon.geojson             play-area polygon
//   - exclusion.geojson           optional exclusion polygon
//   - fixtures/pois.json, water.json   frozen Overpass responses
//   - baseline/expected.{csv,kml}      blessed reference output
//
// The runner writes actual.{csv,kml} into a tmp dir, diffs them against
// expected.{csv,kml}, and exits non-zero on any drift.

import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, "..", "..", "..");
const PARITY_DIR = join(REPO_ROOT, "stations-generator", "parity-test");
const CASES_DIR = join(PARITY_DIR, "cases");
const CLI_MAIN = join(HERE, "main.js");

const CASES = [
  { name: "sioux", hasExclusion: false },
  { name: "town-excl", hasExclusion: true },
];

function run(cmd, args) {
  return new Promise((resolveP, rejectP) => {
    const child = spawn(cmd, args, { stdio: "inherit" });
    child.on("exit", (code) => (code === 0 ? resolveP() : rejectP(new Error(`exit ${code}`))));
  });
}

function diff(label, expectedPath, actualPath) {
  const expected = readFileSync(expectedPath, "utf8");
  const actual = readFileSync(actualPath, "utf8");
  if (expected === actual) {
    process.stderr.write(`  ✓ ${label}: byte-identical\n`);
    return true;
  }
  process.stderr.write(`  ✗ ${label}: differs (${expected.length} vs ${actual.length} bytes)\n`);
  const expectedLines = expected.split("\n");
  const actualLines = actual.split("\n");
  const max = Math.min(expectedLines.length, actualLines.length);
  let shown = 0;
  for (let i = 0; i < max && shown < 10; i += 1) {
    if (expectedLines[i] !== actualLines[i]) {
      process.stderr.write(
        `    line ${i + 1}:\n      expected: ${expectedLines[i]}\n      actual:   ${actualLines[i]}\n`,
      );
      shown += 1;
    }
  }
  if (expectedLines.length !== actualLines.length) {
    process.stderr.write(`    line count: expected=${expectedLines.length} actual=${actualLines.length}\n`);
  }
  return false;
}

async function runCase(caseDef) {
  process.stderr.write(`\n--- case: ${caseDef.name} ---\n`);
  const caseDir = join(CASES_DIR, caseDef.name);
  const expectedCsv = join(caseDir, "baseline", "expected.csv");
  const expectedKml = join(caseDir, "baseline", "expected.kml");
  if (!existsSync(expectedCsv) || !existsSync(expectedKml)) {
    process.stderr.write(`error: baseline missing in ${caseDir}/baseline/\n`);
    return false;
  }
  const tmp = mkdtempSync(join(tmpdir(), `parity-${caseDef.name}-`));
  const args = [
    CLI_MAIN,
    "--polygon-file", join(caseDir, "polygon.geojson"),
    "--name", "expected",
    "--overpass-fixture-dir", join(caseDir, "fixtures"),
    "--output-dir", tmp,
    "--no-timestamp",
    "--min-station-spacing-m", "300",
    "--density-radius-m", "1609",
    "--playing-hours", "7am-7pm",
    "--playing-days-of-week", "sat,sun",
  ];
  if (caseDef.hasExclusion) {
    args.push("--subtract-polygon", join(caseDir, "exclusion.geojson"));
  }
  try {
    await run("node", args);
    const csvOk = diff("csv", expectedCsv, join(tmp, "expected.csv"));
    const kmlOk = diff("kml", expectedKml, join(tmp, "expected.kml"));
    return csvOk && kmlOk;
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

async function main() {
  let allOk = true;
  for (const c of CASES) {
    const ok = await runCase(c);
    if (!ok) allOk = false;
  }
  process.stderr.write(`\n${allOk ? "all cases passed" : "SOME CASES FAILED"}\n`);
  process.exit(allOk ? 0 : 1);
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e.stack ?? e.message}\n`);
  process.exit(1);
});
