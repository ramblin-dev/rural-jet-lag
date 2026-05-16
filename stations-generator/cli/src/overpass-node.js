// Node-side Overpass fetcher with optional fixture cache, mirroring the
// Python --overpass-fixture-dir behavior: if the fixture file exists,
// read from it (no network); else fetch and write it.

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname } from "node:path";
import {
  OVERPASS_URL,
  USER_AGENT,
  OVERPASS_TIMEOUT_SEC,
} from "@rural-jet-lag/core";

export async function fetchOverpassCached(query, fixturePath) {
  if (fixturePath && existsSync(fixturePath)) {
    return JSON.parse(await readFile(fixturePath, "utf8"));
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(),
    (OVERPASS_TIMEOUT_SEC + 10) * 1000);
  let elements;
  try {
    const r = await fetch(OVERPASS_URL, {
      method: "POST",
      headers: {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ data: query }).toString(),
      signal: controller.signal,
    });
    if (!r.ok) throw new Error(`Overpass HTTP ${r.status}: ${await r.text()}`);
    const json = await r.json();
    elements = json.elements ?? [];
  } finally {
    clearTimeout(timeout);
  }
  if (fixturePath) {
    await mkdir(dirname(fixturePath), { recursive: true });
    await writeFile(fixturePath, JSON.stringify(elements));
  }
  return elements;
}
