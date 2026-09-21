import { empty, V } from "./helpers";
import type { Recipe, WikiCommandSet, WikiSection } from "./types";

// ---------- Market Block ----------

export const marketBlockRecipe: Recipe = {
  key: "market-block",
  title: "Market Block",
  station: "Crafting Table",
  requirement: "None",
  ingredients: [
    { name: "Ink Sac", qty: 1, texture: V("ink_sac.png") },
    { name: "Paper", qty: 1, texture: V("paper.png") },
    empty,
    { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
    { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
    { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
    { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
    empty,
    { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
  ],
  note: "Synthetic Ink can replace the Ink Sac. Use one Oak Plank in each of the five plank slots.",
  output: {
    name: "Market Block",
    qty: 1,
    model: {
      url: "/wiki/models/market-block.json",
      textures: {
        "4": "/wiki/textures/market-block/wood_m.png",
        "8": "/wiki/textures/market-block/wood2.png",
        "9": "/wiki/textures/market-block/wood1.png",
        "10": "/wiki/textures/market-block/coin.png",
        "11": "/wiki/textures/market-block/manifest.png",
        "12": "/wiki/textures/market-block/ink_bottle.png",
        "13": "/wiki/textures/market-block/apple.png",
      },
    },
  },
};

export type MarketTrade = {
  item: string;
  bundleSize: number;
  restingPrice: number;
  currentPrice: number;
  pricePerItem: number;
  category: string;
};

/**
 * `trades/*.json`. All 33 live trades currently sit at demand = demand limit
 * (20), so current price is exactly 2x resting price for every one of them :
 * see the price formula on the page.
 */
export const marketBlockTrades: MarketTrade[] = [
  { item: "Wheat", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Farming" },
  { item: "Carrot", bundleSize: 64, restingPrice: 1, currentPrice: 2, pricePerItem: 0.031, category: "Farming" },
  { item: "Potato", bundleSize: 64, restingPrice: 1, currentPrice: 2, pricePerItem: 0.031, category: "Farming" },
  { item: "Beetroot", bundleSize: 64, restingPrice: 1, currentPrice: 2, pricePerItem: 0.031, category: "Farming" },
  { item: "Melon Slice", bundleSize: 16, restingPrice: 1, currentPrice: 2, pricePerItem: 0.125, category: "Farming" },
  { item: "Pumpkin", bundleSize: 16, restingPrice: 2, currentPrice: 4, pricePerItem: 0.25, category: "Farming" },
  { item: "Sugar Cane", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Farming" },
  { item: "Honey Bottle", bundleSize: 16, restingPrice: 4, currentPrice: 8, pricePerItem: 0.5, category: "Farming" },
  { item: "Honeycomb", bundleSize: 16, restingPrice: 4, currentPrice: 8, pricePerItem: 0.5, category: "Farming" },
  { item: "Salt", bundleSize: 32, restingPrice: 2, currentPrice: 4, pricePerItem: 0.125, category: "Farming" },
  { item: "Spice Leaf", bundleSize: 8, restingPrice: 4, currentPrice: 8, pricePerItem: 1.0, category: "Farming" },
  { item: "Tobacco", bundleSize: 4, restingPrice: 2, currentPrice: 4, pricePerItem: 1.0, category: "Farming" },
  { item: "Coal", bundleSize: 32, restingPrice: 3, currentPrice: 6, pricePerItem: 0.1875, category: "Mining" },
  { item: "Copper Ingot", bundleSize: 32, restingPrice: 3, currentPrice: 6, pricePerItem: 0.1875, category: "Mining" },
  { item: "Iron Ingot", bundleSize: 16, restingPrice: 4, currentPrice: 8, pricePerItem: 0.5, category: "Mining" },
  { item: "Redstone", bundleSize: 64, restingPrice: 1, currentPrice: 2, pricePerItem: 0.031, category: "Mining" },
  { item: "Lapis Lazuli", bundleSize: 32, restingPrice: 5, currentPrice: 10, pricePerItem: 0.3125, category: "Mining" },
  { item: "Amethyst Shard", bundleSize: 4, restingPrice: 1, currentPrice: 2, pricePerItem: 0.5, category: "Mining" },
  { item: "Diamond", bundleSize: 1, restingPrice: 2, currentPrice: 4, pricePerItem: 4.0, category: "Mining" },
  { item: "Tin", bundleSize: 12, restingPrice: 8, currentPrice: 16, pricePerItem: 1.33, category: "Mining" },
  { item: "Oak Log", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Woodcutting" },
  { item: "Spruce Log", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Woodcutting" },
  { item: "Birch Log", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Woodcutting" },
  { item: "Jungle Log", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Woodcutting" },
  { item: "Acacia Log", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Woodcutting" },
  { item: "Dark Oak Log", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Woodcutting" },
  { item: "Mangrove Log", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Woodcutting" },
  { item: "Cherry Log", bundleSize: 32, restingPrice: 1, currentPrice: 2, pricePerItem: 0.0625, category: "Woodcutting" },
  { item: "Cod", bundleSize: 16, restingPrice: 3, currentPrice: 6, pricePerItem: 0.375, category: "Fishing" },
  { item: "Salmon", bundleSize: 16, restingPrice: 4, currentPrice: 8, pricePerItem: 0.5, category: "Fishing" },
  { item: "String", bundleSize: 32, restingPrice: 6, currentPrice: 12, pricePerItem: 0.375, category: "Other" },
  { item: "Silk", bundleSize: 4, restingPrice: 2, currentPrice: 4, pricePerItem: 1.0, category: "Other" },
  { item: "Enchanted Dust", bundleSize: 8, restingPrice: 6, currentPrice: 12, pricePerItem: 1.5, category: "Other" },
];

export type MarketCategory = { name: string; colour: string };

export const marketBlockCategories: MarketCategory[] = [
  { name: "Farming", colour: "#b3d177" },
  { name: "Mining", colour: "#ad9084" },
  { name: "Woodcutting", colour: "#a3702f" },
  { name: "Fishing", colour: "#7fb2d4" },
  { name: "Other", colour: "#d8d8d8" },
];

/**
 * The jar contains zero permission checks on `/marketblock`, so every
 * subcommand below is technically runnable by any player right now. That is
 * documented as a known bug, not the intended design. By design MarketBlock
 * has no player-facing command: you interact with the block.
 */
export const marketBlockCommands: WikiCommandSet = {
  system: "Market Block",
  href: "/wiki/market-blocks",
  commands: [],
  excludedStaffCommands: [
    "/marketblock reload",
    "/marketblock add",
    "/marketblock delete <id>",
    "/marketblock reset <id>",
    "/marketblock resetall",
  ],
};

export const marketBlockSection: WikiSection = {
  nav: {
    href: "/wiki/market-blocks",
    label: "Market Block",
    category: "social",
    blurb: "A sell-only shop block: dump raw materials for denars at a price that sags the more you sell.",
  },
  recipes: [marketBlockRecipe],
  commands: marketBlockCommands,
};

