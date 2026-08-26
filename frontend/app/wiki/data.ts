export type Slot = {
  name: string;
  qty: number;
  texture?: string;
  /** Render a small live 3D preview instead of a flat texture (used for station outputs). */
  model?: { url: string; texture: string };
};

export type Recipe = {
  key: string;
  title: string;
  station: string;
  time?: number;
  requirement?: string;
  ingredients: Slot[];
  output: Slot;
  note?: string;
};

const T = (path: string) => `/wiki/textures/${path}`;

export const navItems = [
  { href: "/wiki", label: "Overview" },
  { href: "/wiki/arcane-trace-detector", label: "Arcane Trace Detector" },
  { href: "/wiki/musical-instruments", label: "Musical Instruments" },
  { href: "/wiki/mount-whistle", label: "Mount Whistle" },
  { href: "/wiki/materials", label: "Materials" },
  { href: "/wiki/stations", label: "Stations" },
] as const;

// ---------- Arcane Trace Detector ("Geiger Counter") ----------

export const detectorRecipes: Recipe[] = [
  {
    key: "unpowered-detector",
    title: "Unpowered Trace Detector",
    station: "Engineer Station",
    requirement: "Treasure Hunter profession",
    ingredients: [
      { name: "Iron Block", qty: 2, texture: T("vanilla/iron_block.png") },
      { name: "Arcane Crystal", qty: 2, texture: T("materials/arcane_crystal.png") },
      {
        name: "Slightly Magic Crystallite Shard",
        qty: 1,
        texture: T("materials/crystallite_shard.png"),
      },
      { name: "Slightly Magic Ruby Shard", qty: 1, texture: T("materials/ruby_shard.png") },
      { name: "Slightly Magic Emerald Shard", qty: 1, texture: T("materials/emerald_shard.png") },
    ],
    output: { name: "Unpowered Trace Detector", qty: 1, texture: T("tools/dead_geiger_counter.png") },
  },
  {
    key: "arcane-fuel",
    title: "Arcane Fuel",
    station: "Engineer Station",
    requirement: "Arcane Fuel Maker profession",
    ingredients: [
      { name: "Arcane Crystal", qty: 1, texture: T("materials/arcane_crystal.png") },
      { name: "Copper Block", qty: 4, texture: T("vanilla/copper_block.png") },
    ],
    output: { name: "Arcane Fuel", qty: 16, texture: T("tools/arcane_fuel.png") },
    note: "Yields 16 fuel per craft.",
  },
  {
    key: "trace-detector",
    title: "Arcane Trace Detector",
    station: "Engineer Station",
    requirement: "None",
    ingredients: [
      { name: "Unpowered Trace Detector", qty: 1, texture: T("tools/dead_geiger_counter.png") },
      { name: "Arcane Fuel", qty: 1, texture: T("tools/arcane_fuel.png") },
    ],
    output: { name: "Arcane Trace Detector", qty: 1, texture: T("tools/geiger_counter.png") },
    note: "The same recipe recharges a dead detector — no need to re-craft the base item.",
  },
];

export const signalTable = [
  { signal: "1 ring", meaning: "Over 1000 blocks away." },
  { signal: "2 rings", meaning: "Within 1000 blocks." },
  { signal: "3 rings", meaning: "Within 300 blocks." },
  { signal: "Very dark purple, almost black", meaning: "Near the far edge of range (~2500 blocks)." },
  { signal: "Bright purple", meaning: "~200 blocks out." },
  { signal: "Turning white", meaning: "Under 200 blocks — the whiter, the closer." },
  { signal: "Slow clicking (~1 every 2s)", meaning: "Outer limit of the signal." },
  { signal: "Rapid clicking (a stream)", meaning: "Almost at the source." },
];

export const lootTable = [
  {
    rarity: "Common",
    chance: "45%",
    rewards:
      "32x Grain Bread, 32x Jamon, 8x Raw Tin, 8x Abyssalite Fragment, 1x Mythril Fragment, 32x Raw Iron Block, Weak Repair Kit, Tool Repair Kit, Lost Knowledge Scrap",
  },
  {
    rarity: "Uncommon",
    chance: "30%",
    rewards:
      "12x Raw Tin, 12x Abyssalite Fragment, 2x Mythril Fragment, 1x Mythrilite, 48x Raw Iron Block, Medium Repair Kit, Magical Repair Kit, Sword/Wand/Staff Runestone",
  },
  {
    rarity: "Rare",
    chance: "15%",
    rewards:
      "4x Mythril Fragment, 2x Mythrilite, Trial Key, 64x Raw Iron Block, Strong Repair Kit, 2x Magical Repair Kit, Armor Runestone",
  },
  {
    rarity: "Epic",
    chance: "7%",
    rewards: "3x Mythrilite, 6x Mythril Fragment, 16x Raw Gold Block, Mythical Gemstone Pouch",
  },
  {
    rarity: "Legendary",
    chance: "2.5%",
    rewards:
      "4x Mythrilite, 8x Mythril Fragment, 32x Raw Gold Block, 2x Armor Runestone, 2x Mythical Gemstone Pouch",
  },
  {
    rarity: "Mythical",
    chance: "0.5%",
    rewards: "64x Raw Gold Block, 4x Armor Runestone, 4x Mythical Gemstone Pouch, Skill Point Book",
  },
];

