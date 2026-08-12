"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import LoreItemEditor from "../../../../../../components/character/LoreItemEditor";
import {
  CharactersApiError,
  customiseLoreItem,
  listLoreItems,
  logoutCharacter,
  type LoreItemRow,
} from "../../../../../../../lib/characters/api";
import {
  UI_DEV_LORE_CHARACTER_ID,
  uiDevApplyCustomise,
  uiDevLoreItemsResponse,
} from "../../../../../../../lib/characters/loreItemsDev";
import {
  clearSession,
  getSession,
  isSessionValid,
  type CharacterSession,
} from "../../../../../../../lib/characters/session";
import {
  isCharacterUiDev,
  UI_DEV_SESSION_TOKEN,
} from "../../../../../../../lib/characters/uiDev";

function uiDevSession(): CharacterSession {
  return {
    session_token: UI_DEV_SESSION_TOKEN,
    player_uuid: "00000000-0000-4000-8000-ui0000000001",
    expires_at: new Date(Date.now() + 86400000).toISOString(),
    scope: "character",
  };
}

export default function CharacterKitEditPage() {
  const router = useRouter();
  const params = useParams();
  const characterId = String(params?.id || "").trim();
  const kitId = String(params?.kitId || "").trim().toLowerCase() || "starter";
  const kitKey = String(params?.kitKey || "").trim().toLowerCase();
  const uiDev = isCharacterUiDev();

  const [ready, setReady] = useState(false);
  const [session, setSession] = useState<CharacterSession | null>(null);
  const [item, setItem] = useState<LoreItemRow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const [editorKey, setEditorKey] = useState(0);

  const load = useCallback(
    async (token: string) => {
      setError(null);
      setFormError(null);
      try {
        if (uiDev) {
          const data = uiDevLoreItemsResponse(
            characterId || UI_DEV_LORE_CHARACTER_ID
          );
          const match =
            data.items.find((r) => r.kit_key.toLowerCase() === kitKey) ||
            data.items[0] ||
            null;
          setItem(match);
          if (!match) setError("Editable item not found.");
          return;
        }
        const data = await listLoreItems(token, characterId, kitId);
        const match =
          data.items.find((r) => r.kit_key.toLowerCase() === kitKey) || null;
        setItem(match);
        if (!match) setError("Editable item not found or kit not claimable.");
      } catch (err) {
        setError(
          err instanceof CharactersApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Failed to load item"
        );
      }
    },
    [characterId, kitId, kitKey, uiDev]
  );

  useEffect(() => {
    if (!characterId || !kitKey) {
      setReady(true);
      setError("Missing character or item key.");
      return;
    }
    if (uiDev) {
      const s = uiDevSession();
      setSession(s);
      void load(s.session_token).finally(() => setReady(true));
      return;
    }
    const s = getSession();
    if (!s || !isSessionValid(s) || s.scope !== "character") {
      clearSession();
      router.replace("/character");
      return;
    }
    setSession(s);
    void load(s.session_token).finally(() => setReady(true));
  }, [characterId, kitKey, load, router, uiDev]);

  async function onLogout() {
    if (!session || loggingOut) return;
    setLoggingOut(true);
    try {
      if (!uiDev) await logoutCharacter(session.session_token);
    } catch {
      /* clear */
    } finally {
      clearSession();
      router.replace("/character");
    }
  }

  async function onSubmit(input: {
    displayName: string;
    lore: string[];
    existingSkinId?: string | null;
    textureFile?: File | null;
    modelFile?: File | null;
    use3d?: boolean;
    nameColours?: string[];
  }) {
    if (!session || !item) return;
    setSubmitting(true);
    setFormError(null);
    setSuccessMessage(null);
    const uploadedNewSkin = Boolean(input.textureFile);
    const timingLine =
      "It can take up to 5 minutes for a submission to enter the system. You will get a Discord DM once the kit is ready to claim.";
    const successCopy = uploadedNewSkin
      ? `Item submitted. ${timingLine} Your custom skin needs staff approval before the kit is ready.`
      : `Item submitted. ${timingLine}`;
    try {
      if (uiDev) {
        const next = uiDevApplyCustomise(item, input);
        setItem(next);
        setEditorKey((k) => k + 1);
        setSuccessMessage(`${successCopy} (UI-dev)`);
        return;
      }
      const next = await customiseLoreItem(
        session.session_token,
        characterId,
        item.kit_key,
        input,
        kitId
      );
      setItem(next);
      setEditorKey((k) => k + 1);
      setSuccessMessage(successCopy);
    } catch (err) {
      setFormError(
        err instanceof CharactersApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Submit failed"
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!ready) {
    return (
      <p className="mt-8 text-sm text-[var(--tfmc-mist)]">Loading…</p>
    );
  }

  const backHref = `/character/${encodeURIComponent(characterId)}/kits/${encodeURIComponent(kitId)}`;

  return (
    <div className="char-rise">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Link
          href={backHref}
          className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline"
        >
          Back to kit
        </Link>
        <button
          type="button"
          onClick={onLogout}
          disabled={loggingOut || submitting}
          className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline disabled:opacity-50"
        >
          {loggingOut ? "Logging out…" : uiDev ? "Exit" : "Log out"}
        </button>
      </div>

      <h1 className="mb-4 font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)]">
        Edit item
      </h1>

      {error ? (
        <p className="text-sm text-[#e8a0a0]">{error}</p>
      ) : item ? (
        <>
          {successMessage ? (
            <p className="mb-3 whitespace-pre-wrap text-sm text-[var(--tfmc-mist)]">
              {successMessage}
            </p>
          ) : null}
          {formError ? (
            <p className="mb-3 text-sm text-[#e8a0a0]">{formError}</p>
          ) : null}
          <LoreItemEditor
            key={editorKey}
            item={item}
            sessionToken={session?.session_token || UI_DEV_SESSION_TOKEN}
            nameColourStops={uiDev ? 4 : 4}
            submitting={submitting}
            successMessage={null}
            onSubmit={onSubmit}
          />
        </>
      ) : null}
    </div>
  );
}
