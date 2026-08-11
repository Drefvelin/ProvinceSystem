"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  CharactersApiError,
  listCharacterKits,
  logoutCharacter,
  type CharacterKit,
  type CharacterKitItem,
} from "../../../../../lib/characters/api";
import {
  clearSession,
  getSession,
  isSessionValid,
  type CharacterSession,
} from "../../../../../lib/characters/session";
import {
  isCharacterUiDev,
  UI_DEV_SESSION_TOKEN,
} from "../../../../../lib/characters/uiDev";
import { uiDevCharacterKits } from "../../../../../lib/characters/kitsDev";

function uiDevSession(): CharacterSession {
  return {
    session_token: UI_DEV_SESSION_TOKEN,
    player_uuid: "00000000-0000-4000-8000-ui0000000001",
    expires_at: new Date(Date.now() + 86400000).toISOString(),
    scope: "character",
  };
}

function itemLabel(item: CharacterKitItem): string {
  if (item.preview?.display_name) return item.preview.display_name;
  const path = item.path || "";
  const seg = path.includes(".") ? path.slice(path.lastIndexOf(".") + 1) : path;
  return seg.replace(/_/g, " ") || path || "Item";
}

export default function CharacterKitDetailPage() {
  const router = useRouter();
  const params = useParams();
  const characterId = String(params?.id || "").trim();
  const kitId = String(params?.kitId || "").trim().toLowerCase();
  const uiDev = isCharacterUiDev();

  const [ready, setReady] = useState(false);
  const [session, setSession] = useState<CharacterSession | null>(null);
  const [kit, setKit] = useState<CharacterKit | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);

  const load = useCallback(
    async (token: string) => {
      setError(null);
      try {
        const data = uiDev
          ? uiDevCharacterKits(characterId)
          : await listCharacterKits(token, characterId);
        const found =
          data.kits.find((k) => k.id.toLowerCase() === kitId) || null;
        setKit(found);
        if (!found) setError("Kit not found.");
      } catch (err) {
        setError(
          err instanceof CharactersApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Failed to load kit"
        );
      }
    },
    [characterId, kitId, uiDev]
  );

  useEffect(() => {
    if (!characterId || !kitId) {
      setReady(true);
      setError("Missing character or kit id.");
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
  }, [characterId, kitId, load, router, uiDev]);

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

  if (!ready) {
    return (
      <p className="mt-8 text-sm text-[var(--tfmc-mist)]">Loading…</p>
    );
  }

  return (
    <div className="char-rise mt-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Link
          href={`/character/${encodeURIComponent(characterId)}/kits`}
          className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline"
        >
          All kits
        </Link>
        <button
          type="button"
          onClick={onLogout}
          disabled={loggingOut}
          className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline disabled:opacity-50"
        >
          {loggingOut ? "Logging out…" : uiDev ? "Exit" : "Log out"}
        </button>
      </div>

      {error ? (
        <p className="text-sm text-[#e8a0a0]">{error}</p>
      ) : kit ? (
        <>
          <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)]">
            {kit.display_name || kit.id}
          </h1>
          <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
            {kit.claimable
              ? "Claimable in-game with /rpcharacter kit " + kit.id
              : "Claimed"}
            {kit.once_per_character ? " · once per character" : " · repeatable"}
          </p>

          <ul className="mt-8 divide-y divide-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)]">
            {kit.items.map((item) => {
              const canEdit =
                Boolean(item.editable && item.kit_key) && kit.claimable;
              return (
                <li
                  key={`${item.path}-${item.amount}`}
                  className="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <p className="text-[var(--tfmc-cream)]">
                      {itemLabel(item)}
                      <span className="ml-2 text-sm text-[var(--tfmc-stone)]">
                        ×{item.amount}
                      </span>
                    </p>
                    {!item.editable ? (
                      <p className="mt-1 text-xs text-[var(--tfmc-mist)]">
                        Not customisable
                      </p>
                    ) : !kit.claimable ? (
                      <p className="mt-1 text-xs text-[var(--tfmc-mist)]">
                        Claimed · editing closed
                      </p>
                    ) : null}
                  </div>
                  {canEdit ? (
                    <Link
                      href={`/character/${encodeURIComponent(characterId)}/kits/${encodeURIComponent(kit.id)}/edit/${encodeURIComponent(item.kit_key!)}`}
                      className="inline-flex items-center justify-center rounded-sm bg-[var(--tfmc-accent)] px-4 py-2 text-sm font-semibold text-[var(--tfmc-forest-deep)] transition-opacity hover:opacity-90"
                    >
                      Edit
                    </Link>
                  ) : null}
                </li>
              );
            })}
          </ul>
        </>
      ) : null}
    </div>
  );
}
