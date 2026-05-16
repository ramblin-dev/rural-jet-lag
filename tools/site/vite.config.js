import { defineConfig } from "vite";

// Relative base so the built site works under any GitHub Pages subpath.
export default defineConfig({
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
