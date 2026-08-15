"use client";

import Link from "next/link";

export type MapAccessGateReason = "login" | "permission" | "unknown";

type MapAccessGateProps = {
  reason: MapAccessGateReason;
  mapDisplayName?: string;
};

export default function MapAccessGate({
  reason,
  mapDisplayName = "this map",
}: MapAccessGateProps) {
  const title =
    reason === "login"
      ? "Profile login required"
      : reason === "permission"
        ? "Staff map permission required"
        : "Unable to load map";

  const body =
    reason === "login"
      ? `Sign in with your profile code on the Character page to view ${mapDisplayName}.`
      : reason === "permission"
        ? `Your profile is signed in, but you do not have staff access to ${mapDisplayName}. Ask an operator to grant the tfmc.map.staff LuckPerms node, join lobby or survival once so meta syncs, then try again.`
        : `Something went wrong while loading ${mapDisplayName}. Please try again later.`;

  return (
    <div className="flex min-h-[calc(100dvh-var(--tfmc-header-h))] items-center justify-center bg-[var(--tfmc-forest-deep)] px-6">
      <div className="max-w-lg text-center">
        <h1 className="font-[family-name:var(--font-fraunces)] text-2xl font-medium text-[var(--tfmc-cream)]">
          {title}
        </h1>
        <p className="mt-4 text-sm leading-relaxed text-[var(--tfmc-stone)]">
          {body}
        </p>
        {(reason === "login" || reason === "permission") && (
          <Link
            href="/character"
            className="mt-6 inline-flex rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_20%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-moss)_40%,var(--tfmc-forest-deep))] px-4 py-2 text-sm font-medium text-[var(--tfmc-cream)] transition-colors hover:text-white"
          >
            Go to Character
          </Link>
        )}
      </div>
    </div>
  );
}
