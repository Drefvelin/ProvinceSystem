"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createSubmission, checkSubmissionConflict, SkinsApiError } from "../../../lib/skins/api";
import { setLastSubmissionId } from "../../../lib/skins/session";
import {
  ARMOR_TIERS,
  baseSetLabel,
  baseSetPickerTitle,
  baseSetsForKind,
  defaultBaseSet,
} from "../../../lib/skins/baseSets";
import {
  assertFileSize,
  expectedSizeForField,
  fileFieldsForKind,
  isBowFrameKind,
  isLargeTextureKind,
  isModel3dKind,
  isGunKind,
  sizeHint,
  ARMOR_BODY_FIELDS,
  type SkinKind,
} from "../../../lib/skins/sizes";
import {
  LEGACY_PALETTE,
  NAME_STYLES,
  normalizePreviewHex,
  previewSpans,
  previewStyleCss,
  type NameStyle,
} from "../../../lib/skins/namePreview";
import FancyCheckbox from "./FancyCheckbox";
import KindPicker from "./KindPicker";

const GRIPS = ["bottom", "middle", "top"] as const;
const MAX_TIERS = ARMOR_TIERS.length;

type Props = {
  sessionToken: string;
};

type TierEntry = {
  tier: string;
  /** Display suffix for this tier (default Iron/Steel/…). */
  alias: string;
  /** When true, helmet is model+texture instead of 16×16 icon. */
  helmet3d: boolean;
  files: Record<string, File | null>;
};

const fieldLabel: Record<string, string> = {
  helmet: "Helmet (16×16)",
  helmet_texture: "Helmet texture (PNG)",
  helmet_model: "Helmet model (JSON)",
  chestplate: "Chestplate (16×16)",
  leggings: "Leggings (16×16)",
  boots: "Boots (16×16)",
  layer_1: "Layer 1 (64×32)",
  layer_2: "Layer 2 (64×32)",
  texture: "Texture (PNG)",
  model: "Model (JSON)",
  carry_model: "Carry model (JSON)",
  reload_model: "Reload model (JSON)",
  aim_model: "Aim model (JSON)",
  pull_0: "Pull 0",
  pull_1: "Pull 1",
  pull_2: "Pull 2",
  charged: "Charged",
};

function namingHint(): string {
  return (
    "File names can be anything; the server renames your PNGs automatically " +
    "from your item name. Sizes still matter (see above)."
  );
}

function slotLabel(kind: SkinKind, field: string): string {
  if (kind === "armor_set") {
    return fieldLabel[field] || field;
  }
  if (isModel3dKind(kind) || isGunKind(kind)) {
    return fieldLabel[field] || field;
  }
  const size = isLargeTextureKind(kind) ? "32×32" : "16×16";
  const base = fieldLabel[field] || field;
  if (isBowFrameKind(kind) || field === "texture") {
    if (field === "texture" && isBowFrameKind(kind)) {
      return `Standby texture (${size})`;
    }
    return `${base} (${size})`;
  }
  return `Texture (${size})`;
}

function acceptForField(field: string): string {
  if (
    field === "model" ||
    field.endsWith("_model") ||
    field === "helmet_model" ||
    field === "carry_model" ||
    field === "reload_model" ||
    field === "aim_model"
  ) {
    return "application/json,.json";
  }
  return "image/png,.png";
}

