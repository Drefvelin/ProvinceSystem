"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createSubmission, SkinsApiError } from "../../../lib/skins/api";
import {
  ARMOR_FIELDS,
  assertFileSize,
  expectedSizeForField,
  sizeHint,
  type SkinKind,
} from "../../../lib/skins/sizes";
import { ARMOR_SUFFIXES, assertUploadFilenames } from "../../../lib/skins/slug";
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
  texture: "Texture",
};

function namingHint(kind: SkinKind): string {
  if (kind === "armor_set") {
    return (
      "PNG file names must match: your_id_helmet.png, _chestplate, _leggings, " +
      "_boots, _layer_1, _layer_2 (same your_id on all six). Example: blue_knight_helmet.png"
    );
  }
  return (
    "PNG file name becomes the skin id: use your_id.png " +
    "(lowercase letters, numbers, underscores). Example: blue_knight.png"
  );
}

export default function UploadForm({ sessionToken }: Props) {
  const router = useRouter();
  const [kind, setKind] = useState<SkinKind>("armor_set");
  const [itemName, setItemName] = useState("");
  const [grip, setGrip] = useState<(typeof GRIPS)[number]>("bottom");
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFiles({});
    setError(null);
  }, [kind]);

  const fileFields =
    kind === "armor_set" ? [...ARMOR_FIELDS] : (["texture"] as const);

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
              {kind === "armor_set"
                ? fieldLabel[field]
                : `Texture (${kind === "large_handheld" ? "32×32" : "16×16"})`}
            </span>
            {kind === "armor_set" ? (
              <span className="text-xs text-[var(--tfmc-mist)]">
                Required name: …{ARMOR_SUFFIXES[field]}
              </span>
            ) : (
              <span className="text-xs text-[var(--tfmc-mist)]">
                Required name: your_id.png
              </span>
            )}
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
