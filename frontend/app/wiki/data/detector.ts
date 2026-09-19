import { stationRecipe } from "./station-recipes";
import type { Recipe, WikiCommandSet, WikiSection } from "./types";

// ---------- Arcane Trace Detector ("Geiger Counter") ----------

/**
 * These three used to be hand-written here. They are now taken straight from
 * the server's `engineer-station.yml` (see `data/generated/stationRecipes.ts`),
 * which is authoritative, so the page and the Engineer Station page can never
 * disagree. They are registered by `stationsSection`, not by this section.
 */
export const detectorRecipes: Recipe[] = [
  stationRecipe("gen-engineer-station-dead_geiger_counter"),
  stationRecipe("gen-engineer-station-fuel"),
  stationRecipe("gen-engineer-station-geiger_counter"),
];

export const signalTable = [
  { signal: "1 ring", meaning: "Over 1000 blocks away." },
  { signal: "2 rings", meaning: "Within 1000 blocks." },
  { signal: "3 rings", meaning: "Within 300 blocks." },
  { signal: "Very dark purple, almost black", meaning: "Near the far edge of range (~2500 blocks)." },
  { signal: "Bright purple", meaning: "~200 blocks out." },
  { signal: "Turning white", meaning: "Under 200 blocks: the whiter, the closer." },
  { signal: "Slow clicking (~1 every 2s)", meaning: "Outer limit of the signal." },
  { signal: "Rapid clicking (a stream)", meaning: "Almost at the source." },
];

export const lootTable = [
  {
    rarity: "Common",
    chance: "65%",
    rewards: "2x Ignitium, Common Item Skin Scroll, Weak Repair Kit, Tool Repair Kit, Lost Knowledge Scrap, or 8x Raw Iron Block",
  },
  {
    rarity: "Rare",
    chance: "25%",
    rewards: "4x Ignitium, Rare Item Skin Scroll, Trial Key, Medium Repair Kit, 2x Tool Repair Kit, or 16x Raw Iron Block",
  },
  {
    rarity: "Epic",
    chance: "7%",
    rewards: "8x Ignitium, Rare Item Skin Scroll, Strong Repair Kit, 4x Tool Repair Kit, or 32x Raw Iron Block",
  },
  {
    rarity: "Legendary",
    chance: "3%",
    rewards: "16x Ignitium, Rare Item Skin Scroll, 2x Strong Repair Kit, Magical Repair Kit, 64x Raw Iron Block, or 8x Raw Gold Block",
  },
];

/** geiger_counter 1.1.2 exposes only an op-default admin command. */
export const detectorCommands: WikiCommandSet = {
  system: "Arcane Trace Detector",
  href: "/wiki/arcane-trace-detector",
  commands: [],
  excludedStaffCommands: ["/geiger <locate|move|limits|resetlimits|droplist|reload>"],
};

export const detectorSection: WikiSection = {
  nav: {
    href: "/wiki/arcane-trace-detector",
    label: "Arcane Trace Detector",
    category: "magic",
    blurb:
      "Hunt the server's single hidden source of Arcane Radiation with a clicking, glowing detector. A serverwide loot race.",
  },
  // `detectorRecipes` are server recipes registered by `stationsSection`; listing
  // them again here would put them in the recipe index twice.
  commands: detectorCommands,
};
