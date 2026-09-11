import { slugify } from "./helpers";
import { dropOnlyMaterials, materialRecipes, serverCraftedMaterials } from "./materials";
import { allRecipes } from "./registry";
import type { MaterialCatalogEntry, Recipe } from "./types";

// ---------- Material catalogue (for cross-linking + detail pages) ----------

export function getRecipesForStation(name: string): Recipe[] {
  return allRecipes.filter((r) => r.station === name);
}

function buildMaterialCatalog(): Map<string, MaterialCatalogEntry> {
  const map = new Map<string, MaterialCatalogEntry>();

  for (const r of materialRecipes) {
    map.set(r.output.name, {
      slug: slugify(r.output.name),
      name: r.output.name,
      texture: r.output.texture,
      recipe: r,
      usedIn: [],
    });
  }
  for (const m of [...serverCraftedMaterials, ...dropOnlyMaterials]) {
    if (!map.has(m.name)) {
      map.set(m.name, {
        slug: slugify(m.name),
        name: m.name,
        texture: m.texture,
        lore: m.lore,
        usedIn: [],
      });
    } else {
      const entry = map.get(m.name)!;
      entry.lore = entry.lore ?? m.lore;
    }
  }

  // A material listed without a hand-written recipe still has one if some
  // registered recipe produces it: the server-generated station recipes are
  // where most material recipes now live.
  for (const entry of map.values()) {
    if (!entry.recipe) entry.recipe = allRecipes.find((r) => r.output.name === entry.name);
  }

  for (const r of allRecipes) {
    for (const ing of r.ingredients) {
      const entry = map.get(ing.name);
      if (entry && entry.recipe?.key !== r.key) {
        entry.usedIn.push(r);
      }
    }
  }

  return map;
}

export const materialCatalog = buildMaterialCatalog();

/** Names in the catalogue, for CraftingGrid to decide which slots become clickable material links. */
export const catalogNames = new Set(materialCatalog.keys());

export function getMaterialBySlug(slug: string): MaterialCatalogEntry | undefined {
  for (const entry of materialCatalog.values()) {
    if (entry.slug === slug) return entry;
  }
  return undefined;
}
