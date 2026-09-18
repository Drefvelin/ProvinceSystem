import generated from "./generated/woodworkingFurniture.json";
import type { WikiSection } from "./types";

// Source: plugins/Woodworking (categories, projects, hits, materials, qualities) and the
// ItemsAdder furniture packs. Regenerate with `python scripts/build-woodworking-furniture.py`.

export type WoodworkingProject = {
  id: string;
  name: string;
  category: string;
  itemId: string;
  modelUrl: string;
  textureUrls: Record<string, string>;
  /** Set instead of `textureUrls` when the single texture is an animated frame strip. */
  textureUrl?: string;
  textureAnimationUrl?: string;
};

export const woodworkingCategories: { id: string; name: string }[] = generated.categories;
export const woodworkingProjects = generated.projects as unknown as WoodworkingProject[];

/** Each action is performed with its matching artisan tool in the main hand. */
export const woodworkingActions = [
  { action: "Whittle", tool: "Whittling Tool", group: "Woodworking" },
  { action: "Engrave", tool: "Engraving Tool", group: "Woodworking" },
  { action: "Hit", tool: "Hammer Tool", group: "Metalworking" },
  { action: "Small Hit", tool: "Small Hammer Tool", group: "Metalworking" },
  { action: "Etch", tool: "Etching Tool", group: "Metalworking" },
  { action: "Sew", tool: "Sewing Needle", group: "Other" },
];

export const woodworkingMaterials = ["Valewood", "Runebark", "Amberpine", "Goldmaple", "Silk"];

/** Quality is picked by hit accuracy; the highest threshold met wins. */
export const woodworkingQualities = [
  { name: "Crude", accuracy: "Below 50%" },
  { name: "Sturdy", accuracy: "50%" },
  { name: "Fine", accuracy: "75%" },
  { name: "Ornate", accuracy: "90%" },
  { name: "Masterwork", accuracy: "100%" },
];

export const woodworkingSection: WikiSection = {
  nav: {
    href: "/wiki/woodworking",
    label: "Woodworking Furniture",
    category: "professions",
    blurb: `Every one of the ${generated.projects.length} decorative furniture pieces you can craft, with a 3D preview of each.`,
  },
};
