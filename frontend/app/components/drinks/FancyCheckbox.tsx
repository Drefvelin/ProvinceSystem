"use client";

type Props = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  description?: string;
};

export default function FancyCheckbox({
  checked,
  onChange,
  label,
  description,
}: Props) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="flex w-full items-start gap-3 rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_16%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-3 text-left transition hover:border-[color-mix(in_srgb,var(--tfmc-accent)_40%,var(--tfmc-cream))] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--tfmc-accent)]"
    >
      <span
        aria-hidden
        className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-sm border transition ${
          checked
            ? "border-[var(--tfmc-accent)] bg-[var(--tfmc-accent)]"
            : "border-[color-mix(in_srgb,var(--tfmc-cream)_35%,transparent)] bg-transparent"
        }`}
      >
        <svg
          viewBox="0 0 12 12"
          className={`h-3 w-3 text-[var(--tfmc-forest-deep)] transition-opacity ${
            checked ? "opacity-100" : "opacity-0"
          }`}
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M2.5 6.2 4.8 8.5 9.5 3.5" />
        </svg>
      </span>
      <span className="min-w-0">
        <span className="block text-sm font-medium text-[var(--tfmc-cream)]">
          {label}
        </span>
        {description ? (
          <span className="mt-0.5 block text-xs text-[var(--tfmc-mist)]">
            {description}
          </span>
        ) : null}
      </span>
    </button>
  );
}
