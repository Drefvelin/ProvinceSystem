"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  CharactersApiError,
  listCharacters,
  logoutCharacter,
  type CharacterListItem,
} from "../../../lib/characters/api";
import {
  clearSession,
  getSession,
  isSessionValid,
  type CharacterSession,
} from "../../../lib/characters/session";
import {
  isCharacterUiDev,
  UI_DEV_SESSION_TOKEN,
} from "../../../lib/characters/uiDev";
import { UI_DEV_LORE_CHARACTER_ID } from "../../../lib/characters/loreItemsDev";

function uiDevSession(): CharacterSession {
  return {
    session_token: UI_DEV_SESSION_TOKEN,
    player_uuid: "00000000-0000-4000-8000-ui0000000001",
    expires_at: new Date(Date.now() + 86400000).toISOString(),
    scope: "character",
  };
}

export default function CharacterDetailPage() {
  const router = useRouter();
  const params = useParams();
  const characterId = String(params?.id || "").trim();
  const uiDev = isCharacterUiDev();

  const [ready, setReady] = useState(false);
  const [session, setSession] = useState<CharacterSession | null>(null);
  const [character, setCharacter] = useState<CharacterListItem | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);

  const load = useCallback(
    async (token: string) => {
      setError(null);
      if (uiDev) {
        setCharacter({
          id: UI_DEV_LORE_CHARACTER_ID,
          name: "UI Dev Character",
          status: "ALIVE",
          race: "human",
          class: "Warrior",
          kit_status: "eligible",
          kit_statuses: { starter: "eligible" },
          source: "roster",
        });
        return;
      }
      const list = await listCharacters(token);
      const found =
        list.characters.find((c) => c.id === characterId) || null;
      setCharacter(found);
      if (!found) {
        setError("Character not found.");
      }
    },
    [characterId, uiDev]
  );

  useEffect(() => {
    if (!characterId) {
      setReady(true);
      setError("Missing character id.");
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
  }, [characterId, load, router, uiDev]);

  async function onLogout() {
    if (!session || loggingOut) return;
    setLoggingOut(true);
    try {
      if (!uiDev) {
        await logoutCharacter(session.session_token);
      }
    } catch {
      /* still clear local */
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

  const status = String(character?.status || "").toUpperCase();
  const isAlive = status === "ALIVE";
  const meta = [character?.race, character?.class].filter(Boolean).join(" · ");

  return (
    <div className="char-rise mt-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Link
          href="/character"
          className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline"
        >
          Back to characters
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
      ) : character ? (
        <>
          <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)]">
            {character.name || "Unnamed"}
          </h1>
          <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
            {meta || "—"} · {status}
          </p>

          <nav className="mt-10 flex flex-col gap-3">
            {isAlive ? (
              <Link
                href={`/character/${encodeURIComponent(character.id)}/kits`}
                className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)] px-4 py-3 text-[var(--tfmc-cream)] transition-colors hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_6%,transparent)]"
              >
                Kits
              </Link>
            ) : (
              <p className="text-sm text-[var(--tfmc-mist)]">
                Kits are available for alive characters.
              </p>
            )}
          </nav>
        </>
      ) : null}
    </div>
  );
}