// ---------- Musical Instruments ----------

export const instrumentRecipes: Recipe[] = [
  {
    key: "flute",
    title: "Flute",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Bone", qty: 1, texture: T("vanilla/bone.png") },
      { name: "Stick", qty: 2, texture: T("vanilla/stick.png") },
    ],
    output: { name: "Flute", qty: 1, texture: T("instruments/flute.png") },
    note: "Shift: higher octave.",
  },
  {
    key: "lute",
    title: "Lute",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Oak Planks", qty: 3, texture: T("vanilla/oak_planks.png") },
      { name: "String", qty: 1, texture: T("vanilla/string.png") },
      { name: "Stick", qty: 1, texture: T("vanilla/stick.png") },
    ],
    output: { name: "Lute", qty: 1, texture: T("instruments/lute.png") },
    note: "Shift: chords.",
  },
  {
    key: "vielle",
    title: "Vielle",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Oak Log", qty: 3, texture: T("vanilla/oak_log.png") },
      { name: "String", qty: 1, texture: T("vanilla/string.png") },
      { name: "Stick", qty: 1, texture: T("vanilla/stick.png") },
    ],
    output: { name: "Vielle", qty: 1, texture: T("instruments/vielle.png") },
    note: "Shift: chords.",
  },
  {
    key: "trumpet",
    title: "Trumpet",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Iron Ingot", qty: 2, texture: T("vanilla/iron_ingot.png") },
      { name: "Copper Ingot", qty: 3, texture: T("vanilla/copper_ingot.png") },
    ],
    output: { name: "Trumpet", qty: 1, texture: T("instruments/trumpet.png") },
    note: "Shift: higher octave.",
  },
  {
    key: "celtic-harp",
    title: "Celtic Harp",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Gold Ingot", qty: 3, texture: T("vanilla/gold_ingot.png") },
      { name: "String", qty: 2, texture: T("vanilla/string.png") },
      { name: "Stick", qty: 2, texture: T("vanilla/stick.png") },
    ],
    output: { name: "Celtic Harp", qty: 1, texture: T("instruments/celtic_harp.png") },
    note: "Shift: chords.",
  },
  {
    key: "kalimba",
    title: "Kalimba",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Iron Ingot", qty: 3, texture: T("vanilla/iron_ingot.png") },
      { name: "Note Block", qty: 3, texture: T("vanilla/note_block.png") },
      { name: "Stick", qty: 2, texture: T("vanilla/stick.png") },
    ],
    output: { name: "Kalimba", qty: 1, texture: T("instruments/kalimba.png") },
    note: "Shift: chords.",
  },
  {
    key: "dulcimer",
    title: "Dulcimer",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Iron Ingot", qty: 1, texture: T("vanilla/iron_ingot.png") },
      { name: "String", qty: 2, texture: T("vanilla/string.png") },
      { name: "Stick", qty: 2, texture: T("vanilla/stick.png") },
      { name: "Oak Planks", qty: 4, texture: T("vanilla/oak_planks.png") },
    ],
    output: { name: "Dulcimer", qty: 1, texture: T("instruments/dulcimer.png") },
    note: "Shift: chords.",
  },
  {
    key: "accordion",
    title: "Accordion",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Oak Planks", qty: 4, texture: T("vanilla/oak_planks.png") },
      { name: "Leather", qty: 2, texture: T("vanilla/leather.png") },
      { name: "String", qty: 3, texture: T("vanilla/string.png") },
    ],
    output: { name: "Accordion", qty: 1, texture: T("instruments/accordion.png") },
    note: "Shift: chords.",
  },
  {
    key: "bagpipe",
    title: "Bagpipe",
    station: "Instrument Station",
    requirement: "Bard class",
    ingredients: [
      { name: "Flute", qty: 3, texture: T("instruments/flute.png") },
      { name: "Leather", qty: 5, texture: T("vanilla/leather.png") },
    ],
    output: { name: "Bagpipe", qty: 1, texture: T("instruments/bagpipe.png") },
    note: "Shift: higher octave (same scale, one octave up).",
  },
];

// ---------- Instrument keyboards ----------

export type InstrumentKey = { num: number; note: string; sound: string };

export type InstrumentInfo = {
  slug: string;
  name: string;
  icon: string;
  mode: "chord" | "octave";
  row1: InstrumentKey[];
  row2: InstrumentKey[];
};

const NOTE_LETTERS = ["c", "d", "e", "f", "g", "a", "b", "c"];

function instrumentKeys(folder: string, mode: "chord" | "octave"): { row1: InstrumentKey[]; row2: InstrumentKey[] } {
  const S = (num: number, letter: string, suffix: "single" | "chord") =>
    `/wiki/sounds/instruments/${folder}/${folder}_${num}${letter}_${suffix}.ogg`;

  const row1 = NOTE_LETTERS.map((letter, i) => ({
    num: i + 1,
    note: letter.toUpperCase(),
    sound: S(i + 1, letter, "single"),
  }));

  const row2 =
    mode === "chord"
      ? NOTE_LETTERS.map((letter, i) => ({
          num: i + 1,
          note: letter.toUpperCase(),
          sound: S(i + 1, letter, "chord"),
        }))
      : NOTE_LETTERS.map((letter, i) => ({
          num: i + 9,
          note: letter.toUpperCase(),
          sound: S(i + 9, letter, "single"),
        }));

  return { row1, row2 };
}

