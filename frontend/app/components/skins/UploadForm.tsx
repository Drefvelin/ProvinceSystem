"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createSubmission, checkSubmissionConflict, SkinsApiError } from "../../../lib/skins/api";
import {
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
  sizeHint,
  type SkinKind,
} from "../../../lib/skins/sizes";
import {
  ARMOR_SUFFIXES,
  BOW_SUFFIXES,
  CROSSBOW_SUFFIXES,
  assertUploadFilenames,
} from "../../../lib/skins/slug";
import {
  LEGACY_PALETTE,
  NAME_STYLES,
  normalizePreviewHex,
  previewSpans,
  previewStyleCss,
  type NameStyle,
} from "../../../lib/skins/namePreview";
import KindPicker from "./KindPicker";

const GRIPS = ["bottom", "middle", "top"] as const;

type Props = {
  sessionToken: string;
};

const fieldLabel: Record<string, string> = {
  helmet: "Helmet (16×16)",
  chestplate: "Chestplate (16×16)",
  leggings: "Leggings (16×16)",
  boots: "Boots (16×16)",
  layer_1: "Layer 1 (64×32)",
  layer_2: "Layer 2 (64×32)",
  texture: "Standby texture",
  pull_0: "Pull 0",
  pull_1: "Pull 1",
  pull_2: "Pull 2",
  charged: "Charged",
};

function namingHint(kind: SkinKind): string {
  if (kind === "armor_set") {
    return (
      "PNG file names must match: your_id_helmet.png, _chestplate, _leggings, " +
      "_boots, _layer_1, _layer_2 (same your_id on all six). Example: blue_knight_helmet.png"
    );
  }
  if (kind === "bow" || kind === "large_bow") {
    return (
      "Four PNGs with the same id: your_id.png, your_id_0.png, your_id_1.png, " +
      "your_id_2.png. Example: blue_shortbow.png + blue_shortbow_0.png …"
    );
  }
  if (kind === "crossbow") {
    return (
      "Five PNGs with the same id: your_id.png, _0, _1, _2, and your_id_charged.png. " +
      "Example: blue_cross.png … blue_cross_charged.png"
    );
  }
  return (
    "PNG file name becomes the skin id: use your_id.png " +
    "(lowercase letters, numbers, underscores). Example: blue_knight.png"
  );
}

function requiredNameHint(kind: SkinKind, field: string): string {
  if (kind === "armor_set") {
    return `Required name: …${ARMOR_SUFFIXES[field]}`;
  }
  if (isBowFrameKind(kind)) {
    const suffixes =
      kind === "crossbow" ? CROSSBOW_SUFFIXES : BOW_SUFFIXES;
    const suffix = suffixes[field];
    if (field === "texture") {
      return "Required name: your_id.png";
    }
    return `Required name: your_id${suffix}`;
  }
  return "Required name: your_id.png";
}

function slotLabel(kind: SkinKind, field: string): string {
  if (kind === "armor_set") {
    return fieldLabel[field] || field;
  }
  const size = isLargeTextureKind(kind) ? "32×32" : "16×16";
  const base = fieldLabel[field] || field;
  if (isBowFrameKind(kind) || field === "texture") {
    return `${base} (${size})`;
  }
  return `Texture (${size})`;
}

