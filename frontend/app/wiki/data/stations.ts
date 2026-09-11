import { M, T, V, empty } from "./helpers";
import { stationRecipes } from "./station-recipes";
import type { Recipe, StationInfo, WikiSection } from "./types";

// ---------- Stations ----------

const vehicleStationTexture = (station: string, file: string) => T(`vehicle-stations/${station}/${file}.png`);
const engineerModel = { url: M("vehicles/ammunition_station.json"), textures: {
  "0": vehicleStationTexture("ammunition_station", "bullet"),
  "1": vehicleStationTexture("ammunition_station", "pin"),
  "2": vehicleStationTexture("ammunition_station", "stand"),
  "3": vehicleStationTexture("ammunition_station", "bag"),
  "4": vehicleStationTexture("ammunition_station", "wood4"),
  "5": vehicleStationTexture("ammunition_station", "powder"),
  "6": vehicleStationTexture("ammunition_station", "bullet2"),
  "8": vehicleStationTexture("ammunition_station", "wood2"),
  "9": vehicleStationTexture("ammunition_station", "wood1"),
  particle: vehicleStationTexture("ammunition_station", "bullet"),
} };
const animalModel = { url: M("animal-station.json"), texture: T("stations/animal-station.png") };
const alchemyModel = { url: M("alchemy-station.json"), texture: T("stations/alchemy-station.png") };
const birdMailboxModel = { url: M("bird-mailbox.json"), texture: T("bird-mail/mailbox.png") };
const magicModel = { url: M("magic-station.json"), texture: T("stations/magic-station.png") };
const weaponModel = { url: M("weapon-station.json"), texture: T("stations/weapon-station.png") };
const converterModel = { url: M("ingredient-converter.json"), texture: T("stations/ingredient-converter.png") };
const alloyModel = { url: M("alloy-forge.json"), texture: T("stations/alloy-forge.png"), textureAnimationUrl: T("stations/alloy-forge.png.mcmeta") };
const recyclingModel = { url: M("recycling-station.json"), texture: T("stations/recycling-station.png") };
const dockyardModel = { url: M("vehicles/dockyard.json"), textures: {
  bottom: vehicleStationTexture("dockyard", "bottom"),
  side: vehicleStationTexture("dockyard", "side"),
  front: vehicleStationTexture("dockyard", "front"),
  top: vehicleStationTexture("dockyard", "top"),
  particle: vehicleStationTexture("dockyard", "side"),
} };
const grindstoneModel = { url: M("stations/grindstone.json"), textures: {
  pivot: T("stations/grindstone/pivot.png"),
  round: T("stations/grindstone/round.png"),
  side: T("stations/grindstone/side.png"),
  leg: T("stations/grindstone/leg.png"),
  particle: T("stations/grindstone/side.png"),
} };
const fishingStationModel = { url: M("stations/fishing-station.json"), textures: {
  "2": T("stations/fishing-station/fishing-station.png"),
} };
const gunsmithingStationModel = { url: M("stations/gunsmithing-station.json"), textures: {
  "4": T("stations/gunsmithing-station/wood_m.png"),
  "8": T("stations/gunsmithing-station/wood2.png"),
  "9": T("stations/gunsmithing-station/wood1.png"),
  "11": T("stations/gunsmithing-station/manifest.png"),
  "14": T("stations/gunsmithing-station/pistol.png"),
  particle: T("stations/gunsmithing-station/bullet.png"),
} };
const mealPrepStationModel = { url: M("stations/meal-prep-station.json"), textures: {
  "0": T("stations/meal-prep-station/meal-prep-station.png"),
  particle: T("stations/meal-prep-station/meal-prep-station.png"),
} };

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
    slug: "weapon-station",
    name: "Weapon Station",
    blurb: "Hands-on crafting for weapons, armour, and bows.",
    icon: T("stations/weapon-station.png"),
    model: weaponModel,
  },
  {
    slug: "ingredient-converter",
    name: "Ingredient Converter",
    blurb: "Previews how a raw material contributes to an Advanced Crafting project.",
    icon: T("stations/ingredient-converter.png"),
    model: converterModel,
  },
  {
    slug: "alloy-forge",
    name: "Alloy Forge",
    blurb: "Combines base materials and catalysts into named alloys.",
    icon: T("stations/alloy-forge.png"),
    model: alloyModel,
  },
  {
    slug: "recycling-station",
    name: "Recycling Station",
    blurb: "Returns materials from supported weapons, armour, guns, and dedicated recipes.",
    icon: T("stations/recycling-station.png"),
    model: recyclingModel,
  },
  {
    slug: "fishing-station",
    name: "Fishing Station",
    blurb: "Crafts fishing rods and processes recovered fragments.",
    // The block's only texture is a 256x96 atlas, which is unreadable at icon size.
    // Use the rod item texture instead, as gunsmithing-station does with an ammo sprite.
    icon: T("fishing-rods/fishing_rod.png"),
    model: fishingStationModel,
  },
  {
    slug: "gunsmithing-station",
    name: "Gunsmithing Station",
    blurb: "Crafts gun parts for players with the Musketeer class.",
    // pistol.png is a UV-mapped face of the block model, not an item sprite, so it
    // reads as a blob at 16px. Use the bronzeshot ammo item texture instead.
    icon: T("ammunition/bronzeshot.png"),
    model: gunsmithingStationModel,
  },
  {
    slug: "meal-prep-station",
    name: "Meal Prep Station",
    blurb: "Crafts cooking furniture and prepares food before cooking.",
    // The block's only texture is a 64x64 model atlas, which is unreadable at icon
    // size. No clean cookware sprite exists in the texture set, so use the vanilla
    // campfire item sprite as the closest readable cooking icon.
    icon: V("campfire.png"),
    model: mealPrepStationModel,
  },
  {
    slug: "block-station",
    name: "Block Station",
    blurb: "Crafts furniture, displays, and building pieces.",
    icon: T("stations/grindstone/side.png"),
    model: grindstoneModel,
  },
  {
    slug: "dockyard",
    name: "Dockyard",
    blurb: "Builds ships after their blueprints are selected.",
    icon: T("vehicle-stations/dockyard/front.png"),
    model: dockyardModel,
  },
  {
    slug: "archeology-station",
    name: "Archeology Station",
    blurb: "Field equipment for surveying, excavating, cleaning, and registering finds.",
    // The block's only texture is a 64x64 model atlas, which is unreadable at icon
    // size. Use the vanilla brush item sprite instead, since a brush is the
    // vanilla archaeology tool and one of this station's own workshop recipes.
    icon: V("brush.png"),
    model: { url: M("archeology-station.json"), texture: T("stations/archeology-station.png") },
    craftRecipe: {
      key: "craft-archeology-station",
      title: "Archeology Table",
      station: "Crafting Table",
      requirement: "None",
      ingredients: [
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Bone", qty: 1, texture: V("bone.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
        { name: "Oak Planks", qty: 1, texture: V("oak_planks.png") },
      ],
      output: { name: "Archeology Table", qty: 1, model: { url: M("archeology-station.json"), texture: T("stations/archeology-station.png") } },
    },
  },
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
        "This is a plain vanilla Jukebox. Shift+right-click it to open the Instrument Station menu: a normal right-click just plays a disc like usual.",
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
        "This is a plain vanilla Blast Furnace. Shift+right-click it to open the Ingot Station menu: a normal right-click opens the regular smelting GUI instead.",
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
    blurb: "Herbal powders and reagents: Transmutation profession.",
    icon: T("materials/alchemy_powder.png"),
    model: alchemyModel,
    craftRecipe: alchemyStationCraft,
  },
  {
    slug: "magic-station",
    name: "Magic Station",
    blurb: "Magical handles, tomes, and cores: Mage class required.",
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
  {
    slug: "copper-station",
    name: "Copper Station",
    // No block model exists for this station yet, so it gets an item sprite only.
    // Copper Ingot is the material every recipe here is built from.
    blurb: "Every copper block variant: cut, chiselled, grates, bulbs, doors, and their waxed forms.",
    icon: V("copper_ingot.png"),
    fallbackTexture: V("copper_ingot.png"),
  },
  {
    slug: "forester-station",
    name: "Forester Station",
    blurb: "Logs, leaves, saplings, flowers, mushrooms, and every plant dye.",
    icon: V("oak_log.png"),
    fallbackTexture: V("oak_log.png"),
  },
  {
    slug: "tool-station",
    name: "Tool Station",
    blurb: "Iron through Mythril tools, profession toolkits, mount gear, and lockpicks.",
    icon: V("iron_pickaxe.png"),
    fallbackTexture: V("iron_pickaxe.png"),
  },
  {
    slug: "research-station",
    name: "Research Station",
    blurb: "Turns research papers into materials, currency, and runestones.",
    icon: V("book.png"),
    fallbackTexture: V("book.png"),
  },
  {
    slug: "bird-mailbox",
    name: "Bird Mailbox",
    blurb: "Right-click it to send a written Letter to another character: the block behind the Bird Mail system.",
    icon: T("bird-mail/mailbox.png"),
    model: birdMailboxModel,
  },
];

export function getStationBySlug(slug: string): StationInfo | undefined {
  return stations.find((s) => s.slug === slug);
}

export const stationsSection: WikiSection = {
  nav: {
    href: "/wiki/stations",
    label: "Stations",
    category: "reference",
    blurb: "Every crafting station, with an interactive 3D preview where a model exists.",
  },
  // Station *craft* recipes (`StationInfo.craftRecipe`) intentionally stay out of
  // the global recipe index: they are rendered on the station's own page only,
  // as they always have been.
  //
  // What is registered here is every recipe read off the server's crafting-station
  // configs. Registering them once, here, is what puts them on station pages and
  // into the materials "used in" index.
  recipes: stationRecipes,
};
