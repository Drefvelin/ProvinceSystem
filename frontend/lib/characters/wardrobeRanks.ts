/** Wardrobe lock labels from catalog slot_limits groups. */

import type { SlotLimits } from "./api";
import { parseNameRuns, type LoreRun } from "./lorePreview";

export type RankLockLabel = {
  /** Plain fallback e.g. "Gilded+" */
  plain: string;
  /** Coloured runs from group display_name when available */
  runs: LoreRun[];
};

function visibleGroups(slotLimits: SlotLimits | undefined) {
  const groups = slotLimits?.groups;
  if (!Array.isArray(groups)) return [];
  return groups
    .filter((g) => g && g.visible !== false)
    .slice()
    .sort((a, b) => Number(a.tier ?? 0) - Number(b.tier ?? 0));
}

/** First visible group that grants at least `minSlots` swappable skins. */
export function groupUnlockingSlots(
  slotLimits: SlotLimits | undefined,
  minSlots: number
): { id?: string; display_name?: string; wardrobe_skin_slots?: number } | null {
  for (const g of visibleGroups(slotLimits)) {
    const n = Number(g.wardrobe_skin_slots ?? 0);
    if (n >= minSlots) return g;
  }
  return null;
}

const FALLBACK: Record<string, string> = {
  extra_1: "Gilded+",
  extra_2: "Ascended+",
};

/** Lock copy for a wardrobe extra slot. */
export function lockLabelForSlot(
  slot: string,
  slotLimits: SlotLimits | undefined
): RankLockLabel {
  const key = String(slot || "").toLowerCase();
  const minSlots = key === "extra_2" ? 3 : key === "extra_1" ? 2 : 0;
  if (minSlots <= 0) {
    return { plain: "Locked", runs: [{ text: "Locked", color: "#ffffff" }] };
  }
  const group = groupUnlockingSlots(slotLimits, minSlots);
  const display = String(group?.display_name || "").trim();
  if (display) {
    const runs = parseNameRuns(display);
    // Append "+" in the last run's colour
    if (runs.length > 0) {
      const last = runs[runs.length - 1]!;
      return {
        plain: `${runs.map((r) => r.text).join("")}+`,
        runs: [
          ...runs.slice(0, -1),
          { ...last, text: `${last.text}+` },
        ],
      };
    }
  }
  const plain = FALLBACK[key] || "Higher rank+";
  return { plain, runs: [{ text: plain, color: "#ffffff" }] };
}

export function minSlotsForExtra(slot: string): number {
  const key = String(slot || "").toLowerCase();
  if (key === "extra_2") return 3;
  if (key === "extra_1") return 2;
  return 0;
}
