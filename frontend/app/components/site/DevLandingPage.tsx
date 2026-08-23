"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import CharacterRedeemForm from "../character/CharacterRedeemForm";
import {
  clearSession,
  type CharacterSession,
} from "@/lib/characters/session";
import { SITE_DISCORD_URL } from "@/lib/site/config";
import { hasSiteStaffAccess } from "@/lib/site/staffAccess";

const STAFF_DENIED_MESSAGE =
  "This site is in development. Staff access only.";

type Props = {
  loading?: boolean;
  accessDenied?: boolean;
  onStaffVerified: () => void;
};

function HubAtmosphere() {
  return (
    <>
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background: `
            radial-gradient(ellipse 80% 60% at 50% 35%, color-mix(in srgb, var(--tfmc-moss) 55%, transparent), transparent 70%),
            radial-gradient(ellipse 100% 80% at 50% 100%, color-mix(in srgb, var(--tfmc-forest) 80%, #000), transparent),
            linear-gradient(165deg, var(--tfmc-forest-deep) 0%, var(--tfmc-forest) 45%, #152820 100%)
          `,
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        }}
      />
    </>
  );
}

export default function DevLandingPage({
  loading = false,
  accessDenied = false,
  onStaffVerified,
}: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const [staffError, setStaffError] = useState<string | null>(
    accessDenied ? STAFF_DENIED_MESSAGE : null
  );
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    if (accessDenied) {
      clearSession();
      setStaffError(STAFF_DENIED_MESSAGE);
    }
  }, [accessDenied]);

  async function handleRedeemed(session: CharacterSession) {
    setStaffError(null);
    setVerifying(true);
    try {
      const staff = await hasSiteStaffAccess(session.session_token);
      if (!staff) {
        clearSession();
        setStaffError(STAFF_DENIED_MESSAGE);
        return;
      }
      onStaffVerified();
      const returnPath = pathname && pathname !== "/" ? pathname : "/";
      router.replace(returnPath);
    } catch {
      clearSession();
      setStaffError(STAFF_DENIED_MESSAGE);
    } finally {
      setVerifying(false);
    }
  }

  const showSpinner = loading || verifying;

  return (
    <main className="relative flex min-h-dvh flex-col items-center justify-center overflow-hidden px-6">
      <HubAtmosphere />

      <div className="relative z-10 flex w-full max-w-md flex-col items-center text-center">
        <h1 className="hub-rise font-[family-name:var(--font-fraunces)] text-6xl font-medium tracking-tight text-[var(--tfmc-cream)] sm:text-7xl">
          TFMC
        </h1>
        <p className="hub-rise-delay mt-4 text-lg text-[var(--tfmc-mist)] sm:text-xl">
          We are in development
        </p>
        <p className="hub-fade-delay mt-2 font-[family-name:var(--font-fraunces)] text-2xl font-medium text-[var(--tfmc-cream)] sm:text-3xl">
          Season 5 Coming Soon
        </p>

        <a
          href={SITE_DISCORD_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="hub-fade-delay mt-8 inline-flex items-center justify-center rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_35%,transparent)] bg-transparent px-6 py-3 text-sm font-semibold tracking-wide text-[var(--tfmc-cream)] transition-colors hover:border-[var(--tfmc-cream)] hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_8%,transparent)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--tfmc-cream)]"
        >
          Join our Discord
        </a>

        <div className="hub-fade-delay mt-10 w-full border-t border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] pt-8">
          <p className="text-xs font-medium uppercase tracking-widest text-[var(--tfmc-stone)]">
            Staff access
          </p>

          {showSpinner ? (
            <p className="mt-4 text-sm text-[var(--tfmc-mist)]">Checking access…</p>
          ) : (
            <>
              <CharacterRedeemForm
                variant="compact"
                onRedeemed={handleRedeemed}
              />
              {staffError ? (
                <p className="mt-3 text-sm text-[#e8a0a0]" role="alert">
                  {staffError}
                </p>
              ) : null}
            </>
          )}
        </div>
      </div>
    </main>
  );
}
