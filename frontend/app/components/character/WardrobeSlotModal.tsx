"use client";

import { useEffect, useId, useRef, useState } from "react";
import type { ArmModel } from "../../../lib/skins/steveMannequin";
import SkinMannequinPreview from "./SkinMannequinPreview";

type Props = {
  open: boolean;
  slotLabel: string;
  slotId: string;
  filled: boolean;
  canEquip: boolean;
  defaultEquipOnSave: boolean;
  existingTextureSrc: string | null;
  /** Current custom/default name shown in the field */
  initialDisplayName: string;
  /** Placeholder when field empty (defaults to slot default label) */
  namePlaceholder: string;
  saving: boolean;
  error: string | null;
  onClose: () => void;
  onSave: (input: {
    file: File | null;
    equip: boolean;
    displayName: string | null;
  }) => void;
  onClear?: () => void;
};

const SIZE_ERR = "Skin must be exactly 64×64 pixels.";
const NAME_MAX = 24;

function validatePng64(file: File): Promise<string | null> {
  return new Promise((resolve) => {
    if (!file.type.includes("png") && !file.name.toLowerCase().endsWith(".png")) {
      resolve("File must be a PNG.");
      return;
    }
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      if (img.naturalWidth !== 64 || img.naturalHeight !== 64) {
        resolve(SIZE_ERR);
      } else {
        resolve(null);
      }
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve("Could not read PNG.");
    };
    img.src = url;
  });
}

export default function WardrobeSlotModal({
  open,
  slotLabel,
  slotId,
  filled,
  canEquip,
  defaultEquipOnSave,
  existingTextureSrc,
  initialDisplayName,
  namePlaceholder,
  saving,
  error,
  onClose,
  onSave,
  onClear,
}: Props) {
  const titleId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [localErr, setLocalErr] = useState<string | null>(null);
  const [model, setModel] = useState<ArmModel | null>(null);
  const [equipOnSave, setEquipOnSave] = useState(defaultEquipOnSave);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState(initialDisplayName);

  useEffect(() => {
    if (!open) return;
    setFile(null);
    setLocalErr(null);
    setModel(null);
    setEquipOnSave(defaultEquipOnSave);
    setPreviewUrl(null);
    setDisplayName(initialDisplayName);
    const t = window.setTimeout(() => inputRef.current?.focus(), 20);
    return () => window.clearTimeout(t);
  }, [open, defaultEquipOnSave, slotId, initialDisplayName]);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && !saving) {
        e.preventDefault();
        onClose();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, saving, onClose]);

  if (!open) return null;

  const previewSource = previewUrl || existingTextureSrc;
  const trimmedName = displayName.trim();
  const nameChanged =
    trimmedName !== String(initialDisplayName || "").trim();
  const canSave =
    !localErr &&
    !saving &&
    (Boolean(file) || (filled && nameChanged));

  async function onPick(f: File | null) {
    setLocalErr(null);
    setFile(null);
    setModel(null);
    if (!f) return;
    const err = await validatePng64(f);
    if (err) {
      setLocalErr(err);
      return;
    }
    setFile(f);
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-[color-mix(in_srgb,var(--tfmc-forest)_72%,black)]/80 p-4 backdrop-blur-[2px] sm:items-center"
      role="presentation"
      onClick={() => {
        if (!saving) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_22%,transparent)] bg-[var(--tfmc-forest)] p-4 shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id={titleId}
          className="font-[family-name:var(--font-display)] text-xl text-[var(--tfmc-cream)]"
        >
          {slotLabel}
        </h2>
        <p className="mt-1 text-sm text-[var(--tfmc-mist)]">
          Upload a 64×64 PNG. Save signs the skin for in-game use.
        </p>

        <div className="mt-4 flex justify-center">
          <div className="h-56 w-36 overflow-hidden rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)]">
            <SkinMannequinPreview
              source={previewSource}
              className="h-full w-full"
              onModelDetected={setModel}
            />
          </div>
        </div>
        {model ? (
          <p className="mt-2 text-center text-xs text-[var(--tfmc-stone)]">
            Model: {model === "slim" ? "slim" : "classic"}
          </p>
        ) : null}

        <label className="mt-4 flex flex-col gap-1.5 text-sm text-[var(--tfmc-cream)]">
          Name{" "}
          <span className="font-normal text-[var(--tfmc-stone)]">(optional)</span>
          <input
            type="text"
            maxLength={NAME_MAX}
            value={displayName}
            disabled={saving}
            placeholder={namePlaceholder}
            className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_70%,black)] px-3 py-2 text-sm text-[var(--tfmc-cream)] placeholder:text-[var(--tfmc-stone)]"
            onChange={(e) => setDisplayName(e.target.value.slice(0, NAME_MAX))}
          />
        </label>

        <label className="mt-4 flex flex-col gap-1.5 text-sm text-[var(--tfmc-cream)]">
          PNG file
          <input
            ref={inputRef}
            type="file"
            accept="image/png,.png"
            disabled={saving}
            className="text-xs text-[var(--tfmc-mist)] file:mr-3 file:rounded-sm file:border-0 file:bg-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] file:px-3 file:py-1.5 file:text-[var(--tfmc-cream)]"
            onChange={(e) => {
              const f = e.target.files?.[0] ?? null;
              void onPick(f);
              e.target.value = "";
            }}
          />
        </label>

        {canEquip ? (
          <label className="mt-3 flex items-center gap-2 text-sm text-[var(--tfmc-mist)]">
            <input
              type="checkbox"
              checked={equipOnSave}
              disabled={saving || !file}
              onChange={(e) => setEquipOnSave(e.target.checked)}
            />
            Equip on save
          </label>
        ) : null}

        {(localErr || error) && (
          <p className="mt-3 text-sm text-red-300" role="alert">
            {localErr || error}
          </p>
        )}

        <div className="mt-5 flex flex-wrap items-center justify-end gap-2">
          {filled && onClear ? (
            <button
              type="button"
              disabled={saving}
              onClick={onClear}
              className="mr-auto rounded-sm border border-red-900/50 px-3 py-2 text-sm text-red-200 transition-colors hover:bg-red-950/40 disabled:opacity-50"
            >
              Clear
            </button>
          ) : null}
          <button
            type="button"
            disabled={saving}
            onClick={onClose}
            className="rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)] px-3 py-2 text-sm text-[var(--tfmc-mist)] transition-colors hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_6%,transparent)] disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={!canSave}
            onClick={() => {
              if (!canSave) return;
              const name =
                trimmedName.length === 0
                  ? null
                  : trimmedName.slice(0, NAME_MAX);
              onSave({
                file,
                equip: Boolean(file) && canEquip && equipOnSave,
                displayName: name,
              });
            }}
            className="inline-flex min-w-[7rem] items-center justify-center gap-2 rounded-sm bg-[var(--tfmc-accent)] px-3 py-2 text-sm font-medium text-[var(--tfmc-ink)] transition-opacity disabled:opacity-50"
          >
            {saving ? (
              <>
                <span
                  className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-[var(--tfmc-ink)] border-t-transparent"
                  aria-hidden
                />
                {file ? "Signing skin…" : "Saving…"}
              </>
            ) : (
              "Save"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