const instrumentDefs: Array<{ slug: string; name: string; folder: string; mode: "chord" | "octave" }> = [
  { slug: "flute", name: "Flute", folder: "flute", mode: "octave" },
  { slug: "lute", name: "Lute", folder: "lute", mode: "chord" },
  { slug: "vielle", name: "Vielle", folder: "vielle", mode: "chord" },
  { slug: "trumpet", name: "Trumpet", folder: "trumpet", mode: "octave" },
  { slug: "celtic-harp", name: "Celtic Harp", folder: "celtic_harp", mode: "chord" },
  { slug: "kalimba", name: "Kalimba", folder: "kalimba", mode: "chord" },
  { slug: "dulcimer", name: "Dulcimer", folder: "dulcimer", mode: "chord" },
  { slug: "accordion", name: "Accordion", folder: "accordion", mode: "chord" },
  { slug: "bagpipe", name: "Bagpipe", folder: "bagpipe", mode: "octave" },
];

export const instruments: InstrumentInfo[] = instrumentDefs.map((d) => ({
  slug: d.slug,
  name: d.name,
  icon: T(`instruments/${d.folder}.png`),
  mode: d.mode,
  ...instrumentKeys(d.folder, d.mode),
}));

export function getInstrumentBySlug(slug: string): InstrumentInfo | undefined {
  return instruments.find((i) => i.slug === slug);
}

// ---------- Mount Whistle ("Animal Whistle") ----------

export const whistleRecipe: Recipe = {
  key: "mount-whistle",
  title: "Mount Whistle",
  station: "Animal Station",
  requirement: "None",
  ingredients: [
    { name: "Gold Nugget", qty: 1, texture: T("vanilla/gold_nugget.png") },
    { name: "Iron Nugget", qty: 1, texture: T("vanilla/iron_nugget.png") },
  ],
  output: { name: "Mount Whistle", qty: 1, texture: T("pets/horse_whistle.png") },
};

export const whistleMessages = [
  { message: '"Highlighted 3 animals nearby."', meaning: "Found them — three mounts are glowing right now." },
  { message: '"No animals found nearby."', meaning: "Nothing within 64 blocks." },
  { message: '"The whistle is on cooldown for another 2s."', meaning: "You whistled too fast. Wait a moment." },
];

// ---------- Materials ----------

