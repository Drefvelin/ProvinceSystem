"use client";

import { FormEvent, useState } from "react";
import { redeemCode, SkinsApiError } from "../../../lib/skins/api";
import { setSession, type SkinsSession } from "../../../lib/skins/session";
import { isUiDev } from "../../../lib/skins/uiDev";

type Props = {
  onRedeemed: (session: SkinsSession) => void;
};

export default function RedeemForm({ onRedeemed }: Props) {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const uiDev = isUiDev();

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const trimmed = code.trim();
    if (!trimmed) {
      setError("Enter a code");
      return;
    }

    setLoading(true);
    try {
      if (uiDev) {
        const session: SkinsSession = {
          session_token: `ui-dev:${trimmed}`,
          player_uuid: "00000000-0000-4000-8000-000000000000",
          expires_at: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
        };
        setSession(session);
        onRedeemed(session);
        return;
      }

      const result = await redeemCode(trimmed);
      const session = {
        session_token: result.session_token,
        player_uuid: result.player_uuid,
        expires_at: result.expires_at,
      };
      setSession(session);
      onRedeemed(session);
    } catch (err) {
      const message =
        err instanceof SkinsApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Redeem failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="mt-8 flex w-full flex-col gap-4">
      {uiDev ? (
        <p className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-accent)_40%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-accent)_12%,transparent)] px-3 py-2 text-xs text-[var(--tfmc-cream)]">
          UI dev mode: any code unlocks the upload form (no API).
        </p>
      ) : null}
      <label className="flex flex-col gap-2 text-left">
        <span className="text-sm font-medium text-[var(--tfmc-stone)]">
          Upload code
        </span>
        <input
          type="text"
          name="code"
          autoComplete="off"
          spellCheck={false}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          disabled={loading}
          placeholder={uiDev ? "anything" : "e.g. TEST-CODE-1"}
          className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-[var(--tfmc-cream)] outline-none placeholder:text-[color-mix(in_srgb,var(--tfmc-mist)_60%,transparent)] focus:border-[var(--tfmc-accent)] disabled:opacity-60"
        />
      </label>

      {error ? (
        <p className="text-sm text-[#e8a0a0]" role="alert">
          {error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={loading}
        className="inline-flex items-center justify-center rounded-sm bg-[var(--tfmc-accent)] px-5 py-2.5 text-sm font-semibold text-[var(--tfmc-forest-deep)] transition-opacity hover:opacity-90 disabled:opacity-50"
      >
        {loading ? "Redeeming…" : "Redeem"}
      </button>
    </form>
  );
}
