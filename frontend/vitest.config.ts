import path from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
  test: {
    // Node stays the default: every `.test.ts` in this repo is pure logic and
    // gains nothing from a DOM, and jsdom is slow enough to be worth not
    // paying for by default.
    environment: "node",
    // `.test.tsx` was previously unmatched, which meant *no* `.tsx` file in
    // this repo was ever imported by a test — a component could stop
    // compiling (a dropped `export`, a bad import) and the whole suite stayed
    // green. Component tests opt into jsdom with a
    // `@vitest-environment jsdom` docblock at the top of the file, so the
    // node-env `.test.ts` files keep running exactly as they did.
    include: ["app/**/*.test.ts", "app/**/*.test.tsx"],
  },
});
