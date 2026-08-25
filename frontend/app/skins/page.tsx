"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import RedeemForm from "../components/skins/RedeemForm";
import UploadForm from "../components/skins/UploadForm";
import { getPlayerMeta } from "../../lib/skins/api";
import {
  clearSession,
  getLastSubmissionId,
  getSession,
  isSessionValid,
  setSession,
  type SkinsSession,
} from "../../lib/skins/session";
import { formatExpiresIn, formatLocal } from "../../lib/skins/formatTime";

export default function SkinsPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [session, setSessionState] = useState<SkinsSession | null>(null);
  const [metaSynced, setMetaSynced] = useState(true);

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

  useEffect(() => {
    if (!session || !isSessionValid(session)) return;
    let cancelled = false;
    async function refreshMeta() {
      try {
        const meta = await getPlayerMeta(session!.session_token);
        if (cancelled) return;
        const next: SkinsSession = {
          ...session!,
          name_colour_stops: meta.name_colour_stops,
          max_3d_pair_bytes: meta.max_3d_pair_bytes,
          skin_token_cooldown_days: meta.skin_token_cooldown_days,
          skin_kinds: meta.skin_kinds,
          allow_armor_3d_helmet: meta.allow_armor_3d_helmet,
        };
        setSession(next);
        setSessionState(next);
        setMetaSynced(meta.meta_synced !== false);
      } catch {
        // Keep redeem-time session snapshot if refresh fails.
      }
    }
    void refreshMeta();
    return () => {
      cancelled = true;
    };
  }, [session?.session_token]);

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
            skinKinds={session.skin_kinds ?? null}
            allowArmor3dHelmet={session.allow_armor_3d_helmet === true}
            colourLockedMessage={
              !metaSynced && (session.name_colour_stops ?? 0) <= 0
                ? "Join the server once to sync rank perks"
                : undefined
            }
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
