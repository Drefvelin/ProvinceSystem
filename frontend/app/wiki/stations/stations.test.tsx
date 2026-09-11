// @vitest-environment node
// NOTE: `renderToStaticMarkup` is only needed by the disabled suite at the
// bottom of this file (see its block comment); re-add this import when
// restoring that suite.
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { stations } from "../data";

// TEMPORARILY DISABLED: Stations section - the route files were renamed to
// `page.disabled.tsx` / `[slug]/page.disabled.tsx` so Next stops routing them
// (see the matching comment at the top of those files). This test file used to
// import `StationsPage` from "./page" and `StationDetailPage`/
// `generateStaticParams` from "./[slug]/page" at the top of the file; those
// imports are removed here because `tsc`/vitest would fail to resolve them
// while the routes are off (TS2307 "Cannot find module").
//
// The data-only assertions below (the `stations` array itself, its slugs, and
// the on-disk asset checks) don't need those components, so they still run
// and still guard against broken asset paths or data regressions.
//
// The suite at the bottom that needs the rendered route components is
// `describe.skip`-ped with its original body preserved in a block comment.
// TO RESTORE: rename the route files back to `page.tsx`, add back
//   import StationsPage from "./page";
//   import StationDetailPage, { generateStaticParams } from "./[slug]/page";
// at the top of this file, then replace the `describe.skip(...)` block below
// with the commented-out code inside it (uncomment it verbatim).

describe("station data (still live)", () => {
  // These assertions only touch the `stations` data module and on-disk assets,
  // none of which were disabled, so they keep running and guarding against
  // broken asset paths / data regressions while the routes are off.

  it("documents exactly 22 stations", () => {
    expect(stations).toHaveLength(22);
  });

  it("includes the bird mailbox and the four newly added stations", () => {
    expect(stations.some((station) => station.slug === "bird-mailbox")).toBe(true);
    for (const slug of ["copper-station", "forester-station", "tool-station", "research-station"]) {
      expect(stations.some((station) => station.slug === slug), slug).toBe(true);
    }
  });

  it("resolves icon and fallback texture assets on disk for the four newly added stations", () => {
    for (const slug of ["copper-station", "forester-station", "tool-station", "research-station"]) {
      const station = stations.find((candidate) => candidate.slug === slug);
      expect(station, slug).toBeDefined();
      expect(station?.model).toBeUndefined();
      expect(existsSync(join(process.cwd(), "public", station!.icon as string)), station!.icon as string).toBe(true);
      expect(existsSync(join(process.cwd(), "public", station!.fallbackTexture as string)), station!.fallbackTexture as string).toBe(true);
    }
    const copper = stations.find((station) => station.slug === "copper-station");
    expect(copper?.icon).toBe("/wiki/textures/vanilla/copper_ingot.png");
    const forester = stations.find((station) => station.slug === "forester-station");
    expect(forester?.icon).toBe("/wiki/textures/vanilla/oak_log.png");
    const tool = stations.find((station) => station.slug === "tool-station");
    expect(tool?.icon).toBe("/wiki/textures/vanilla/iron_pickaxe.png");
    const research = stations.find((station) => station.slug === "research-station");
    expect(research?.icon).toBe("/wiki/textures/vanilla/book.png");
  });

  it("uses the complete vanilla grindstone model for Block Station", () => {
    const block = stations.find((station) => station.slug === "block-station");
    expect(block?.model?.url).toBe("/wiki/models/stations/grindstone.json");
    const model = JSON.parse(readFileSync(join(process.cwd(), "public/wiki/models/stations/grindstone.json"), "utf8"));
    expect(model.elements).toHaveLength(5);
    expect(new Set(Object.values(model.textures))).toEqual(new Set(["block/grindstone_pivot", "block/grindstone_round", "block/grindstone_side", "block/dark_oak_log"]));
    for (const url of Object.values(block?.model?.textures ?? {})) {
      expect(existsSync(join(process.cwd(), "public", url as string)), url as string).toBe(true);
    }
  });
});

// TEMPORARILY DISABLED: Stations section - these tests render `StationsPage` /
// `StationDetailPage` and call `generateStaticParams`, all of which live in the
// renamed `page.disabled.tsx` files and cannot be imported while the route is
// off (importing them would reintroduce the TS2307 "Cannot find module './page'"
// error this change fixes). The original bodies are preserved verbatim in the
// block comment below so they can be dropped back in without rewriting them.
//
// TO RESTORE (see the file-level comment above for the required imports):
// describe("station gallery (rendered components)", () => {
//   it("lists every documented station while mounting one selected preview", () => {
//     const html = renderToStaticMarkup(<StationsPage />);
//     expect(stations).toHaveLength(22);
//     expect(html.match(/aria-pressed=/g) ?? []).toHaveLength(stations.length);
//     expect(html.match(/View station details/g) ?? []).toHaveLength(1);
//     for (const station of stations) expect(html).toContain(`>${station.name}</button>`);
//     expect(html).toContain('href="/wiki/stations/weapon-station"');
//     expect(stations.some((station) => station.slug === "bird-mailbox")).toBe(true);
//     expect(html).toContain(">Bird Mailbox</button>");
//     expect(html).toContain(">Copper Station</button>");
//     expect(html).toContain(">Forester Station</button>");
//     expect(html).toContain(">Tool Station</button>");
//     expect(html).toContain(">Research Station</button>");
//   });
//
//   it("publishes a detail route for each selector", async () => {
//     expect(generateStaticParams()).toEqual(stations.map(({ slug }) => ({ slug })));
//     const archaeology = await StationDetailPage({ params: Promise.resolve({ slug: "archeology-station" }) });
//     expect(renderToStaticMarkup(archaeology)).toContain("Archeology Table");
//     const birdMailbox = await StationDetailPage({ params: Promise.resolve({ slug: "bird-mailbox" }) });
//     expect(renderToStaticMarkup(birdMailbox)).toContain("Bird Mailbox");
//   });
//
//   it("publishes a detail route for each of the four newly added stations", async () => {
//     for (const slug of ["copper-station", "forester-station", "tool-station", "research-station"]) {
//       const station = stations.find((candidate) => candidate.slug === slug);
//       expect(station, slug).toBeDefined();
//       const page = await StationDetailPage({ params: Promise.resolve({ slug }) });
//       expect(renderToStaticMarkup(page)).toContain(station!.name);
//     }
//   });
//
//   it("does not render 'Recipes crafted here' section on station detail pages", async () => {
//     // Regression test: the "Recipes crafted here" section was removed and should never silently return
//     const alchemyStation = await StationDetailPage({ params: Promise.resolve({ slug: "alchemy-station" }) });
//     const html = renderToStaticMarkup(alchemyStation);
//
//     // Verify the removed section headers are not present
//     expect(html).not.toContain("Recipes crafted here");
//     expect(html).not.toContain("No recipes documented yet.");
//
//     // Verify the separate "How to obtain this station" section still renders
//     expect(html).toContain("How to obtain this station");
//   });
// });
describe.skip("station gallery (rendered components) - see block comment above to restore", () => {
  it.skip("needs StationsPage/StationDetailPage from the disabled route files - restore per comment above", () => {});
});
