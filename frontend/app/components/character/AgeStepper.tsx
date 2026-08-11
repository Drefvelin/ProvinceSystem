"use client";

import { useEffect, useState } from "react";

type Props = {
  value: string;
  min: number;
  max: number;
  onChange: (value: string) => void;
  /** Current fantasy birthday text shown in the editable field. */
  birthdayValue: string;
  /** Commit edited birthday text; return error message or null. */
  onBirthdayApply: (raw: string) => string | null;
  birthdayHint?: string;
};

export default function AgeStepper({
  value,
  min,
  max,
  onChange,
  birthdayValue,
  onBirthdayApply,
  birthdayHint = "DD/MM/YYYY AE",
}: Props) {
  const parsed = Number(value);
  const current = Number.isFinite(parsed) ? parsed : min;
  const [birthdayDraft, setBirthdayDraft] = useState(birthdayValue);
  const [birthdayError, setBirthdayError] = useState<string | null>(null);

  useEffect(() => {
    setBirthdayDraft(birthdayValue);
    setBirthdayError(null);
  }, [birthdayValue]);

  function setClamped(next: number) {
    const n = Math.max(min, Math.min(max, Math.trunc(next)));
    onChange(String(n));
  }

  function bump(delta: 1 | -1) {
    const base = Number.isFinite(parsed) ? parsed : min;
    setClamped(base + delta);
  }

  function commitBirthday() {
    const err = onBirthdayApply(birthdayDraft);
    setBirthdayError(err);
    if (!err) {
      // parent updates birthdayValue; effect syncs draft
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm text-[var(--tfmc-stone)]">Age</span>
      <div className="flex items-center gap-3">
        <button
          type="button"
          aria-label="Decrease age"
          disabled={current <= min}
          onClick={() => bump(-1)}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_30%,transparent)] text-lg text-[var(--tfmc-cream)] transition-opacity duration-150 disabled:opacity-30"
        >
          −
        </button>
        <input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          value={value}
          onChange={(e) => {
            const raw = e.target.value.replace(/[^\d]/g, "");
            onChange(raw);
          }}
          onBlur={() => {
            if (!value.trim()) {
              onChange(String(min));
              return;
            }
            setClamped(Number(value));
          }}
          className="char-age-input w-full rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-center font-[family-name:var(--font-fraunces)] text-2xl text-[var(--tfmc-cream)] outline-none transition-[border-color] duration-150 focus:border-[var(--tfmc-accent)]"
        />
        <button
          type="button"
          aria-label="Increase age"
          disabled={current >= max}
          onClick={() => bump(1)}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_30%,transparent)] text-lg text-[var(--tfmc-cream)] transition-opacity duration-150 disabled:opacity-30"
        >
          +
        </button>
      </div>

      <label className="mt-1 flex flex-col gap-1.5">
        <span className="text-sm text-[var(--tfmc-stone)]">Birthday</span>
        <div className="flex gap-2">
          <input
            type="text"
            value={birthdayDraft}
            onChange={(e) => {
              setBirthdayDraft(e.target.value);
              setBirthdayError(null);
            }}
            onBlur={commitBirthday}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                commitBirthday();
              }
            }}
            placeholder={birthdayHint}
            className="w-full rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-[var(--tfmc-cream)] outline-none focus:border-[var(--tfmc-accent)]"
          />
          <button
            type="button"
            onClick={commitBirthday}
            className="shrink-0 rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_30%,transparent)] px-3 py-2 text-sm text-[var(--tfmc-cream)] hover:border-[var(--tfmc-accent)]"
          >
            Apply
          </button>
        </div>
        {birthdayError ? (
          <p className="text-xs text-[#e8a0a0]">{birthdayError}</p>
        ) : (
          <p className="text-xs text-[var(--tfmc-stone)]">
            Format {birthdayHint}. Applying updates age.
          </p>
        )}
      </label>
    </div>
  );
}
