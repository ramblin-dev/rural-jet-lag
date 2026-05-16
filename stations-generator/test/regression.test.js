// End-to-end regression tests for the vehicle-stations pipeline.
// Each case runs the CLI in a subprocess against its frozen Overpass
// fixture and asserts byte-equality with the case's blessed
// expected.{csv,kml} baseline.
//
// Run with: npm test (which calls `node --test test/`).
// Add a case: see test/README.md.

import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { describe, it, after } from "node:test";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PKG_ROOT = resolve(HERE, "..");
const CASES_DIR = join(HERE, "cases");
const CLI_MAIN = join(PKG_ROOT, "cli", "src", "main.js");

const CASES = [
  { name: "sioux", hasExclusion: false },
  { name: "town-excl", hasExclusion: true },
];

function runCli(args) {
  return new Promise((resolveP, rejectP) => {
    const child = spawn("node", [CLI_MAIN, ...args], { stdio: ["ignore", "ignore", "pipe"] });
    let stderr = "";
    child.stderr.on("data", (d) => { stderr += d; });
    child.on("exit", (code) => {
      if (code === 0) resolveP();
      else rejectP(new Error(`CLI exited ${code}\n${stderr}`));
    });
  });
}

describe("regression: vehicle-stations pipeline", () => {
  for (const c of CASES) {
    describe(c.name, () => {
      const caseDir = join(CASES_DIR, c.name);
      const expectedCsv = join(caseDir, "baseline", "expected.csv");
      const expectedKml = join(caseDir, "baseline", "expected.kml");
      const tmp = mkdtempSync(join(tmpdir(), `regression-${c.name}-`));
      after(() => rmSync(tmp, { recursive: true, force: true }));

      it("baseline files exist", () => {
        assert.ok(existsSync(expectedCsv), `missing ${expectedCsv}`);
        assert.ok(existsSync(expectedKml), `missing ${expectedKml}`);
      });

      it("CLI runs against the frozen fixture", async () => {
        const args = [
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
        if (c.hasExclusion) {
          args.push("--subtract-polygon", join(caseDir, "exclusion.geojson"));
        }
        await runCli(args);
      });

      it("CSV matches baseline byte-for-byte", () => {
        const expected = readFileSync(expectedCsv, "utf8");
        const actual = readFileSync(join(tmp, "expected.csv"), "utf8");
        assert.equal(actual, expected);
      });

      it("KML matches baseline byte-for-byte", () => {
        const expected = readFileSync(expectedKml, "utf8");
        const actual = readFileSync(join(tmp, "expected.kml"), "utf8");
        assert.equal(actual, expected);
      });
    });
  }
});