export const materialRecipes: Recipe[] = [
  // Ingot Station
  {
    key: "coke",
    title: "Coke",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Ignitium", qty: 2, texture: T("materials/ignitium.png") },
      { name: "Coal Block", qty: 1, texture: T("vanilla/coal_block.png") },
    ],
    output: { name: "Coke", qty: 1, texture: T("materials/coke.png") },
  },
  {
    key: "steel-ingot",
    title: "Steel Ingot",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Coke", qty: 2, texture: T("materials/coke.png") },
      { name: "Iron Block", qty: 1, texture: T("vanilla/iron_block.png") },
    ],
    output: { name: "Steel Ingot", qty: 1, texture: T("materials/steel_ingot.png") },
  },
  {
    key: "bronze-ingot",
    title: "Bronze Ingot",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Tin", qty: 2, texture: T("materials/raw_tin.png") },
      { name: "Copper Block", qty: 1, texture: T("vanilla/copper_block.png") },
    ],
    output: { name: "Bronze Ingot", qty: 1, texture: T("materials/bronze_ingot.png") },
  },
  {
    key: "abyssalite-ingot",
    title: "Abyssalite Ingot",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Abyssalite Fragment", qty: 2, texture: T("materials/abyssalite.png") },
      { name: "Bronze Ingot", qty: 1, texture: T("materials/bronze_ingot.png") },
      { name: "Steel Ingot", qty: 1, texture: T("materials/steel_ingot.png") },
    ],
    output: { name: "Abyssalite Ingot", qty: 1, texture: T("materials/abyssalite_ingot.png") },
  },
  {
    key: "mythril-ingot",
    title: "Mythril Ingot",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Mythril Fragment", qty: 2, texture: T("materials/mythril_fragment.png") },
      { name: "Mythrilite", qty: 1, texture: T("materials/mythrilite.png") },
      { name: "Abyssalite Ingot", qty: 1, texture: T("materials/abyssalite_ingot.png") },
    ],
    output: { name: "Mythril Ingot", qty: 1, texture: T("materials/mythril_ingot.png") },
  },
  {
    key: "barkwood",
    title: "Barkwood",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Bark", qty: 4, texture: T("materials/bark.png") },
      { name: "Iron Ingot", qty: 1, texture: T("vanilla/iron_ingot.png") },
    ],
    output: { name: "Barkwood", qty: 1, texture: T("materials/barkwood.png") },
  },
  {
    key: "maplewood",
    title: "Maplewood",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Bark", qty: 4, texture: T("materials/bark.png") },
      { name: "Steel Ingot", qty: 1, texture: T("materials/steel_ingot.png") },
    ],
    output: { name: "Maplewood", qty: 1, texture: T("materials/maplewood.png") },
  },
  {
    key: "elderwood",
    title: "Elderwood",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Bark", qty: 4, texture: T("materials/bark.png") },
      { name: "Abyssalite Ingot", qty: 1, texture: T("materials/abyssalite_ingot.png") },
    ],
    output: { name: "Elderwood", qty: 1, texture: T("materials/elderwood.png") },
  },
  {
    key: "demonwood",
    title: "Demonwood",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [
      { name: "Bark", qty: 4, texture: T("materials/bark.png") },
      { name: "Mythril Ingot", qty: 1, texture: T("materials/mythril_ingot.png") },
    ],
    output: { name: "Demonwood", qty: 1, texture: T("materials/demonwood.png") },
  },
  {
    key: "refined-barkwood",
    title: "Refined Barkwood",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [{ name: "Barkwood", qty: 1, texture: T("materials/barkwood.png") }],
    output: { name: "Refined Barkwood", qty: 1, texture: T("materials/refined_barkwood.png") },
  },
  {
    key: "refined-maplewood",
    title: "Refined Maplewood",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [{ name: "Maplewood", qty: 1, texture: T("materials/maplewood.png") }],
    output: { name: "Refined Maplewood", qty: 1, texture: T("materials/refined_maplewood.png") },
  },
  {
    key: "refined-elderwood",
    title: "Refined Elderwood",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [{ name: "Elderwood", qty: 1, texture: T("materials/elderwood.png") }],
    output: { name: "Refined Elderwood", qty: 1, texture: T("materials/refined_elderwood.png") },
  },
  {
    key: "refined-demonwood",
    title: "Refined Demonwood",
    station: "Ingot Station",
    requirement: "None",
    ingredients: [{ name: "Demonwood", qty: 1, texture: T("materials/demonwood.png") }],
    output: { name: "Refined Demonwood", qty: 1, texture: T("materials/refined_demonwood.png") },
  },
  // Alchemy Station
  {
    key: "alchemy-powder",
    title: "Alchemy Powder",
    station: "Alchemy Station",
    requirement: "Transmutation I",
    ingredients: [
      { name: "Nightshade", qty: 4, texture: T("herbs/icon36.png") },
      { name: "Grapeberries", qty: 4, texture: T("herbs/icon33.png") },
      { name: "Burrow Root", qty: 2, texture: T("herbs/icon32.png") },
      { name: "Nether Wart", qty: 4, texture: T("vanilla/nether_wart.png") },
    ],
    output: { name: "Alchemy Powder", qty: 1, texture: T("materials/alchemy_powder.png") },
  },
  {
    key: "carbon-powder",
    title: "Carbon Powder",
    station: "Alchemy Station",
    requirement: "Transmutation I",
    ingredients: [
      { name: "Arcane Leaf", qty: 2, texture: T("herbs/icon5.png") },
      { name: "Fiery Fruit", qty: 2, texture: T("herbs/icon20.png") },
      { name: "Coal", qty: 4, texture: T("vanilla/coal.png") },
    ],
    output: { name: "Carbon Powder", qty: 2, texture: T("materials/carbon_powder.png") },
  },
  {
    key: "synthetic-ink",
    title: "Synthetic Ink",
    station: "Alchemy Station",
    requirement: "Transmutation I",
    ingredients: [
      { name: "Carbon Powder", qty: 2, texture: T("materials/carbon_powder.png") },
      { name: "Alchemy Powder", qty: 1, texture: T("materials/alchemy_powder.png") },
    ],
    output: { name: "Synthetic Ink", qty: 2, texture: T("materials/synthetic_ink.png") },
  },
  {
    key: "potash",
    title: "Potash",
    station: "Alchemy Station",
    requirement: "Transmutation I",
    ingredients: [
      { name: "Barkshroom", qty: 2, texture: T("herbs/icon24.png") },
      { name: "Caveshroom", qty: 2, texture: T("herbs/icon21.png") },
      { name: "Flatshroom", qty: 2, texture: T("herbs/icon45.png") },
      { name: "Alchemy Powder", qty: 1, texture: T("materials/alchemy_powder.png") },
      { name: "Nether Wart", qty: 4, texture: T("vanilla/nether_wart.png") },
    ],
    output: { name: "Potash", qty: 2, texture: T("materials/potash.png") },
  },
  {
    key: "fertilizer",
    title: "Fertilizer",
    station: "Alchemy Station",
    requirement: "Transmutation I",
    ingredients: [
      { name: "Potash", qty: 2, texture: T("materials/potash.png") },
      { name: "Spot Leaf", qty: 2, texture: T("herbs/icon19.png") },
      { name: "Death Fruit", qty: 1, texture: T("herbs/icon42.png") },
    ],
    output: { name: "Fertilizer", qty: 2, texture: T("materials/fertilizer.png") },
  },
  {
    key: "transmutation-powder",
    title: "Transmutation Powder",
    station: "Alchemy Station",
    requirement: "Transmutation II",
    ingredients: [
      { name: "Long Leaf", qty: 4, texture: T("herbs/icon14.png") },
      { name: "Clover", qty: 4, texture: T("herbs/icon17.png") },
      { name: "Thorn Root", qty: 2, texture: T("herbs/icon41.png") },
      { name: "Alchemy Powder", qty: 1, texture: T("materials/alchemy_powder.png") },
      { name: "Nether Wart", qty: 4, texture: T("vanilla/nether_wart.png") },
    ],
    output: { name: "Transmutation Powder", qty: 2, texture: T("materials/transmutation_powder.png") },
  },
  {
    key: "sulfur",
    title: "Sulfur",
    station: "Alchemy Station",
    requirement: "Transmutation II",
    ingredients: [
      { name: "Dying Leaf", qty: 2, texture: T("herbs/icon29.png") },
      { name: "Autumn Leaf", qty: 2, texture: T("herbs/icon4.png") },
      { name: "Blazed Root", qty: 2, texture: T("herbs/icon44.png") },
      { name: "Transmutation Powder", qty: 1, texture: T("materials/transmutation_powder.png") },
      { name: "Nether Wart", qty: 4, texture: T("vanilla/nether_wart.png") },
    ],
    output: { name: "Sulfur", qty: 2, texture: T("materials/sulfur.png") },
  },
  {
    key: "saltpeter",
    title: "Saltpeter",
    station: "Alchemy Station",
    requirement: "Transmutation II",
    ingredients: [
      { name: "Potash", qty: 2, texture: T("materials/potash.png") },
      { name: "Serpent Root", qty: 2, texture: T("herbs/icon18.png") },
      { name: "Fire Leaf", qty: 2, texture: T("herbs/icon2.png") },
      { name: "Transmutation Powder", qty: 1, texture: T("materials/transmutation_powder.png") },
      { name: "Nether Wart", qty: 4, texture: T("vanilla/nether_wart.png") },
      { name: "Blaze Powder", qty: 2, texture: T("vanilla/blaze_powder.png") },
    ],
    output: { name: "Saltpeter", qty: 2, texture: T("materials/saltpeter.png") },
  },
  // Magic Station
  {
    key: "basic-handle",
    title: "Basic Magical Handle",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Enchanted Dust", qty: 8, texture: T("magic_crafting/enchanted_dust.png") },
      { name: "Stick", qty: 2, texture: T("vanilla/stick.png") },
    ],
    output: { name: "Basic Magical Handle", qty: 1, texture: T("magic_crafting/basic_magical_handle.png") },
  },
  {
    key: "petty-handle",
    title: "Petty Magical Handle",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Basic Magical Handle", qty: 1, texture: T("magic_crafting/basic_magical_handle.png") },
      { name: "Enchanted Dust", qty: 8, texture: T("magic_crafting/enchanted_dust.png") },
    ],
    output: { name: "Petty Magical Handle", qty: 1, texture: T("magic_crafting/petty_magical_handle.png") },
  },
  {
    key: "heavy-handle",
    title: "Heavy Magical Handle",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Petty Magical Handle", qty: 1, texture: T("magic_crafting/petty_magical_handle.png") },
      { name: "Enchanted Dust", qty: 8, texture: T("magic_crafting/enchanted_dust.png") },
    ],
    output: { name: "Heavy Magical Handle", qty: 1, texture: T("magic_crafting/heavy_magical_handle.png") },
  },
  {
    key: "petty-tome",
    title: "Petty Magical Tome",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Enchanted Dust", qty: 8, texture: T("magic_crafting/enchanted_dust.png") },
      { name: "Book", qty: 1, texture: T("vanilla/book.png") },
    ],
    output: { name: "Petty Magical Tome", qty: 1, texture: T("magic_crafting/binding_tome.png") },
  },
  {
    key: "heavy-tome",
    title: "Heavy Magical Tome",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Petty Magical Tome", qty: 1, texture: T("magic_crafting/binding_tome.png") },
      { name: "Enchanted Dust", qty: 8, texture: T("magic_crafting/enchanted_dust.png") },
    ],
    output: { name: "Heavy Magical Tome", qty: 1, texture: T("magic_crafting/strong_binding_tome.png") },
  },
  {
    key: "iron-core",
    title: "Iron Magical Core",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Slightly Magic Crystallite Shard", qty: 2, texture: T("materials/crystallite_shard.png") },
      { name: "Enchanted Dust", qty: 8, texture: T("magic_crafting/enchanted_dust.png") },
      { name: "Iron Ingot", qty: 6, texture: T("vanilla/iron_ingot.png") },
    ],
    output: { name: "Iron Magical Core", qty: 1, texture: T("magic_crafting/makeshift_magical_core.png") },
  },
  {
    key: "steel-core",
    title: "Steel Magical Core",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Iron Magical Core", qty: 1, texture: T("magic_crafting/makeshift_magical_core.png") },
      { name: "Steel Ingot", qty: 6, texture: T("materials/steel_ingot.png") },
      { name: "Slightly Magic Ruby Shard", qty: 2, texture: T("materials/ruby_shard.png") },
      { name: "Enchanted Dust", qty: 8, texture: T("magic_crafting/enchanted_dust.png") },
    ],
    output: { name: "Steel Magical Core", qty: 1, texture: T("magic_crafting/basic_magical_core.png") },
  },
  {
    key: "abyssalite-core",
    title: "Abyssalite Magical Core",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Steel Magical Core", qty: 1, texture: T("magic_crafting/basic_magical_core.png") },
      { name: "Abyssalite Ingot", qty: 6, texture: T("materials/abyssalite_ingot.png") },
      { name: "Petty Magical Tome", qty: 2, texture: T("magic_crafting/binding_tome.png") },
      { name: "Slightly Magic Emerald Shard", qty: 2, texture: T("materials/emerald_shard.png") },
    ],
    output: { name: "Abyssalite Magical Core", qty: 1, texture: T("magic_crafting/petty_magical_core.png") },
  },
  {
    key: "mythril-core",
    title: "Mythril Magical Core",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Abyssalite Magical Core", qty: 1, texture: T("magic_crafting/petty_magical_core.png") },
      { name: "Mythril Ingot", qty: 6, texture: T("materials/mythril_ingot.png") },
      { name: "Heavy Magical Tome", qty: 2, texture: T("magic_crafting/strong_binding_tome.png") },
      { name: "Slightly Magic Emerald Shard", qty: 4, texture: T("materials/emerald_shard.png") },
    ],
    output: { name: "Mythril Magical Core", qty: 1, texture: T("magic_crafting/heavy_magical_core.png") },
  },
  {
    key: "enchanted-leather",
    title: "Enchanted Leather",
    station: "Magic Station",
    requirement: "Mage class",
    ingredients: [
      { name: "Leather", qty: 4, texture: T("vanilla/leather.png") },
      { name: "Enchanted Dust", qty: 4, texture: T("magic_crafting/enchanted_dust.png") },
    ],
    output: { name: "Enchanted Leather", qty: 8, texture: T("magic_crafting/enchanted_leather.png") },
  },
  // Engineer Station
  {
    key: "dynamite",
    title: "Dynamite",
    station: "Engineer Station",
    requirement: "Dynamite Maker profession",
    ingredients: [
      { name: "Niter", qty: 1, texture: T("materials/niter.png") },
      { name: "Paper", qty: 2, texture: T("vanilla/paper.png") },
    ],
    output: { name: "Dynamite", qty: 1, texture: T("materials/dynamite.png") },
  },
  // Medicine Station
  {
    key: "detoxed-leather",
    title: "Detoxed Leather",
    station: "Medicine Station",
    requirement: "Physician profession",
    ingredients: [{ name: "Leather", qty: 2, texture: T("vanilla/leather.png") }],
    output: { name: "Detoxed Leather", qty: 2, texture: T("materials/detoxed_leather.png") },
  },
];