export default function UploadForm({ sessionToken }: Props) {
  const router = useRouter();
  const [kind, setKind] = useState<SkinKind>("armor_set");
  const [baseSet, setBaseSet] = useState(defaultBaseSet("armor_set"));
  const [tiers, setTiers] = useState<TierEntry[]>([]);
  const [tierToAdd, setTierToAdd] = useState<string>("");
  const [itemName, setItemName] = useState("");
  const [applyName, setApplyName] = useState(true);
  const [colours, setColours] = useState<string[]>(["#ffffff"]);
  const [styles, setStyles] = useState<NameStyle[]>([]);
  const [hexDraft, setHexDraft] = useState("#55ff55");
  const [grip, setGrip] = useState<(typeof GRIPS)[number]>("bottom");
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragFrom, setDragFrom] = useState<number | null>(null);

  useEffect(() => {
    setFiles({});
    setTiers([]);
    setTierToAdd("");
    setError(null);
    setBaseSet(defaultBaseSet(kind));
  }, [kind]);

  const fileFields = fileFieldsForKind(kind);
  const baseOptions = baseSetsForKind(kind);
  const isArmor = kind === "armor_set";

  const remainingTiers: string[] = ARMOR_TIERS.filter(
    (t) => !tiers.some((entry) => entry.tier === t)
  );
  const effectiveTierToAdd = remainingTiers.includes(tierToAdd)
    ? tierToAdd
    : remainingTiers[0] ?? "";

  function setFile(field: string, file: File | null) {
    setFiles((prev) => ({ ...prev, [field]: file }));
  }

  /** Ignore cancel / empty picker so an existing selection is kept. */
  function onPickedFile(
    fileList: FileList | null,
    apply: (file: File) => void
  ) {
    const file = fileList?.[0];
    if (file) apply(file);
  }

  function addTier(tier: string) {
    if (!tier || tiers.some((entry) => entry.tier === tier)) return;
    if (tiers.length >= MAX_TIERS) return;
    setTiers((prev) => [
      ...prev,
      { tier, alias: baseSetLabel(tier), helmet3d: false, files: {} },
    ]);
    setTierToAdd("");
    setError(null);
  }

  function removeTier(tier: string) {
    setTiers((prev) => prev.filter((entry) => entry.tier !== tier));
  }

  function setTierAlias(tier: string, alias: string) {
    setTiers((prev) =>
      prev.map((entry) =>
        entry.tier === tier ? { ...entry, alias } : entry
      )
    );
  }

  function setTierHelmet3d(tier: string, helmet3d: boolean) {
    setTiers((prev) =>
      prev.map((entry) => {
        if (entry.tier !== tier) return entry;
        const files = { ...entry.files };
        if (helmet3d) {
          delete files.helmet;
        } else {
          delete files.helmet_model;
          delete files.helmet_texture;
        }
        return { ...entry, helmet3d, files };
      })
    );
  }

  function setTierFile(tier: string, field: string, file: File | null) {
    setTiers((prev) =>
      prev.map((entry) =>
        entry.tier === tier
          ? { ...entry, files: { ...entry.files, [field]: file } }
          : entry
      )
    );
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const name = itemName.trim();
    if (!name) {
      setError("Item name is required (shown in ArmourShop)");
      return;
    }

    if (!isArmor && (!baseSet || !baseOptions.includes(baseSet))) {
      setError(`Choose a ${baseSetPickerTitle(kind).toLowerCase()}`);
      return;
    }

    if (isArmor && tiers.length < 1) {
      setError("Add at least 1 armor tier");
      return;
    }

    if (kind === "large_handheld" && !grip) {
      setError("Choose a grip preset");
      return;
    }

    const uploadFiles: Record<string, File> = {};

    if (isArmor) {
      try {
        for (const entry of tiers) {
          const tierLabel = baseSetLabel(entry.tier);
          const helmetFields = entry.helmet3d
            ? (["helmet_model", "helmet_texture"] as const)
            : (["helmet"] as const);
          const fields = [...helmetFields, ...ARMOR_BODY_FIELDS];
          for (const field of fields) {
            const file = entry.files[field];
            const label = fieldLabel[field] || field;
            if (!file) {
              throw new Error(`Missing ${label} for the ${tierLabel} tier`);
            }
            const expected = expectedSizeForField(kind, field);
            if (expected) {
              await assertFileSize(file, expected, `${tierLabel} ${label}`);
            }
            uploadFiles[`${entry.tier}_${field}`] = file;
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "File validation failed");
        return;
      }
    } else {
      try {
        for (const field of fileFields) {
          const file = files[field];
          if (!file) {
            throw new Error(`Missing file: ${fieldLabel[field] || field}`);
          }
          const expected = expectedSizeForField(kind, field);
          if (expected) {
            await assertFileSize(file, expected, fieldLabel[field] || field);
          }
          uploadFiles[field] = file;
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "File validation failed");
        return;
      }
    }

    if (colours.length > 0) {
      const normalized = colours
        .map((c) => normalizePreviewHex(c))
        .filter((c): c is string => Boolean(c));
      if (normalized.length !== colours.length) {
        setError("Each colour must be #RRGGBB or a legacy § code");
        return;
      }
    }

    setLoading(true);
    try {
      const check = await checkSubmissionConflict({
        sessionToken,
        display_name: name,
      });
      if (!check.ok) {
        const reasons = new Set(
          check.conflicts.flatMap((c) => c.reasons || [])
        );
        if (reasons.has("display_name")) {
          setError(
            `You already have an active skin named "${name}". Choose a different item name.`
          );
        } else {
          setError(
            "You already have an active skin that conflicts with this one. Choose a different item name."
          );
        }
        setLoading(false);
        return;
      }

      const result = await createSubmission({
        sessionToken,
        kind,
        display_name: name,
        base_set: isArmor ? null : baseSet,
        tiers: isArmor ? tiers.map((entry) => entry.tier) : undefined,
        tier_aliases: isArmor
          ? Object.fromEntries(
              tiers.map((entry) => [
                entry.tier,
                entry.alias.trim() || baseSetLabel(entry.tier),
              ])
            )
          : undefined,
        helmet_3d_tiers: isArmor
          ? tiers.filter((e) => e.helmet3d).map((e) => e.tier)
          : undefined,
        grip_preset: kind === "large_handheld" ? grip : null,
        add_name: applyName,
        name_colours: colours.length ? colours : undefined,
        name_styles: styles.length ? styles : undefined,
        files: uploadFiles,
      });
      setLastSubmissionId(result.id);
      router.push(`/skins/${result.id}`);
    } catch (err) {
      const message =
        err instanceof SkinsApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Upload failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  const inputClass =
    "rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2.5 text-[var(--tfmc-cream)] outline-none placeholder:text-[color-mix(in_srgb,var(--tfmc-mist)_60%,transparent)] focus:border-[var(--tfmc-accent)] disabled:opacity-60";

  const spans = previewSpans(itemName.trim() || "Preview", colours);
  const styleCss = previewStyleCss(styles);

  function addColour(token: string) {
    const hex = normalizePreviewHex(token);
    if (!hex) {
      setError("Invalid colour (use #RRGGBB)");
      return;
    }
    if (colours.length >= 8) {
      setError("At most 8 colours");
      return;
    }
    setError(null);
    setColours((prev) => [...prev, hex]);
  }

  function removeColour(index: number) {
    setColours((prev) => prev.filter((_, i) => i !== index));
  }

  function reorderColour(from: number, to: number) {
    if (from === to || from < 0 || to < 0) return;
    setColours((prev) => {
      if (from >= prev.length || to >= prev.length) return prev;
      const next = [...prev];
      const [item] = next.splice(from, 1);
      next.splice(to, 0, item);
      return next;
    });
  }

  function toggleStyle(style: NameStyle) {
    setStyles((prev) =>
      prev.includes(style) ? prev.filter((s) => s !== style) : [...prev, style]
    );
  }

  return (
    <div className="relative">
      {loading ? (
        <div
          className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-4 rounded-sm bg-[color-mix(in_srgb,var(--tfmc-forest)_92%,transparent)] px-6 py-16"
          role="status"
          aria-live="polite"
        >
          <div
            className="h-10 w-10 animate-spin rounded-full border-2 border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] border-t-[var(--tfmc-accent)]"
            aria-hidden
          />
          <p className="text-lg text-[var(--tfmc-cream)]">Submitting…</p>
          <p className="text-center text-sm text-[var(--tfmc-mist)]">
            Uploading textures. Please wait.
          </p>
        </div>
      ) : null}
    <form onSubmit={onSubmit} className="mt-8 flex w-full flex-col gap-6">
      <KindPicker value={kind} onChange={setKind} disabled={loading} />

      <p className="text-sm text-[var(--tfmc-mist)]">{sizeHint(kind)}</p>
      <p className="text-sm text-[var(--tfmc-mist)]">{namingHint()}</p>

      {!isArmor ? (
        <label className="flex flex-col gap-2 text-left">
          <span className="text-sm font-medium text-[var(--tfmc-stone)]">
            {baseSetPickerTitle(kind)}
          </span>
          <select
            value={baseSet}
            disabled={loading}
            onChange={(e) => setBaseSet(e.target.value)}
            className={inputClass}
            required
          >
            {baseOptions.map((id) => (
              <option key={id} value={id}>
                {baseSetLabel(id)}
              </option>
            ))}
          </select>
        </label>
      ) : null}

      <label className="flex flex-col gap-2 text-left">
        <span className="text-sm font-medium text-[var(--tfmc-stone)]">
          Item name
        </span>
        <span className="text-xs text-[var(--tfmc-mist)]">
          {isArmor
            ? "Base name before the tier label (e.g. Norain becomes Norain Iron). Spaces and capitals are fine."
            : "Shown in ArmourShop. Spaces and capitals are fine."}
        </span>
        <input
          type="text"
          value={itemName}
          disabled={loading}
          onChange={(e) => setItemName(e.target.value)}
          className={inputClass}
          maxLength={80}
          placeholder="Blue Knight"
        />
      </label>

      <label className="flex cursor-pointer items-start gap-2.5 text-sm text-[var(--tfmc-cream)]">
        <FancyCheckbox
          checked={applyName}
          disabled={loading}
          onChange={setApplyName}
        />
        <span>
          Apply name when equipped
          <span className="mt-0.5 block text-xs text-[var(--tfmc-mist)]">
            Keep the item&apos;s existing name on the skinned piece. Separate
            from colours below.
          </span>
        </span>
      </label>

      <fieldset className="flex flex-col gap-4 border-0 p-0">
        <legend className="sr-only">Name colours and styles</legend>

        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-[var(--tfmc-stone)]">
            Colours
          </span>
          <span className="text-xs text-[var(--tfmc-mist)]">
            One colour = solid. Two or more = gradient across the name. Drag
            chips to reorder; × removes.
          </span>
          <div className="flex flex-wrap gap-2">
            {colours.map((c, i) => (
              <div
                key={`${c}-${i}`}
                draggable={!loading}
                onDragStart={() => setDragFrom(i)}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  if (dragFrom !== null) {
                    reorderColour(dragFrom, i);
                  }
                  setDragFrom(null);
                }}
                onDragEnd={() => setDragFrom(null)}
                className={`inline-flex cursor-grab items-center gap-2 rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_20%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_30%,transparent)] px-2 py-1 text-xs text-[var(--tfmc-cream)] active:cursor-grabbing ${
                  dragFrom === i ? "opacity-60 ring-1 ring-[var(--tfmc-accent)]" : ""
                }`}
                title="Drag to reorder"
              >
                <span
                  className="inline-block h-3 w-3 rounded-sm border border-black/40"
                  style={{ backgroundColor: normalizePreviewHex(c) || c }}
                />
                {c}
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => removeColour(i)}
                  title="Remove colour"
                  className="rounded-sm px-1 text-[var(--tfmc-mist)] transition hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)] hover:text-[var(--tfmc-cream)]"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="color"
              value={normalizePreviewHex(hexDraft) || "#55ff55"}
              disabled={loading}
              onChange={(e) => setHexDraft(e.target.value)}
              className="h-9 w-12 cursor-pointer bg-transparent"
            />
            <input
              type="text"
              value={hexDraft}
              disabled={loading}
              onChange={(e) => setHexDraft(e.target.value)}
              className={`${inputClass} max-w-[8rem]`}
              placeholder="#55ff55"
              maxLength={7}
            />
            <button
              type="button"
              disabled={loading}
              onClick={() => addColour(hexDraft)}
              className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[var(--tfmc-moss)] px-3 py-2 text-sm text-[var(--tfmc-cream)] transition hover:brightness-110 hover:border-[var(--tfmc-accent)] active:scale-[0.98] disabled:opacity-60"
            >
              Add colour
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {LEGACY_PALETTE.map((p) => (
              <button
                key={p.code}
                type="button"
                disabled={loading}
                title={`${p.label} (§${p.code})`}
                onClick={() => addColour(p.hex)}
                className="h-5 w-5 rounded-sm border border-black/50 transition hover:scale-125 hover:ring-2 hover:ring-[var(--tfmc-accent)] hover:brightness-110 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--tfmc-accent)] active:scale-110"
                style={{ backgroundColor: p.hex }}
              />
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-[var(--tfmc-stone)]">
            Styles
          </span>
          <div className="flex flex-wrap gap-3">
            {NAME_STYLES.map((s) => (
              <label
                key={s}
                className="flex cursor-pointer items-center gap-2.5 text-sm text-[var(--tfmc-cream)]"
              >
                <FancyCheckbox
                  checked={styles.includes(s)}
                  disabled={loading}
                  onChange={() => toggleStyle(s)}
                  className="mt-0"
                />
                {s}
              </label>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-[var(--tfmc-stone)]">
            Preview
          </span>
          <div
            className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)] bg-[#1a1a1a] px-4 py-3"
            aria-live="polite"
          >
            <p
              className="m-0 text-xl tracking-wide"
              style={{
                ...styleCss,
                fontFamily:
                  'ui-monospace, "Cascadia Mono", "Segoe UI Mono", monospace',
              }}
            >
              {spans.map((span, i) => (
                <span key={i} style={{ color: span.color }}>
                  {span.char === " " ? "\u00a0" : span.char}
                </span>
              ))}
            </p>
          </div>
        </div>
      </fieldset>

      {kind === "large_handheld" ? (
        <fieldset className="flex flex-col gap-2">
          <legend className="text-sm font-medium text-[var(--tfmc-stone)]">
            Grip preset
          </legend>
          <div className="flex flex-wrap gap-3">
            {GRIPS.map((g) => (
              <label
                key={g}
                className="flex cursor-pointer items-center gap-2 text-sm text-[var(--tfmc-cream)]"
              >
                <input
                  type="radio"
                  name="grip"
                  value={g}
                  checked={grip === g}
                  disabled={loading}
                  onChange={() => setGrip(g)}
                  className="accent-[var(--tfmc-accent)]"
                />
                {g}
              </label>
            ))}
          </div>
        </fieldset>
      ) : null}

      {isArmor ? (
        <fieldset className="flex flex-col gap-4 border-0 p-0">
          <legend className="text-sm font-medium text-[var(--tfmc-stone)]">
            Armor tiers
          </legend>
          <p className="text-xs text-[var(--tfmc-mist)]">
            Add 1 to 6 tiers (Iron, Steel, Abyssalite, Mythril, Mage, Infantry).
            Each tier needs chestplate, leggings, boots, and both layers. Helmet
            is a 16×16 icon or a 3D model. Pack name example:{" "}
            <span className="text-[var(--tfmc-cream)]">
              {itemName.trim() || "Name"}{" "}
              {tiers[0]?.alias.trim() ||
                (tiers[0] ? baseSetLabel(tiers[0].tier) : "Iron")}
            </span>{" "}
            Helmet / Chestplate / …. Alias per tier is optional.
          </p>

          {tiers.length > 0 ? (
            <div className="flex flex-col gap-4">
              {tiers.map((entry) => {
                const helmetFields = entry.helmet3d
                  ? (["helmet_model", "helmet_texture"] as const)
                  : (["helmet"] as const);
                const tierFields = [...helmetFields, ...ARMOR_BODY_FIELDS];
                return (
                <div
                  key={entry.tier}
                  className="flex flex-col gap-3 rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)] p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm font-semibold text-[var(--tfmc-cream)]">
                      {baseSetLabel(entry.tier)}
                    </span>
                    <button
                      type="button"
                      disabled={loading}
                      onClick={() => removeTier(entry.tier)}
                      className="text-xs text-[#e8a0a0] hover:underline"
                    >
                      Remove tier
                    </button>
                  </div>
                  <label className="flex flex-col gap-2 text-left">
                    <span className="text-sm font-medium text-[var(--tfmc-stone)]">
                      Tier name alias (optional)
                    </span>
                    <input
                      type="text"
                      value={entry.alias}
                      disabled={loading}
                      maxLength={32}
                      placeholder={baseSetLabel(entry.tier)}
                      onChange={(e) =>
                        setTierAlias(entry.tier, e.target.value)
                      }
                      className={inputClass}
                    />
                    <span className="text-xs text-[var(--tfmc-mist)]">
                      In-game:{" "}
                      {(itemName.trim() || "Name") +
                        " " +
                        (entry.alias.trim() || baseSetLabel(entry.tier))}{" "}
                      Chestplate
                    </span>
                  </label>
                  <label className="flex cursor-pointer items-center gap-2.5 text-sm text-[var(--tfmc-cream)]">
                    <FancyCheckbox
                      checked={entry.helmet3d}
                      disabled={loading}
                      onChange={(checked) =>
                        setTierHelmet3d(entry.tier, checked)
                      }
                      className="mt-0"
                    />
                    3D Helmet
                  </label>
                  <div className="flex flex-col gap-4">
                    {tierFields.map((field) => (
                      <label key={field} className="flex flex-col gap-2 text-left">
                        <span className="text-sm font-medium text-[var(--tfmc-stone)]">
                          {slotLabel(kind, field)}
                        </span>
                        <input
                          type="file"
                          accept={acceptForField(field)}
                          disabled={loading}
                          onChange={(e) =>
                            onPickedFile(e.target.files, (file) =>
                              setTierFile(entry.tier, field, file)
                            )
                          }
                          className="text-sm text-[var(--tfmc-mist)] file:mr-3 file:rounded-sm file:border-0 file:bg-[var(--tfmc-moss)] file:px-3 file:py-1.5 file:text-[var(--tfmc-cream)]"
                        />
                        {entry.files[field] ? (
                          <span className="text-xs text-[var(--tfmc-cream)]">
                            Selected: {entry.files[field]!.name}
                          </span>
                        ) : null}
                      </label>
                    ))}
                  </div>
                </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-[var(--tfmc-mist)]">
              No tiers added yet.
            </p>
          )}

          {remainingTiers.length > 0 ? (
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={effectiveTierToAdd}
                disabled={loading}
                onChange={(e) => setTierToAdd(e.target.value)}
                className={inputClass}
              >
                {remainingTiers.map((t) => (
                  <option key={t} value={t}>
                    {baseSetLabel(t)}
                  </option>
                ))}
              </select>
              <button
                type="button"
                disabled={loading}
                onClick={() => addTier(effectiveTierToAdd)}
                className="rounded-sm bg-[var(--tfmc-moss)] px-3 py-2 text-sm text-[var(--tfmc-cream)]"
              >
                Add tier
              </button>
            </div>
          ) : (
            <p className="text-xs text-[var(--tfmc-mist)]">
              All {MAX_TIERS} tiers added.
            </p>
          )}
        </fieldset>
      ) : (
        <div className="flex flex-col gap-4">
          {fileFields.map((field) => (
            <label key={field} className="flex flex-col gap-2 text-left">
              <span className="text-sm font-medium text-[var(--tfmc-stone)]">
                {slotLabel(kind, field)}
              </span>
              <input
                type="file"
                accept={acceptForField(field)}
                disabled={loading}
                onChange={(e) =>
                  onPickedFile(e.target.files, (file) => setFile(field, file))
                }
                className="text-sm text-[var(--tfmc-mist)] file:mr-3 file:rounded-sm file:border-0 file:bg-[var(--tfmc-moss)] file:px-3 file:py-1.5 file:text-[var(--tfmc-cream)]"
              />
              {files[field] ? (
                <span className="text-xs text-[var(--tfmc-cream)]">
                  Selected: {files[field]!.name}
                </span>
              ) : null}
            </label>
          ))}
        </div>
      )}

      {error ? (
        <p className="text-sm text-[#e8a0a0]" role="alert">
          {error}
        </p>
      ) : null}

      <p className="text-sm text-[var(--tfmc-mist)]">
        After you submit, it can take up to 5 minutes for your request to enter
        the system. You will receive a Discord DM when it does.
      </p>

      <button
        type="submit"
        disabled={loading}
        className="inline-flex items-center justify-center rounded-sm bg-[var(--tfmc-accent)] px-5 py-2.5 text-sm font-semibold text-[var(--tfmc-forest-deep)] transition-opacity hover:opacity-90 disabled:opacity-50"
      >
        {loading ? "Uploading…" : "Submit"}
      </button>
    </form>
    </div>
  );
}
