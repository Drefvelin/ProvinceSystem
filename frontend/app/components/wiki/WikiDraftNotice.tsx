"use client";

import { usePathname } from "next/navigation";

import { isDraftHref } from "@/app/wiki/data";

/**
 * Renders a "Draft: unverified" banner at the top of any wiki page whose nav
 * item is flagged `draft: true`. The page remains public; the marker stops
 * configuration research from being read as live-tested behaviour.
 */
export default function WikiDraftNotice() {
  const pathname = usePathname();
  if (!pathname || !isDraftHref(pathname)) return null;

  return (
    <div
      role="note"
      className="mb-6 rounded-md border border-[var(--tfmc-accent)] bg-[color-mix(in_srgb,var(--tfmc-accent)_18%,transparent)] px-4 py-3"
    >
      <p className="font-[family-name:var(--font-fraunces)] text-sm uppercase tracking-widest text-[var(--tfmc-cream)]">
        Draft: unverified
      </p>
      <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
        This page was assembled from server configuration but has not been fully checked in game.
        Treat explicitly marked uncertainties as unconfirmed until they are live-tested.
      </p>
    </div>
  );
}
