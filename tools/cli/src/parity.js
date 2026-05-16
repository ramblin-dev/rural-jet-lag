// JS-side parity runner. Mirrors old-tools/parity-test/run_python.py:
// reads the same fixture, writes a js-sioux baseline alongside the
// python-sioux one, and (optionally) diffs them.

import { spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, "..", "..", "..");
const PARITY_DIR = join(REPO_ROOT, "old-tools", "parity-test");
const CLI_MAIN = join(HERE, "main.js");

function run(cmd, args) {
  return new Promise((resolveP, rejectP) => {
    const child = spawn(cmd, args, { stdio: "inherit" });
    child.on("exit", (code) => (code === 0 ? resolveP() : rejectP(new Error(`exit ${code}`))));
  });
}

function normaliseKml(text) {
  // The KML layer name carries the --name value (python-sioux vs js-sioux),
  // which is deliberately different per run. Strip the impl prefix so the
  // diff focuses on real content.
  return text.replace(/<name>(python|js)-sioux<\/name>/g, "<name>NAME</name>");
}

async function diff(label, pythonPath, jsPath) {
  const py = readFileSync(pythonPath, "utf8");
  const js = readFileSync(jsPath, "utf8");
  const pyN = label === "kml" ? normaliseKml(py) : py;
  const jsN = label === "kml" ? normaliseKml(js) : js;
  if (pyN === jsN) {
    process.stderr.write(`✓ ${label} parity: byte-identical\n`);
    return true;
  }
  process.stderr.write(`✗ ${label} parity: differs (${pyN.length} vs ${jsN.length} bytes)\n`);
  const pyLines = pyN.split("\n");
  const jsLines = jsN.split("\n");
  const max = Math.min(pyLines.length, jsLines.length);
  let shown = 0;
  for (let i = 0; i < max && shown < 10; i += 1) {
    if (pyLines[i] !== jsLines[i]) {
      process.stderr.write(`  line ${i + 1}:\n    py: ${pyLines[i]}\n    js: ${jsLines[i]}\n`);
      shown += 1;
    }
  }
  if (pyLines.length !== jsLines.length) {
    process.stderr.write(`  line count: py=${pyLines.length} js=${jsLines.length}\n`);
  }
  return false;
}

async function main() {
  const args = [
    CLI_MAIN,
    "--polygon-file", join(PARITY_DIR, "polygon.geojson"),
    "--name", "js-sioux",
    "--overpass-fixture-dir", join(PARITY_DIR, "fixtures"),
    "--output-dir", join(PARITY_DIR, "baseline"),
    "--no-timestamp",
    "--min-station-spacing-m", "300",
    "--density-radius-m", "1609",
    "--playing-hours", "7am-7pm",
    "--playing-days-of-week", "sat,sun",
  ];
  process.stderr.write(`Running: node ${args.join(" ")}\n`);
  await run("node", args);

  const pyCsv = join(PARITY_DIR, "baseline", "python-sioux.csv");
  const pyKml = join(PARITY_DIR, "baseline", "python-sioux.kml");
  const jsCsv = join(PARITY_DIR, "baseline", "js-sioux.csv");
  const jsKml = join(PARITY_DIR, "baseline", "js-sioux.kml");
  if (!existsSync(pyCsv) || !existsSync(pyKml)) {
    process.stderr.write(
      `error: Python baseline missing. Run old-tools/parity-test/run_python.py first.\n`,
    );
    process.exit(2);
  }
  const csvOk = await diff("csv", pyCsv, jsCsv);
  const kmlOk = await diff("kml", pyKml, jsKml);
  process.exit(csvOk && kmlOk ? 0 : 1);
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e.stack ?? e.message}\n`);
  process.exit(1);
});