export const leatherInlineRecipe = {
  note: "Leather has a special 3x3 recipe: a single Saddle in the centre slot with every other slot left empty.",
};

export type DropOnlyMaterial = {
  name: string;
  texture?: string;
  lore?: string;
};

export const dropOnlyMaterials: DropOnlyMaterial[] = [
  { name: "Ignitium", texture: T("materials/ignitium.png"), lore: "Uncommon crystal — catalyst in Coke production." },
  { name: "Tin", texture: T("materials/raw_tin.png"), lore: "Malleable metal used to produce alloys like Bronze." },
  {
    name: "Abyssalite Fragment",
    texture: T("materials/abyssalite.png"),
    lore: "Tough fragment of metal, an upgrade path from Steel.",
  },
  {
    name: "Mythril Fragment",
    texture: T("materials/mythril_fragment.png"),
    lore: "A metal of legend — the successor to Abyssalite in utility.",
  },
  {
    name: "Mythrilite",
    texture: T("materials/mythrilite.png"),
    lore: "One of the rarest materials in Cerrith; unlocks Mythril's potential.",
  },
  { name: "Bark", texture: T("materials/bark.png") },
  {
    name: "Slightly Magic Crystallite Shard",
    texture: T("materials/crystallite_shard.png"),
    lore: "Gemstone for Goldsmithing, used in Magical items.",
  },
  {
    name: "Slightly Magic Ruby Shard",
    texture: T("materials/ruby_shard.png"),
    lore: "Gemstone for Goldsmithing, used in Magical items.",
  },
  {
    name: "Slightly Magic Emerald Shard",
    texture: T("materials/emerald_shard.png"),
    lore: "Gemstone for Goldsmithing, used in Magical items.",
  },
  { name: "Bloodmagic Essence", texture: T("magic_crafting/bloodmagic_essence.png") },
  { name: "Necromancy Essence", texture: T("magic_crafting/necromancy_essence.png") },
  { name: "Wood Core", texture: T("materials/wood_core.png") },
  { name: "Flower Core", texture: T("materials/flower_core.png") },
  { name: "Valewood", texture: T("materials/valewood.png") },
  { name: "Runebark", texture: T("materials/runebark.png") },
  { name: "Amberpine", texture: T("materials/amberpine.png") },
  { name: "Goldmaple", texture: T("materials/goldmaple.png") },
  { name: "Silk", texture: T("materials/silk.png") },
  {
    name: "Moldable Gold",
    texture: T("materials/moldable_gold.png"),
    lore: "Uncommon gold variant with Goldsmithing applications.",
  },
  {
    name: "Rough Gold",
    texture: T("materials/rough_gold.png"),
    lore: "Common gold variant with Goldsmithing applications.",
  },
  {
    name: "Shiny Gold",
    texture: T("materials/shiny_gold.png"),
    lore: "Rare gold variant with Goldsmithing applications.",
  },
  { name: "Arcane Crystal", texture: T("materials/arcane_crystal.png"), lore: "Found deep below the earth — not of this Plane." },
  { name: "Niter", texture: T("materials/niter.png") },
  { name: "Smokeless Powder", texture: T("materials/smokeless_powder.png") },
  { name: "Raw Iron Fragment", texture: T("materials/rawiron_fragment.png"), lore: "Crafted into Iron Ingots at a Fishing Station." },
  { name: "Raw Gold Fragment", texture: T("materials/rawgold_fragment.png"), lore: "Crafted into Gold Ingots at a Fishing Station." },
  { name: "Diamond Fragment", texture: T("materials/diamond_fragment.png"), lore: "Crafted into Diamonds at a Fishing Station." },
  { name: "Fossil", texture: T("materials/fossil.png") },
  { name: "Good Quality Leather", texture: T("pets/rareleather.png"), lore: "Used to make weapons and armor on the Anvil." },
  { name: "Great Quality Leather", texture: T("pets/epicleather.png"), lore: "Used to make weapons and armor on the Anvil." },
  { name: "Perfect Quality Leather", texture: T("pets/legendaryleather.png"), lore: "Used to make weapons and armor on the Anvil." },
  { name: "Good Quality Feather", texture: T("pets/rarefeather.png"), lore: "Used to make weapons and armor on the Anvil." },
  { name: "Great Quality Feather", texture: T("pets/epicfeather.png"), lore: "Used to make weapons and armor on the Anvil." },
  { name: "Perfect Quality Feather", texture: T("pets/legendaryfeather.png"), lore: "Used to make weapons and armor on the Anvil." },
  { name: "Good Quality Wool", texture: T("pets/rarewool.png"), lore: "Used to make weapons and armor on the Anvil." },
  { name: "Great Quality Wool", texture: T("pets/epicwool.png"), lore: "Used to make weapons and armor on the Anvil." },
  { name: "Perfect Quality Wool", texture: T("pets/legendarywool.png"), lore: "Used to make weapons and armor on the Anvil." },
  // Alchemy herbs — gathered from the world, used as Alchemy Station reagents.
  { name: "Nightshade", texture: T("herbs/icon36.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Grapeberries", texture: T("herbs/icon33.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Burrow Root", texture: T("herbs/icon32.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Arcane Leaf", texture: T("herbs/icon5.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Fiery Fruit", texture: T("herbs/icon20.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Barkshroom", texture: T("herbs/icon24.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Caveshroom", texture: T("herbs/icon21.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Flatshroom", texture: T("herbs/icon45.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Spot Leaf", texture: T("herbs/icon19.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Death Fruit", texture: T("herbs/icon42.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Long Leaf", texture: T("herbs/icon14.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Clover", texture: T("herbs/icon17.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Thorn Root", texture: T("herbs/icon41.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Dying Leaf", texture: T("herbs/icon29.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Autumn Leaf", texture: T("herbs/icon4.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Blazed Root", texture: T("herbs/icon44.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Serpent Root", texture: T("herbs/icon18.png"), lore: "Herbal reagent gathered from the world." },
  { name: "Fire Leaf", texture: T("herbs/icon2.png"), lore: "Herbal reagent gathered from the world." },
];

// ---------- Slugs, cross-links ----------

export function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

const allRecipeCollections: Recipe[][] = [
  detectorRecipes,
  instrumentRecipes,
  [whistleRecipe],
  materialRecipes,
];

// ---------- Stations ----------

export type StationInfo = {
  slug: string;
  name: string;
  blurb: string;
  icon: string;
  model?: { url: string; texture: string };
  fallbackTexture?: string;
  /** How to craft the physical station block/furniture itself, if it has one. */
  craftRecipe?: Recipe;
  /** Set when the station has no placeable block (opened via NPC/command instead). */
  noPlaceableBlock?: boolean;
  /**
   * Set when this "station" is really a re-skinned vanilla block. Name it, and note how to
   * open its custom menu (usually shift+right-click instead of a plain right-click).
   */
  vanillaBlock?: { name: string; accessNote: string };
  /** Per-face textures for a plain vanilla cube block, rendered with SimpleCubeViewer. */
  cubeFaces?: { up: string; down: string; north: string; south: string; east: string; west: string };
};

const M = (path: string) => `/wiki/models/${path}`;
const V = (file: string) => T(`vanilla/${file}`);
const empty: Slot = { name: "", qty: 0 };

const engineerModel = { url: M("engineer-station.json"), texture: T("stations/engineer-station.png") };
const animalModel = { url: M("animal-station.json"), texture: T("stations/animal-station.png") };
const alchemyModel = { url: M("alchemy-station.json"), texture: T("stations/alchemy-station.png") };
const magicModel = { url: M("magic-station.json"), texture: T("stations/magic-station.png") };

const alchemyStationCraft: Recipe = {
  key: "craft-alchemy-station",
  title: "Alchemy Station",
  station: "Crafting Table",
  requirement: "None",
  ingredients: [
    empty,
    { name: "Diamond", qty: 1, texture: V("diamond.png") },
    empty,
    empty,
    { name: "Diamond", qty: 1, texture: V("diamond.png") },
    empty,
    { name: "Stone", qty: 1, texture: V("stone.png") },
    { name: "Stone", qty: 1, texture: V("stone.png") },
    { name: "Stone", qty: 1, texture: V("stone.png") },
  ],
  output: { name: "Alchemy Station", qty: 1, model: alchemyModel },
};

export const stations: StationInfo[] = [
  {
    slug: "engineer-station",
    name: "Engineer Station",
    blurb: "Trace detectors, arcane fuel, ammunition, and dynamite.",
    icon: T("tools/geiger_counter.png"),
    model: engineerModel,
    craftRecipe: {
      key: "craft-engineer-station",
      title: "Engineering Table",
      station: "Crafting Table",
      requirement: "None",
      ingredients: [
        { name: "Iron Ingot", qty: 1, texture: V("iron_ingot.png") },
        { name: "Iron Ingot", qty: 1, texture: V("iron_ingot.png") },
        { name: "Iron Ingot", qty: 1, texture: V("iron_ingot.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
      ],
      output: { name: "Engineering Table", qty: 1, model: engineerModel },
    },
  },
  {
    slug: "instrument-station",
    name: "Instrument Station",
    blurb: "All nine musical instruments, Bard class required.",
    icon: V("jukebox_top.png"),
    fallbackTexture: V("jukebox_top.png"),
    vanillaBlock: {
      name: "Jukebox",
      accessNote:
        "This is a plain vanilla Jukebox. Shift+right-click it to open the Instrument Station menu — a normal right-click just plays a disc like usual.",
    },
    cubeFaces: {
      up: V("jukebox_top.png"),
      down: V("jukebox_side.png"),
      north: V("jukebox_side.png"),
      south: V("jukebox_side.png"),
      east: V("jukebox_side.png"),
      west: V("jukebox_side.png"),
    },
  },
  {
    slug: "animal-station",
    name: "Animal Station",
    blurb: "Mount Whistle, taming tokens, and pet feed.",
    icon: T("pets/horse_whistle.png"),
    model: animalModel,
    craftRecipe: {
      key: "craft-animal-station",
      title: "Animal Station",
      station: "Crafting Table",
      requirement: "None",
      ingredients: [
        { name: "Oak Log", qty: 1, texture: V("oak_log.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Log", qty: 1, texture: V("oak_log.png") },
        { name: "Oak Log", qty: 1, texture: V("oak_log.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Log", qty: 1, texture: V("oak_log.png") },
        { name: "Oak Log", qty: 1, texture: V("oak_log.png") },
        { name: "Oak Log", qty: 1, texture: V("oak_log.png") },
        { name: "Oak Log", qty: 1, texture: V("oak_log.png") },
      ],
      output: { name: "Animal Station", qty: 1, model: animalModel },
    },
  },
  {
    slug: "ingot-station",
    name: "Ingot Station",
    blurb: "Smelts raw materials into Steel, Bronze, Abyssalite, and Mythril ingots.",
    icon: V("blast_furnace_front.png"),
    fallbackTexture: V("blast_furnace_front.png"),
    vanillaBlock: {
      name: "Blast Furnace",
      accessNote:
        "This is a plain vanilla Blast Furnace. Shift+right-click it to open the Ingot Station menu — a normal right-click opens the regular smelting GUI instead.",
    },
    cubeFaces: {
      up: V("blast_furnace_top.png"),
      down: V("blast_furnace_top.png"),
      north: V("blast_furnace_front.png"),
      south: V("blast_furnace_side.png"),
      east: V("blast_furnace_side.png"),
      west: V("blast_furnace_side.png"),
    },
  },
  {
    slug: "alchemy-station",
    name: "Alchemy Station",
    blurb: "Herbal powders and reagents — Transmutation profession.",
    icon: T("materials/alchemy_powder.png"),
    model: alchemyModel,
    craftRecipe: alchemyStationCraft,
  },
  {
    slug: "magic-station",
    name: "Magic Station",
    blurb: "Magical handles, tomes, and cores — Mage class required.",
    icon: T("magic_crafting/heavy_magical_core.png"),
    model: magicModel,
    craftRecipe: {
      key: "craft-magic-station",
      title: "Magic Crafting Station",
      station: "Crafting Table",
      requirement: "None",
      ingredients: [
        { name: "Blackstone", qty: 1, texture: V("blackstone.png") },
        { name: "Blackstone", qty: 1, texture: V("blackstone.png") },
        { name: "Blackstone", qty: 1, texture: V("blackstone.png") },
        { name: "Blackstone", qty: 1, texture: V("blackstone.png") },
        { name: "Gold Ingot", qty: 1, texture: V("gold_ingot.png") },
        { name: "Blackstone", qty: 1, texture: V("blackstone.png") },
        { name: "Blackstone", qty: 1, texture: V("blackstone.png") },
        { name: "Amethyst Shard", qty: 1, texture: V("amethyst_shard.png") },
        { name: "Blackstone", qty: 1, texture: V("blackstone.png") },
      ],
      output: { name: "Magic Crafting Station", qty: 1, model: magicModel },
    },
  },
  {
    slug: "medicine-station",
    name: "Medicine Station",
    blurb: "Detoxed Leather and other physician goods. Shares its block with the Alchemy Station.",
    icon: T("materials/detoxed_leather.png"),
    model: alchemyModel,
    craftRecipe: alchemyStationCraft,
  },
];

export function getStationBySlug(slug: string): StationInfo | undefined {
  return stations.find((s) => s.slug === slug);
}

export function getRecipesForStation(name: string): Recipe[] {
  return allRecipeCollections.flat().filter((r) => r.station === name);
}

// ---------- Material catalogue (for cross-linking + detail pages) ----------

export type MaterialCatalogEntry = {
  slug: string;
  name: string;
  texture?: string;
  lore?: string;
  recipe?: Recipe;
  usedIn: Recipe[];
};

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
  for (const m of dropOnlyMaterials) {
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

  for (const r of allRecipeCollections.flat()) {
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
