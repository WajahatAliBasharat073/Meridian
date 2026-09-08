import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  test: {
    // Pure logic only for now — these are the mirrors and calculations that
    // decide what the UI allows, so they are worth pinning down without
    // dragging in a DOM environment.
    include: ["lib/**/*.test.ts"],
    environment: "node",
  },
  resolve: {
    alias: { "@": path.resolve(__dirname, ".") },
  },
});
