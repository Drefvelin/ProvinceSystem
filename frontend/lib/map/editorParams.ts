import type { MapId } from "@/app/components/map/types";
import type { EditorTier } from "@/lib/map/api";

const EDITOR_TIERS: EditorTier[] = ["county", "duchy", "kingdom", "empire"];

function isEditorTier(value: string): value is EditorTier {
  return EDITOR_TIERS.includes(value as EditorTier);
}

export function parseRequiredEditorMapIdParam(value: string | null): MapId | null {
  const normalized = (value || "").trim().toLowerCase();
  if (normalized === "main" || normalized === "dev") {
    return normalized;
  }
  return null;
}

export function parseEditorTierParam(value: string | null): EditorTier {
  const normalized = (value || "").trim().toLowerCase();
  return isEditorTier(normalized) ? normalized : "county";
}
