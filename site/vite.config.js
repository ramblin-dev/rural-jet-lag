import { defineConfig } from "vite";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { markdownPagesPlugin } from "./plugins/markdown.js";

const HERE = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  base: "/",
  plugins: [markdownPagesPlugin()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(HERE, "index.html"),
        rules: resolve(HERE, "rules/index.html"),
        setup: resolve(HERE, "setup/index.html"),
        vehicleStations: resolve(HERE, "vehicle-stations/index.html"),
        stations: resolve(HERE, "stations/index.html"),
      },
    },
  },
});
