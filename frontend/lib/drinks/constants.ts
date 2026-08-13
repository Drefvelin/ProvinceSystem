/** Common potion effects shown in the brew editor (blacklist filtered client-side). */
export const COMMON_EFFECTS = [
  "nausea",
  "blindness",
  "confusion",
  "hunger",
  "poison",
  "wither",
  "weakness",
  "slowness",
  "mining_fatigue",
  "levitation",
  "slow_falling",
  "darkness",
  "jump_boost",
  "night_vision",
  "water_breathing",
  "luck",
  "unluck",
  "glowing",
] as const;

const EFFECT_LABELS: Record<string, string> = {
  nausea: "Nausea",
  blindness: "Blindness",
  confusion: "Nausea (Confusion)",
  hunger: "Hunger",
  poison: "Poison",
  wither: "Wither",
  weakness: "Weakness",
  slowness: "Slowness",
  mining_fatigue: "Mining Fatigue",
  levitation: "Levitation",
  slow_falling: "Slow Falling",
  darkness: "Darkness",
  jump_boost: "Jump Boost",
  night_vision: "Night Vision",
  water_breathing: "Water Breathing",
  luck: "Luck",
  unluck: "Bad Luck",
  glowing: "Glowing",
};

export function effectLabel(id: string): string {
  const key = (id || "").trim().toLowerCase();
  if (EFFECT_LABELS[key]) return EFFECT_LABELS[key];
  return key
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export const WOOD_OPTIONS: Array<{ id: string; label: string }> = [
  { id: "0", label: "Any" },
  { id: "oak", label: "Oak" },
  { id: "birch", label: "Birch" },
  { id: "spruce", label: "Spruce" },
  { id: "jungle", label: "Jungle" },
  { id: "acacia", label: "Acacia" },
  { id: "dark_oak", label: "Dark Oak" },
  { id: "mangrove", label: "Mangrove" },
  { id: "cherry", label: "Cherry" },
  { id: "bamboo", label: "Bamboo" },
  { id: "crimson", label: "Crimson" },
  { id: "warped", label: "Warped" },
  { id: "pale_oak", label: "Pale Oak" },
  { id: "cut_copper", label: "Cut Copper" },
];

export const MAX_PNG_BYTES = 512 * 1024;
export const EXPECTED_PNG_SIZE = 16;
