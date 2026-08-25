"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { UI_DEV_LORE_CHARACTER_ID } from "../../../lib/characters/loreItemsDev";
import { isCharacterUiDev } from "../../../lib/characters/uiDev";

/** Legacy escape hatch: send users to the kits edit flow. */
export default function CharacterLoreItemRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    if (typeof window === "undefined") return;
    const q = new URLSearchParams(window.location.search);
    const characterId =
      q.get("character_id")?.trim() ||
      (isCharacterUiDev() ? UI_DEV_LORE_CHARACTER_ID : "");
    const kitKey = q.get("kit_key")?.trim() || "iron_hunting_knife";
    const kitId = q.get("kit_id")?.trim() || "starter";
    if (!characterId) {
      router.replace("/character");
      return;
    }
    router.replace(
      `/character/${encodeURIComponent(characterId)}/kits/${encodeURIComponent(kitId)}/edit/${encodeURIComponent(kitKey)}`
    );
  }, [router]);

  return (
    <p className="mt-8 text-sm text-[var(--tfmc-mist)]">Redirecting…</p>
  );
}
