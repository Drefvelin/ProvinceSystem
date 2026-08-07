"use client";

import { useEffect, useState } from "react";
import RedeemForm from "../components/skins/RedeemForm";
import UploadForm from "../components/skins/UploadForm";
import {
  clearSession,
  getSession,
  isSessionValid,
  type SkinsSession,
} from "../../lib/skins/session";

export default function SkinsPage() {
  const [ready, setReady] = useState(false);
  const [session, setSessionState] = useState<SkinsSession | null>(null);

  useEffect(() => {
    const existing = getSession();
    if (isSessionValid(existing)) {
      setSessionState(existing);
    } else if (existing) {
      clearSession();
    }
    setReady(true);
  }, []);

  function onRedeemed(next: SkinsSession) {
    setSessionState(next);
  }

  function onClear() {
    clearSession();
    setSessionState(null);
  }

  if (!ready) {
    return (
      <main className="mx-auto flex min-h-[calc(100dvh-var(--tfmc-header-h))] max-w-lg flex-col justify-center px-6 py-16">
        <p className="text-[var(--tfmc-mist)]">Loading…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-[calc(100dvh-var(--tfmc-header-h))] max-w-lg flex-col px-6 py-16">
      <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Skins
      </h1>

      {session && isSessionValid(session) ? (
        <div className="mt-4">
          <p className="text-sm text-[var(--tfmc-stone)]">
            Session expires {session.expires_at}
          </p>
          <button
            type="button"
            onClick={onClear}
            className="mt-2 text-sm text-[var(--tfmc-mist)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline"
          >
            Clear session
          </button>
          <UploadForm sessionToken={session.session_token} />
        </div>
      ) : (
        <>
          <p className="mt-3 text-[var(--tfmc-mist)]">
            Enter the code from in-game to start a skin submission.
          </p>
          <RedeemForm onRedeemed={onRedeemed} />
        </>
      )}
    </main>
  );
}
