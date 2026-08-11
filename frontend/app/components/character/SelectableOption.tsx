"use client";

type Props = {
  title: string;
  selected: boolean;
  onSelect: () => void;
  descriptionLines?: string[];
  /** Shown when cost >= 1 (e.g. trait point cost). */
  cost?: number | null;
  disabled?: boolean;
};

export default function SelectableOption({
  title,
  selected,
  onSelect,
  descriptionLines = [],
  cost = null,
  disabled = false,
}: Props) {
  const showCost = cost != null && Number(cost) >= 1;
  const lines = descriptionLines.filter((l) => String(l || "").trim());

  return (
    <button
      type="button"
      disabled={disabled && !selected}
      onClick={onSelect}
      aria-pressed={selected}
      className={`w-full rounded-sm border px-3 py-3 text-left transition-[border-color,background-color,opacity] duration-200 ${
        selected
          ? "border-[var(--tfmc-accent)] bg-[color-mix(in_srgb,var(--tfmc-accent)_15%,transparent)]"
          : "border-[color-mix(in_srgb,var(--tfmc-cream)_20%,transparent)] hover:border-[color-mix(in_srgb,var(--tfmc-cream)_40%,transparent)]"
      } ${disabled && !selected ? "opacity-40" : ""}`}
    >
      <span className="flex items-baseline justify-between gap-3">
        <span className="font-medium text-[var(--tfmc-cream)]">{title}</span>
        {showCost ? (
          <span className="shrink-0 text-xs text-[var(--tfmc-stone)]">
            {Number(cost)} pt{Number(cost) === 1 ? "" : "s"}
          </span>
        ) : null}
      </span>
      <div
        className={`grid transition-[grid-template-rows,opacity] duration-200 ease-out ${
          selected && lines.length
            ? "grid-rows-[1fr] opacity-100"
            : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          {lines.length ? (
            <div className="mt-2 flex flex-col gap-1.5 border-t border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] pt-2">
              {lines.map((line, i) => (
                <p
                  key={`${title}-desc-${i}`}
                  className="text-sm leading-relaxed text-[var(--tfmc-mist)]"
                >
                  {line}
                </p>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </button>
  );
}
