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
import { assertSlugClient, slugifyDisplayName } from "../../../lib/skins/slug";
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

export default function UploadForm({ sessionToken }: Props) {
  const router = useRouter();
  const [kind, setKind] = useState<SkinKind>("armor_set");
  const [displayName, setDisplayName] = useState("");
  const [slug, setSlug] = useState("");
  const [slugTouched, setSlugTouched] = useState(false);
  const [grip, setGrip] = useState<(typeof GRIPS)[number]>("bottom");
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slugTouched) {
      setSlug(slugifyDisplayName(displayName));
    }
  }, [displayName, slugTouched]);

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

    const name = displayName.trim();
    if (!name) {
      setError("Display name is required");
      return;
    }

    try {
      assertSlugClient(slug.trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid slug");
      return;
    }

    if (kind === "large_handheld" && !grip) {
      setError("Choose a grip preset");
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
        slug: slug.trim(),
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

      <label className="flex flex-col gap-2 text-left">
        <span className="text-sm font-medium text-[var(--tfmc-stone)]">
          Display name
        </span>
        <input
          type="text"
          value={displayName}
          disabled={loading}
          onChange={(e) => setDisplayName(e.target.value)}
          className={inputClass}
          maxLength={80}
        />
      </label>

      <label className="flex flex-col gap-2 text-left">
        <span className="text-sm font-medium text-[var(--tfmc-stone)]">
          Slug
        </span>
        <input
          type="text"
          value={slug}
          disabled={loading}
          spellCheck={false}
          onChange={(e) => {
            setSlugTouched(true);
            setSlug(e.target.value);
          }}
          className={inputClass}
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
            <input
              type="file"
              accept="image/png,.png"
              disabled={loading}
              onChange={(e) =>
                setFile(field, e.target.files?.[0] ?? null)
              }
              className="text-sm text-[var(--tfmc-mist)] file:mr-3 file:rounded-sm file:border-0 file:bg-[var(--tfmc-moss)] file:px-3 file:py-1.5 file:text-[var(--tfmc-cream)]"
            />
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
