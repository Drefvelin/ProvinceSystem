import type { EditorTier } from "@/lib/map/api";

const TIER_PREFIX: Record<EditorTier, string> = {
  county: "COUNTY",
  duchy: "DUCHY",
  kingdom: "KINGDOM",
  empire: "EMPIRE",
};

export function nextTitleId(tier: EditorTier, draft: Record<string, unknown>): string {
  const prefix = TIER_PREFIX[tier];
  let max = 0;
  for (const key of Object.keys(draft)) {
    if (!key.startsWith(`${prefix}_`)) continue;
    const suffix = key.slice(prefix.length + 1);
    const num = Number.parseInt(suffix, 10);
    if (!Number.isNaN(num) && num > max) max = num;
  }
  return `${prefix}_${max + 1}`;
}
