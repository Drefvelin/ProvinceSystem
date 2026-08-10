"use client";

import { useCallback, useEffect, useState } from "react";
import CharacterList from "../components/character/CharacterList";
import CharacterRedeemForm from "../components/character/CharacterRedeemForm";
import {
  CharactersApiError,
  getCreationCatalog,
  listCharacters,
  logoutCharacter,
  maxAliveSlots,
  type CharacterListItem,
} from "../../lib/characters/api";
import {
  clearSession,
  getSession,
  isSessionValid,
  type CharacterSession,
} from "../../lib/characters/session";
import { formatExpiresIn, formatLocal } from "../../lib/skins/formatTime";

export default function CharacterPage() {
  const [ready, setReady] = useState(false);
  const [session, setSessionState] = useState<CharacterSession | null>(null);
  const [characters, setCharacters] = useState<CharacterListItem[]>([]);
  const [maxSlots, setMaxSlots] = useState(3);
  const [listError, setListError] = useState<string | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);
  const [loadingList, setLoadingList] = useState(false);

  const loadList = useCallback(async (token: string) => {
    setLoadingList(true);
    setListError(null);
    try {
      const [list, catalog] = await Promise.all([
        listCharacters(token),
        getCreationCatalog(token),
      ]);
      setCharacters(list.characters);
      setMaxSlots(maxAliveSlots(catalog.slot_limits));
    } catch (err) {
      if (err instanceof CharactersApiError && err.status === 401) {
        clearSession();
        setSessionState(null);
        setCharacters([]);
        return;
      }
      setListError(
        err instanceof Error ? err.message : "Could not load characters"
      );
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => {
    const existing = getSession();
    if (isSessionValid(existing)) {
      setSessionState(existing);
      void loadList(existing!.session_token);
    } else if (existing) {
      clearSession();
    }
    setReady(true);
  }, [loadList]);

  function onRedeemed(next: CharacterSession) {
    setSessionState(next);
    void loadList(next.session_token);
  }

  async function onLogout() {
    if (!session) return;
    setLoggingOut(true);
    try {
      await logoutCharacter(session.session_token);
    } catch {
      // still clear locally
    } finally {
      clearSession();
      setSessionState(null);
      setCharacters([]);
      setLoggingOut(false);
    }
  }

  if (!ready) {
    return (
      <main className="mx-auto flex min-h-[calc(100dvh-var(--tfmc-header-h))] max-w-lg flex-col justify-center px-6 py-16">
        <p className="text-[var(--tfmc-mist)]">Loading…</p>
      </main>
    );
  }

  const valid = session && isSessionValid(session);
  const aliveCount = characters.filter(
    (c) => String(c.status).toUpperCase() === "ALIVE"
  ).length;

  return (
    <main className="relative mx-auto flex min-h-[calc(100dvh-var(--tfmc-header-h))] max-w-lg flex-col px-6 py-16">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 opacity-80"
        style={{
          background: `
            radial-gradient(ellipse 70% 50% at 50% 0%, color-mix(in srgb, var(--tfmc-moss) 35%, transparent), transparent 65%)
          `,
        }}
      />
      <h1 className="char-rise font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Character
      </h1>

      {valid ? (
        <div className="mt-4">
          <p className="text-sm text-[var(--tfmc-stone)]">
            Session expires {formatExpiresIn(session.expires_at)} (
            {formatLocal(session.expires_at)})
          </p>
          {loadingList ? (
            <p className="mt-8 text-[var(--tfmc-mist)]">Loading characters…</p>
          ) : listError ? (
            <p className="mt-8 text-sm text-[#e8a0a0]" role="alert">
              {listError}
            </p>
          ) : (
            <CharacterList
              characters={characters}
              aliveCount={aliveCount}
              maxSlots={maxSlots}
              onLogout={onLogout}
              loggingOut={loggingOut}
            />
          )}
        </div>
      ) : (
        <>
          <p className="char-rise-delay mt-3 text-[var(--tfmc-mist)]">
            In-game, run{" "}
            <code className="text-[var(--tfmc-cream)]">
              /token create character
            </code>{" "}
            then paste the code here.
          </p>
          <CharacterRedeemForm onRedeemed={onRedeemed} />
        </>
      )}
    </main>
  );
}
