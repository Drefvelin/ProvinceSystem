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
