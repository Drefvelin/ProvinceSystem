import type { Tone } from "@/lib/precedent/filter";

/** Class strings must be written out literally: Tailwind scans source text, so
 *  an interpolated colour would never make it into the generated CSS.
 *  The amber is for intermediate severity, sitting between the palette's accent
 *  green and the existing #e8a0a0 error red. */
export const toneClass: Record<Tone, string> = {
  positive: "text-[var(--tfmc-accent)]",
  negative: "text-[#e8a0a0]",
  warning: "text-[#d9c48a]",
  neutral: "text-[var(--tfmc-stone)]",
};

/** Rule number: a bordered mono pill, so it is found by shape not by reading. */
export const rulePillClass =
  "inline-flex items-center rounded-sm border border-[color-mix(in_srgb,var(--tfmc-accent)_45%,transparent)] px-1.5 py-0.5 font-mono text-[11px] leading-none text-[var(--tfmc-accent)]";

/** Player names: filled chip, the only field with a background. */
export const playerChipClass =
  "inline-flex items-center rounded-sm bg-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)] px-1.5 py-0.5 text-[11px] leading-none text-[var(--tfmc-cream)]";

export const loggedByClass = "text-[var(--tfmc-stone)]";
export const dateClass = "text-[var(--tfmc-mist)]";
export const idClass = "font-mono text-[10px] text-[color-mix(in_srgb,var(--tfmc-mist)_60%,transparent)]";
