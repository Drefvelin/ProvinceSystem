"use client";

type Props = {
  value: string;
  min: number;
  max: number;
  onChange: (value: string) => void;
};

export default function AgeStepper({ value, min, max, onChange }: Props) {
  const parsed = Number(value);
  const current = Number.isFinite(parsed) ? parsed : min;

  function setClamped(next: number) {
    const n = Math.max(min, Math.min(max, Math.trunc(next)));
    onChange(String(n));
  }

  function bump(delta: 1 | -1) {
    const base = Number.isFinite(parsed) ? parsed : min;
    setClamped(base + delta);
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
    </div>
  );
}
