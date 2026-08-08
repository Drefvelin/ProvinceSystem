"use client";

import type { SkinKind } from "../../../lib/skins/sizes";

const OPTIONS: { value: SkinKind; label: string }[] = [
  { value: "armor_set", label: "Armor set" },
  { value: "handheld", label: "Handheld (16×16)" },
  { value: "large_handheld", label: "Large handheld (32×32)" },
  { value: "bow", label: "Bow (16×16, 4 frames)" },
  { value: "large_bow", label: "Large bow (32×32, 4 frames)" },
  { value: "crossbow", label: "Crossbow (16×16, 5 frames)" },
];

type Props = {
  value: SkinKind;
  onChange: (kind: SkinKind) => void;
  disabled?: boolean;
};

export default function KindPicker({ value, onChange, disabled }: Props) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="text-sm font-medium text-[var(--tfmc-stone)]">
        Kind
      </legend>
      <div className="flex flex-col gap-2">
        {OPTIONS.map((opt) => (
          <label
            key={opt.value}
            className="flex cursor-pointer items-center gap-2 text-sm text-[var(--tfmc-cream)]"
          >
            <input
              type="radio"
              name="kind"
              value={opt.value}
              checked={value === opt.value}
              disabled={disabled}
              onChange={() => onChange(opt.value)}
              className="accent-[var(--tfmc-accent)]"
            />
            {opt.label}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
