"use client";

import type { LoreRun } from "../../../lib/characters/lorePreview";
import type { WardrobeSlot } from "../../../lib/characters/api";
import SkinMannequinPreview from "./SkinMannequinPreview";

type Props = {
  slot: WardrobeSlot;
  label: string;
  active: boolean;
  textureSrc: string | null;
  lockRuns?: LoreRun[] | null;
  lockPlain?: string | null;
  onOpen: () => void;
  onEquip?: () => void;
  equipping?: boolean;
};

function FormattedRuns({ runs }: { runs: LoreRun[] }) {
  return (
    <>
      {runs.map((r, i) => (
        <span
          key={`${i}-${r.text.slice(0, 8)}`}
          style={{
            color: r.color,
            fontWeight: r.bold ? 700 : undefined,
            fontStyle: r.italic ? "italic" : undefined,
            textDecoration: [
              r.underline ? "underline" : "",
              r.strike ? "line-through" : "",
            ]
              .filter(Boolean)
              .join(" ") || undefined,
          }}
        >
          {r.text}
        </span>
      ))}
    </>
  );
}

export default function WardrobeSlotFrame({
  slot,
  label,
  active,
  textureSrc,
  lockRuns,
  lockPlain,
  onOpen,
  onEquip,
  equipping,
}: Props) {
  const locked = !slot.unlocked;
  const canOpen = slot.unlocked;
  const showEquip =
    Boolean(onEquip) &&
    slot.unlocked &&
    slot.filled &&
    slot.slot !== "masked" &&
    !active;

  return (
    <div className="flex w-[7.5rem] flex-col gap-2 sm:w-36">
      <button
        type="button"
        disabled={!canOpen}
        onClick={() => {
          if (canOpen) onOpen();
        }}
        className={`relative aspect-[3/5] w-full overflow-hidden rounded-sm border transition-colors ${
          locked
            ? "cursor-not-allowed border-red-900/60"
            : active
              ? "border-[var(--tfmc-accent)] hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_6%,transparent)]"
              : "border-[color-mix(in_srgb,var(--tfmc-cream)_22%,transparent)] hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_6%,transparent)]"
        }`}
        aria-label={
          locked
            ? `${label} locked`
            : `${label}${slot.filled ? "" : " empty"} — edit`
        }
      >
        {slot.filled && textureSrc ? (
          <SkinMannequinPreview
            source={textureSrc}
            className="absolute inset-0 h-full w-full"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-[color-mix(in_srgb,var(--tfmc-forest)_55%,black)]">
            <span className="text-xs text-[var(--tfmc-mist)]">Empty</span>
          </div>
        )}

        {locked ? (
          <div className="absolute inset-0 flex flex-col items-center justify-end bg-[color-mix(in_srgb,#7f1d1d_45%,transparent)] px-1.5 pb-2 pt-8">
            <p className="text-center text-[10px] leading-snug text-[var(--tfmc-cream)]">
              You need{" "}
              {lockRuns && lockRuns.length > 0 ? (
                <FormattedRuns runs={lockRuns} />
              ) : (
                lockPlain || "a higher rank+"
              )}
            </p>
          </div>
        ) : null}

        {active ? (
          <span className="absolute left-1 top-1 rounded-sm bg-[var(--tfmc-accent)] px-1.5 py-0.5 text-[10px] font-medium text-[var(--tfmc-ink)]">
            Active
          </span>
        ) : null}
      </button>

      <div className="flex flex-col gap-1">
        <p className="text-center text-xs text-[var(--tfmc-cream)]">{label}</p>
        {showEquip ? (
          <button
            type="button"
            disabled={equipping}
            onClick={onEquip}
            className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)] px-2 py-1 text-[10px] text-[var(--tfmc-mist)] transition-colors hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_6%,transparent)] disabled:opacity-50"
          >
            {equipping ? "…" : "Equip"}
          </button>
        ) : null}
      </div>
    </div>
  );
}
