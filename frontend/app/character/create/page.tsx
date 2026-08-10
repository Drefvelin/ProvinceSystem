"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import CreationWizard from "../../components/character/CreationWizard";
import {
  CharactersApiError,
  getCreationCatalog,
  logoutCharacter,
  type CreationCatalog,
} from "../../../lib/characters/api";
import {
  clearSession,
  getSession,
  isSessionValid,
  type CharacterSession,
} from "../../../lib/characters/session";

export default function CharacterCreatePage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [session, setSession] = useState<CharacterSession | null>(null);
  const [catalog, setCatalog] = useState<CreationCatalog | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    const existing = getSession();
    if (!isSessionValid(existing)) {
      clearSession();
      router.replace("/character");
      return;
    }
    setSession(existing);
    void (async () => {
      try {
        const cat = await getCreationCatalog(existing!.session_token);
        if (!cat.updated_at || !(cat.stages || []).length) {
          setError("Sync issue");
        } else {
          setCatalog(cat);
        }
      } catch (err) {
        if (err instanceof CharactersApiError && err.status === 401) {
          clearSession();
          router.replace("/character");
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load catalog");
      } finally {
        setReady(true);
      }
    })();
  }, [router]);

  async function onLogout() {
    if (!session) return;
    setLoggingOut(true);
    try {
      await logoutCharacter(session.session_token);
    } catch {
      // clear locally anyway
    } finally {
      clearSession();
      router.replace("/character");
    }
  }

  if (!ready) {
    return (
      <main className="mx-auto flex min-h-[calc(100dvh-var(--tfmc-header-h))] max-w-lg flex-col justify-center px-6 py-16">
        <p className="text-[var(--tfmc-mist)]">Loading wizard…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-[calc(100dvh-var(--tfmc-header-h))] max-w-lg flex-col px-6 py-12">
      <div className="flex items-baseline justify-between gap-3">
        <h1 className="char-rise font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)]">
          Create
        </h1>
        <Link
          href="/character"
          className="text-sm text-[var(--tfmc-stone)] hover:text-[var(--tfmc-cream)]"
        >
          Back to list
        </Link>
      </div>

      {error ? (
        <p className="mt-8 text-sm text-[#e8a0a0]" role="alert">
          {error}
        </p>
      ) : catalog && session ? (
        <CreationWizard
          catalog={catalog}
          sessionToken={session.session_token}
          onLogout={() => void onLogout()}
          loggingOut={loggingOut}
        />
      ) : null}
    </main>
  );
}