export default function UploadForm({ sessionToken }: Props) {
  const router = useRouter();
  const [kind, setKind] = useState<SkinKind>("armor_set");
  const [baseSet, setBaseSet] = useState(defaultBaseSet("armor_set"));
  const [itemName, setItemName] = useState("");
  const [applyName, setApplyName] = useState(false);
  const [colours, setColours] = useState<string[]>(["#ffffff"]);
  const [styles, setStyles] = useState<NameStyle[]>([]);
  const [hexDraft, setHexDraft] = useState("#55ff55");
  const [grip, setGrip] = useState<(typeof GRIPS)[number]>("bottom");
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFiles({});
    setError(null);
    setBaseSet(defaultBaseSet(kind));
  }, [kind]);

  useEffect(() => {
    if (!applyName) {
      setColours(["#ffffff"]);
      setStyles([]);
    }
  }, [applyName]);

  const fileFields = fileFieldsForKind(kind);
  const baseOptions = baseSetsForKind(kind);

  function setFile(field: string, file: File | null) {
    setFiles((prev) => ({ ...prev, [field]: file }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const name = itemName.trim();
    if (!name) {
      setError("Item name is required (shown in ArmourShop)");
      return;
    }

    if (!baseSet || !baseOptions.includes(baseSet)) {
      setError(`Choose a ${baseSetPickerTitle(kind).toLowerCase()}`);
      return;
    }

    if (kind === "large_handheld" && !grip) {
      setError("Choose a grip preset");
      return;
    }

    let baseId: string;
    try {
      baseId = assertUploadFilenames(kind, files);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid file names");
      return;
    }

    const uploadFiles: Record<string, File> = {};
    try {
      for (const field of fileFields) {
        const file = files[field];
        if (!file) {
          throw new Error(`Missing file: ${field}`);
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

    if (applyName) {
      const normalized = colours
        .map((c) => normalizePreviewHex(c))
        .filter((c): c is string => Boolean(c));
      if (colours.length > 0 && normalized.length !== colours.length) {
        setError("Each colour must be #RRGGBB or a legacy § code");
        return;
      }
    }

    setLoading(true);
    try {
      const check = await checkSubmissionConflict({
        sessionToken,
        display_name: name,
        base_id: baseId,
      });
      if (!check.ok) {
        const reasons = new Set(
          check.conflicts.flatMap((c) => c.reasons || [])
        );
        if (reasons.has("display_name") && reasons.has("base_id")) {
          setError(
            "You already have an active skin with this item name and file id. Ask staff to delete it, or change the name/files."
          );
        } else if (reasons.has("display_name")) {
          setError(
            `You already have an active skin named "${name}". Choose a different item name.`
          );
        } else {
          setError(
            `You already have an active skin with file id "${baseId}". Rename your PNG(s).`
          );
        }
        setLoading(false);
        return;
      }

      const result = await createSubmission({
        sessionToken,
        kind,
        display_name: name,
        base_set: baseSet,
        grip_preset: kind === "large_handheld" ? grip : null,
        add_name: applyName,
        name_colours: applyName ? colours : undefined,
        name_styles: applyName ? styles : undefined,
        files: uploadFiles,
      });
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

  const spans = applyName ? previewSpans(itemName.trim() || "Preview", colours) : [];
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

  function toggleStyle(style: NameStyle) {
    setStyles((prev) =>
      prev.includes(style) ? prev.filter((s) => s !== style) : [...prev, style]
    );
  }

  return (
    <form onSubmit={onSubmit} className="mt-8 flex w-full flex-col gap-6">
      <KindPicker value={kind} onChange={setKind} disabled={loading} />

      <p className="text-sm text-[var(--tfmc-mist)]">{sizeHint(kind)}</p>
      <p className="text-sm text-[var(--tfmc-mist)]">{namingHint(kind)}</p>

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

      <label className="flex flex-col gap-2 text-left">
        <span className="text-sm font-medium text-[var(--tfmc-stone)]">
          Item name
        </span>
        <span className="text-xs text-[var(--tfmc-mist)]">
          Shown in ArmourShop. Spaces and capitals are fine.
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

      <label className="flex cursor-pointer items-center gap-2 text-sm text-[var(--tfmc-cream)]">
        <input
          type="checkbox"
          checked={applyName}
          disabled={loading}
          onChange={(e) => setApplyName(e.target.checked)}
          className="accent-[var(--tfmc-accent)]"
        />
        Apply name (colour / style on the item when equipped)
      </label>

      {applyName ? (
        <fieldset className="flex flex-col gap-4 border-0 p-0">
          <legend className="sr-only">Name colours and styles</legend>

          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium text-[var(--tfmc-stone)]">
              Colours
            </span>
            <span className="text-xs text-[var(--tfmc-mist)]">
              One colour = solid. Two or more = gradient across the name.
            </span>
            <div className="flex flex-wrap gap-2">
              {colours.map((c, i) => (
                <button
                  key={`${c}-${i}`}
                  type="button"
                  disabled={loading}
                  onClick={() => removeColour(i)}
                  title="Remove colour"
                  className="inline-flex items-center gap-2 rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_20%,transparent)] px-2 py-1 text-xs text-[var(--tfmc-cream)]"
                >
                  <span
                    className="inline-block h-3 w-3 rounded-sm border border-black/40"
                    style={{ backgroundColor: normalizePreviewHex(c) || c }}
                  />
                  {c}
                  <span aria-hidden>×</span>
                </button>
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
                className="rounded-sm bg-[var(--tfmc-moss)] px-3 py-2 text-sm text-[var(--tfmc-cream)]"
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
                  className="h-5 w-5 rounded-sm border border-black/50"
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
                  className="flex cursor-pointer items-center gap-2 text-sm text-[var(--tfmc-cream)]"
                >
                  <input
                    type="checkbox"
                    checked={styles.includes(s)}
                    disabled={loading}
                    onChange={() => toggleStyle(s)}
                    className="accent-[var(--tfmc-accent)]"
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
      ) : null}

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

      <div className="flex flex-col gap-4">
        {fileFields.map((field) => (
          <label key={field} className="flex flex-col gap-2 text-left">
            <span className="text-sm font-medium text-[var(--tfmc-stone)]">
              {slotLabel(kind, field)}
            </span>
            <span className="text-xs text-[var(--tfmc-mist)]">
              {requiredNameHint(kind, field)}
            </span>
            <input
              type="file"
              accept="image/png,.png"
              disabled={loading}
              onChange={(e) =>
                setFile(field, e.target.files?.[0] ?? null)
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
  );
}
