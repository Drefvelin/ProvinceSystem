"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import RedeemForm from "../components/skins/RedeemForm";
import UploadForm from "../components/skins/UploadForm";
import {
  clearSession,
  getLastSubmissionId,
  getSession,
  isSessionValid,
  type SkinsSession,
} from "../../lib/skins/session";
import { formatExpiresIn, formatLocal } from "../../lib/skins/formatTime";

export default function SkinsPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [session, setSessionState] = useState<SkinsSession | null>(null);

  useEffect(() => {
    const existing = getSession();
    if (isSessionValid(existing)) {
      const lastId = getLastSubmissionId();
      if (lastId) {
        router.replace(`/skins/${encodeURIComponent(lastId)}`);
        return;
      }
      setSessionState(existing);
    } else if (existing) {
      clearSession();
    }
    setReady(true);
  }, [router]);

  function onRedeemed(next: SkinsSession) {
    setSessionState(next);
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
            Session expires {formatExpiresIn(session.expires_at)} (
            {formatLocal(session.expires_at)})
            {session.staff ? (
              <span className="ml-2 text-[var(--tfmc-accent)]">· Staff</span>
            ) : null}
          </p>
          <UploadForm
            sessionToken={session.session_token}
            staff={session.staff === true}
            nameColourStops={session.name_colour_stops}
            max3dPairBytes={session.max_3d_pair_bytes}
          />
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
