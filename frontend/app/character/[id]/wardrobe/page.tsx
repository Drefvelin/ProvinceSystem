"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  getCreationCatalog,
  logoutCharacter,
  type CreationCatalog,
  type SlotLimits,
} from "../../../../lib/characters/api";
import {
  clearSession,
  getSession,
  isSessionValid,
  type CharacterSession,
} from "../../../../lib/characters/session";
import {
  isCharacterUiDev,
  UI_DEV_SESSION_TOKEN,
} from "../../../../lib/characters/uiDev";
import WardrobeEditor from "../../../components/character/WardrobeEditor";

function uiDevSession(): CharacterSession {
  return {
    session_token: UI_DEV_SESSION_TOKEN,
    player_uuid: "00000000-0000-4000-8000-ui0000000001",
    expires_at: new Date(Date.now() + 86400000).toISOString(),
    scope: "character",
  };
}

export default function CharacterWardrobePage() {
  const router = useRouter();
  const params = useParams();
  const characterId = String(params?.id || "").trim();
  const uiDev = isCharacterUiDev();

  const [ready, setReady] = useState(false);
  const [session, setSession] = useState<CharacterSession | null>(null);
  const [slotLimits, setSlotLimits] = useState<SlotLimits | undefined>();
  const [loggingOut, setLoggingOut] = useState(false);

  const loadCatalog = useCallback(
    async (token: string) => {
      if (uiDev) {
        setSlotLimits({
          defaults: { wardrobe_skin_slots: 1 },
          groups: [
            {
              id: "gilded",
              tier: 2,
              visible: true,
              wardrobe_skin_slots: 2,
              display_name: "Gilded",
            },
            {
              id: "ascended",
              tier: 3,
              visible: true,
              wardrobe_skin_slots: 3,
              display_name: "Ascended",
            },
          ],
        });
        return;
      }
      const catalog = await getCreationCatalog(token).catch(
        () => null as CreationCatalog | null
      );
      setSlotLimits(catalog?.slot_limits);
    },
    [uiDev]
  );

  useEffect(() => {
    if (!characterId) {
      setReady(true);
      return;
    }
    if (uiDev) {
      const s = uiDevSession();
      setSession(s);
      void loadCatalog(s.session_token).finally(() => setReady(true));
      return;
    }
    const s = getSession();
    if (!s || !isSessionValid(s) || s.scope !== "character") {
      router.replace("/character");
      return;
    }
    setSession(s);
    void loadCatalog(s.session_token).finally(() => setReady(true));
  }, [characterId, loadCatalog, router, uiDev]);

  async function onLogout() {
    if (!session || loggingOut) return;
    setLoggingOut(true);
    try {
      if (!uiDev) await logoutCharacter(session.session_token);
    } catch {
      /* still clear local */
    }
    clearSession();
    router.replace("/character");
  }

  if (!ready) {
    return (
      <p className="text-sm text-[var(--tfmc-mist)]">Loading wardrobe…</p>
    );
  }

  if (!characterId || !session) {
    return (
      <p className="text-sm text-red-300" role="alert">
        Missing character id.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link
            href={`/character/${encodeURIComponent(characterId)}`}
            className="text-sm text-[var(--tfmc-mist)] underline-offset-2 hover:underline"
          >
            ← Character
          </Link>
          <h1 className="mt-2 font-[family-name:var(--font-display)] text-3xl text-[var(--tfmc-cream)]">
            Wardrobe
          </h1>
          <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
            Optional skins for this character. Masked applies automatically when
            wearing a mask.
          </p>
        </div>
        <button
          type="button"
          disabled={loggingOut}
          onClick={() => void onLogout()}
          className="text-sm text-[var(--tfmc-mist)] underline-offset-2 hover:underline disabled:opacity-50"
        >
          {loggingOut ? "…" : "Log out"}
        </button>
      </div>

      <WardrobeEditor
        mode="live"
        characterId={characterId}
        sessionToken={session.session_token}
        slotLimits={slotLimits}
        uiDev={uiDev}
      />
    </div>
  );
}
