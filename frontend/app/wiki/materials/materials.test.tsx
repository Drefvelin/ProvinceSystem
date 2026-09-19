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
    expect(html).not.toContain("Chance");
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
    expect(html).not.toContain("0.05%");
    expect(html).toContain("Rare Ore Mine");
    expect(html).not.toContain("50%");
    expect(html).not.toContain("No crafting recipe. This material comes from loot");
  });

  it("lists no acquisition sources for Tin", () => {
    expect(getMaterialBySlug("tin")!.acquisition).toBeUndefined();
  });

  it("lists Ignitium sources without any drop chances", () => {
    const sources = getMaterialBySlug("ignitium")!.acquisition!;
    expect(sources.some((s) => s.method.includes("Lucky Miner I"))).toBe(true);
    expect(sources.some((s) => s.method.includes("Tree Gatherer IV"))).toBe(true);
    expect(sources.every((s) => !("chance" in s) && !/%|chance/i.test(s.detail))).toBe(true);
  });
});
