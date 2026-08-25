"use client";

import { clearSession } from "@/lib/profile/session";
import { isCharacterUiDev } from "@/lib/characters/uiDev";
import { isSiteDevGateEnabled } from "@/lib/site/config";

export default function BackToGateButton() {
  if (!isSiteDevGateEnabled() || isCharacterUiDev()) {
    return null;
  }

  function returnToGate() {
    clearSession();
    window.location.assign("/");
  }

  return (
    <button
      type="button"
      onClick={returnToGate}
      className="inline-flex min-w-[8.5rem] items-center justify-center rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_35%,transparent)] bg-transparent px-6 py-3 text-sm font-semibold tracking-wide text-[var(--tfmc-cream)] transition-colors hover:border-[var(--tfmc-cream)] hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_8%,transparent)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--tfmc-cream)]"
    >
      Back to gate
    </button>
  );
}
