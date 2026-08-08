"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createSubmission, SkinsApiError } from "../../../lib/skins/api";
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
  const [grip, setGrip] = useState<(typeof GRIPS)[number]>("bottom");
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFiles({});
    setError(null);
    setBaseSet(defaultBaseSet(kind));
  }, [kind]);

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

    try {
      assertUploadFilenames(kind, files);
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

    setLoading(true);
    try {
      const result = await createSubmission({
        sessionToken,
        kind,
        display_name: name,
        base_set: baseSet,
        grip_preset: kind === "large_handheld" ? grip : null,
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
