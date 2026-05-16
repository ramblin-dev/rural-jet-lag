// Browser fetch wrapper for Overpass. Returns the parsed elements list.
// Overpass's public endpoint sets permissive CORS headers, so a direct
// fetch works without a proxy.

import { OVERPASS_TIMEOUT_SEC, OVERPASS_URL } from "@rural-jet-lag/core";

export async function fetchOverpass(query) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(),
    (OVERPASS_TIMEOUT_SEC + 10) * 1000);
  try {
    const r = await fetch(OVERPASS_URL, {
      method: "POST",
      // Browsers refuse to set the User-Agent header, so it's omitted here
      // intentionally; the constant stays defined for the Node CLI.
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ data: query }).toString(),
      signal: controller.signal,
    });
    if (!r.ok) throw new Error(`Overpass HTTP ${r.status}`);
    const json = await r.json();
    return json.elements ?? [];
  } finally {
    clearTimeout(timeout);
  }
}
