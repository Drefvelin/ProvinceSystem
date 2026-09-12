import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { getMaterialBySlug, serverCraftedMaterials } from "../data";
import MaterialsPage from "./page";
import MaterialDetailPage from "./[slug]/page";

describe("material acquisition", () => {
  it("does not claim gathered materials have no recipes", () => {
    const html = renderToStaticMarkup(MaterialsPage());
    expect(html).not.toContain("Drop / gather only");
    expect(html).not.toContain("These materials have no crafting recipe");
  });

  it.each(["Niter", "Arcane Crystal"])("does not register %s as crafted", (name) => {
    expect(serverCraftedMaterials.some((m) => m.name === name)).toBe(false);
  });

  it.each(["tin", "ignitium"])("separates %s gathering from unpacking", async (slug) => {
    const html = renderToStaticMarkup(await MaterialDetailPage({ params: Promise.resolve({ slug }) }));
    expect(html).toContain("Block unpacking");
    expect(html).toContain("already own");
    expect(html).toContain("Chance");
    expect(getMaterialBySlug(slug)?.recipe).toBeUndefined();
    const unpacking = getMaterialBySlug(slug)!.unpackingRecipes;
    expect(unpacking).toHaveLength(1);
    expect(unpacking[0].ingredients).toMatchObject([{ qty: 1 }]);
    expect(unpacking[0].output.qty).toBe(4);
    expect(unpacking[0].station).toBe("Ingot Station");
    expect(unpacking[0].time).toBe(5);
  });

  it.each(["niter", "arcane-crystal"])("documents actual %s acquisition", async (slug) => {
    const html = renderToStaticMarkup(await MaterialDetailPage({ params: Promise.resolve({ slug }) }));
    expect(html).toContain("Lucky Miner I");
    expect(html).toContain("0.05%");
    expect(html).toContain("Rare Ore Mine");
    expect(html).not.toContain("50%");
    expect(html).not.toContain("No crafting recipe. This material comes from loot");
  });

  it("does not advertise disabled Tin mining or the inactive detector reward pool as available", () => {
    const sources = getMaterialBySlug("tin")!.acquisition!;
    expect(sources.find((s) => s.method === "Mining")?.chance).toBe("No active Lucky Miner Tin drop.");
    expect(sources.find((s) => s.method.startsWith("Detector"))?.detail).toContain("currently unavailable");
    expect(sources.every((s) => !s.chance.includes("%"))).toBe(true);
  });

  it("reports base Ignitium drop chances with profession and Fortune conditions", () => {
    const sources = getMaterialBySlug("ignitium")!.acquisition!;
    expect(sources.find((s) => s.method.includes("Lucky Miner I"))?.chance).toBe("0.2% per eligible ore block before Fortune.");
    expect(sources.find((s) => s.method.includes("Tree Gatherer IV"))?.chance).toBe("0.01% per eligible log before Fortune.");
    expect(sources.find((s) => s.method === "Detector rewards")?.chance).toContain("unverified");
  });
});
