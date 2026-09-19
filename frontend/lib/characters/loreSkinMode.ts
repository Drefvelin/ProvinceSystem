import type { LoreItemRow } from "./api";

export type LoreSkinMode = "upload" | "pick";

/** Default skin tab when opening or reloading the kit item editor. */
export function resolveInitialSkinMode(item: LoreItemRow): LoreSkinMode {
  if (item.draft.existing_skin_id) {
    return "pick";
  }
  const state = String(item.draft.state || item.state || "")
    .trim()
    .toLowerCase();
  const submissionId = String(item.draft.submission_id || "").trim();
  if (state === "pending_skin" && submissionId) {
    return "upload";
  }
  if (item.pickable_skins.length > 0) {
    return "pick";
  }
  return "upload";
}

/** Stable key for syncing editor state when server draft reloads. */
export function loreItemDraftSyncKey(item: LoreItemRow): string {
  const d = item.draft;
  return [
    item.kit_key,
    d.existing_skin_id ?? "",
    d.submission_id ?? "",
    String(d.state ?? item.state ?? ""),
    String(item.pickable_skins.length),
  ].join("|");
}
