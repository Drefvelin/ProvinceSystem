import type { SkinKind } from "./sizes";

/** Mirrors backend BASE_SETS (step-8 / batch 8.01). */
export const BASE_SETS: Record<SkinKind, readonly string[]> = {
  armor_set: ["iron", "steel", "abyssalite", "mythril", "mage", "infantry"],
  handheld: [
    "swords",
    "battleaxes",
    "daggers",
    "warhammers",
    "shortswords",
    "hatchets",
    "hoes",
    "knives",
  ],
  large_handheld: ["spears", "polearms", "greathammers", "staffs"],
  bow: ["shortbows"],
  large_bow: ["longbows"],
  crossbow: ["crossbows"],
};

const LABELS: Record<string, string> = {
  iron: "Iron",
  steel: "Steel",
  abyssalite: "Abyssalite",
  mythril: "Mythril",
  mage: "Mage",
  infantry: "Infantry",
  swords: "Swords",
  battleaxes: "Battleaxes",
  daggers: "Daggers",
  warhammers: "Warhammers",
  shortswords: "Shortswords",
  hatchets: "Hatchets",
  hoes: "Hoes",
  knives: "Knives",
  spears: "Spears",
  polearms: "Polearms",
  greathammers: "Greathammers",
  staffs: "Staffs",
  shortbows: "Shortbows",
  longbows: "Longbows",
  crossbows: "Crossbows",
};

export function baseSetsForKind(kind: SkinKind): readonly string[] {
  return BASE_SETS[kind];
}

export function baseSetLabel(id: string): string {
  return LABELS[id] ?? id;
}

export function defaultBaseSet(kind: SkinKind): string {
  return BASE_SETS[kind][0];
}

export function baseSetPickerTitle(kind: SkinKind): string {
  return kind === "armor_set" ? "Armor tier" : "Applicable type";
}
