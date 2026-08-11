"use client";

import { useMemo, useRef, useState, type FormEvent } from "react";
import ModelPreview from "../skins/ModelPreview";
import type { LoreItemRow } from "../../../lib/characters/api";
import {
  DISPLAY_NAME_HINT,
  displayNameError,
  proseError,
} from "../../../lib/textValidation";
import { ITEM_SIZE, assertFileSize } from "../../../lib/skins/sizes";

const LORE_MAX_LINES = 6;
const LORE_LINE_MAX = 48;
const DISPLAY_NAME_MAX = 80;

type SkinMode = "upload" | "pick";

type Props = {
  item: LoreItemRow;
  submitting?: boolean;
  refreshing?: boolean;
  error?: string | null;
  successMessage?: string | null;
  onSubmit: (input: {
    displayName: string;
    lore: string[];
    existingSkinId?: string | null;
    textureFile?: File | null;
  }) => void | Promise<void>;
  onRefreshStatus?: () => void | Promise<void>;
};

const inputClass =
  "w-full rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_22%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_55%,transparent)] px-3 py-2 text-sm text-[var(--tfmc-cream)] placeholder:text-[var(--tfmc-stone)] focus:border-[var(--tfmc-accent)] focus:outline-none";

function mergePreview(
  base: LoreItemRow["base_preview"],
  displayName: string,
  lore: string[]
): { display_name: string; lore: string[] } {
  const name = displayName.trim() || base.display_name || "";
  const custom = lore.map((l) => l.trim()).filter(Boolean);
  return {
    display_name: name,
    lore: [...(base.lore || []), ...custom],
  };
}

export default function LoreItemEditor({
  item,
  submitting = false,
  refreshing = false,
  error = null,
  successMessage = null,
  onSubmit,
  onRefreshStatus,
}: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [displayName, setDisplayName] = useState(
    item.draft.display_name || ""
  );
  const [lore, setLore] = useState<string[]>(
    item.draft.lore.length > 0 ? [...item.draft.lore] : []
  );
  const [loreDraft, setLoreDraft] = useState("");
  const [skinMode, setSkinMode] = useState<SkinMode>(
    item.draft.existing_skin_id ? "pick" : "upload"
  );
  const [textureFile, setTextureFile] = useState<File | null>(null);
  const [pickedSkinId, setPickedSkinId] = useState<string>(
    item.draft.existing_skin_id || ""
  );
  const [localError, setLocalError] = useState<string | null>(null);

  const nameErr = displayName
    ? displayNameError(displayName, {
        minLen: 1,
        maxLen: DISPLAY_NAME_MAX,
        field: "display name",
      })
    : null;

  const loreDraftTrimmed = loreDraft.trim();
  const loreDraftErr =
    loreDraftTrimmed.length > 0
      ? proseError(loreDraftTrimmed, {
          minLen: 1,
          maxLen: LORE_LINE_MAX,
          field: "lore line",
        })
      : null;

  const livePreview = useMemo(
    () => mergePreview(item.base_preview, displayName, lore),
    [item.base_preview, displayName, lore]
  );

  const canAddLore =
    lore.length < LORE_MAX_LINES &&
    loreDraftTrimmed.length > 0 &&
    loreDraftErr === null;

  async function onPickFile(file: File | null) {
    setLocalError(null);
    if (!file) {
      setTextureFile(null);
      return;
    }
    try {
      await assertFileSize(file, ITEM_SIZE, "Knife texture");
      setTextureFile(file);
      setSkinMode("upload");
      setPickedSkinId("");
    } catch (err) {
      setTextureFile(null);
      if (fileRef.current) fileRef.current.value = "";
      setLocalError(err instanceof Error ? err.message : "Invalid texture");
    }
  }

  function addLoreLine() {
    if (!canAddLore) return;
    setLore([...lore, loreDraftTrimmed]);
    setLoreDraft("");
  }

  function removeLoreLine(index: number) {
    setLore(lore.filter((_, i) => i !== index));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLocalError(null);
    if (!displayName.trim()) {
      setLocalError("Display name is required");
      return;
    }
    if (nameErr) {
      setLocalError(nameErr);
      return;
    }
    for (let i = 0; i < lore.length; i++) {
      const err = proseError(lore[i], {
        minLen: 1,
        maxLen: LORE_LINE_MAX,
        field: `lore[${i}]`,
      });
      if (err) {
        setLocalError(err);
        return;
      }
    }

    if (skinMode === "upload" && textureFile) {
      await onSubmit({
        displayName: displayName.trim(),
        lore,
        textureFile,
      });
      setTextureFile(null);
      if (fileRef.current) fileRef.current.value = "";
      return;
    }

    if (skinMode === "pick" && pickedSkinId) {
      await onSubmit({
        displayName: displayName.trim(),
        lore,
        existingSkinId: pickedSkinId,
      });
      return;
    }

    await onSubmit({
      displayName: displayName.trim(),
      lore,
    });
  }

  const showError = localError || error;
  const submissionId = item.draft.submission_id;
  const submissionStatus = item.draft.submission_status;

  return (
    <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-10">
      <section>
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
          Preview
        </h2>
        <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
          Name and lore update as you edit. Base item stats stay from the kit
          knife.
        </p>
        <div className="mt-4">
          <p className="font-[family-name:var(--font-fraunces)] text-lg text-[var(--tfmc-cream)]">
            {livePreview.display_name || "Untitled"}
          </p>
          {livePreview.lore.length === 0 ? (
            <p className="mt-2 text-sm text-[var(--tfmc-stone)]">No lore lines.</p>
          ) : (
            <ul className="mt-2 flex flex-col gap-1">
              {livePreview.lore.map((line, i) => (
                <li
                  key={`${i}-${line.slice(0, 16)}`}
                  className="text-sm text-[var(--tfmc-mist)]"
                >
                  {line}
                </li>
              ))}
            </ul>
          )}
        </div>
        {textureFile ? (
          <div className="mt-4">
            <ModelPreview
              kind="handheld"
              textureFile={textureFile}
              flatTextureFile={textureFile}
              className="overflow-hidden rounded-sm"
            />
          </div>
        ) : null}
      </section>

      <section>
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
          Display name
        </h2>
        <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
          Also used as the skin name when you upload a texture. {DISPLAY_NAME_HINT}.
        </p>
        <label className="mt-4 block">
          <span className="sr-only">Display name</span>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            maxLength={DISPLAY_NAME_MAX}
            className={inputClass}
            placeholder={item.base_preview.display_name || "Knife name"}
            autoComplete="off"
          />
        </label>
        {nameErr ? (
          <p className="mt-2 text-xs text-[#e8a0a0]">{nameErr}</p>
        ) : (
          <p className="mt-2 text-xs text-[var(--tfmc-stone)]">
            {displayName.trim().length}/{DISPLAY_NAME_MAX}
          </p>
        )}
      </section>

      <section>
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
          Lore
        </h2>
        <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
          Up to {LORE_MAX_LINES} custom lines ({LORE_LINE_MAX} characters each).
          They appear after the base knife lore.
        </p>
        {lore.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--tfmc-mist)]">No custom lore yet.</p>
        ) : (
          <ul className="mt-3 flex flex-col gap-2">
            {lore.map((line, i) => (
              <li
                key={`${i}-${line.slice(0, 12)}`}
                className="flex items-start justify-between gap-3 border-b border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] py-2"
              >
                <p className="text-sm text-[var(--tfmc-cream)]">{line}</p>
                <button
                  type="button"
                  onClick={() => removeLoreLine(i)}
                  className="shrink-0 text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
        {lore.length < LORE_MAX_LINES ? (
          <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:items-start">
            <input
              type="text"
              value={loreDraft}
              onChange={(e) => setLoreDraft(e.target.value)}
              maxLength={LORE_LINE_MAX}
              className={`${inputClass} sm:flex-1`}
              placeholder="Add a lore line"
              autoComplete="off"
            />
            <button
              type="button"
              onClick={addLoreLine}
              disabled={!canAddLore}
              className="rounded-sm bg-[var(--tfmc-moss)] px-3 py-2 text-sm text-[var(--tfmc-cream)] disabled:opacity-50"
            >
              Add line
            </button>
          </div>
        ) : null}
        {loreDraftErr ? (
          <p className="mt-2 text-xs text-[#e8a0a0]">{loreDraftErr}</p>
        ) : null}
      </section>

      <section>
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
          Skin
        </h2>
        <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
          Upload a new 16×16 texture or pick an applied knives skin. Kind and
          base set are fixed for the hunting knife.
        </p>
        <div className="mt-4 flex flex-wrap gap-4 text-sm">
          <button
            type="button"
            onClick={() => {
              setSkinMode("upload");
              setPickedSkinId("");
            }}
            className={
              skinMode === "upload"
                ? "text-[var(--tfmc-cream)] underline underline-offset-2"
                : "text-[var(--tfmc-stone)] hover:text-[var(--tfmc-cream)]"
            }
          >
            Upload new
          </button>
          <button
            type="button"
            onClick={() => {
              setSkinMode("pick");
              setTextureFile(null);
              if (fileRef.current) fileRef.current.value = "";
            }}
            className={
              skinMode === "pick"
                ? "text-[var(--tfmc-cream)] underline underline-offset-2"
                : "text-[var(--tfmc-stone)] hover:text-[var(--tfmc-cream)]"
            }
          >
            Pick existing
          </button>
        </div>

        {skinMode === "upload" ? (
          <label className="mt-4 block">
            <span className="mb-2 block text-sm text-[var(--tfmc-stone)]">
              Texture PNG (16×16)
            </span>
            <input
              ref={fileRef}
              type="file"
              accept="image/png"
              onChange={(e) => {
                const file = e.target.files?.[0] ?? null;
                void onPickFile(file);
              }}
              className="text-sm text-[var(--tfmc-mist)] file:mr-3 file:rounded-sm file:border-0 file:bg-[var(--tfmc-moss)] file:px-3 file:py-1.5 file:text-[var(--tfmc-cream)]"
            />
            {textureFile ? (
              <p className="mt-2 text-xs text-[var(--tfmc-stone)]">
                Selected: {textureFile.name}
              </p>
            ) : null}
          </label>
        ) : (
          <div className="mt-4">
            {item.pickable_skins.length === 0 ? (
              <p className="text-sm text-[var(--tfmc-mist)]">
                No applied knives skins available yet.
              </p>
            ) : (
              <ul className="flex flex-col gap-2">
                {item.pickable_skins.map((skin) => {
                  const selected = pickedSkinId === skin.id;
                  return (
                    <li key={skin.id}>
                      <button
                        type="button"
                        onClick={() => setPickedSkinId(skin.id)}
                        className={`w-full border-b border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] py-2 text-left text-sm ${
                          selected
                            ? "text-[var(--tfmc-cream)]"
                            : "text-[var(--tfmc-mist)] hover:text-[var(--tfmc-cream)]"
                        }`}
                      >
                        {skin.display_name}
                        {selected ? " (selected)" : ""}
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        )}
      </section>

      {submissionId ? (
        <section>
          <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
            Skin review
          </h2>
          <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
            Submission {submissionId}
            {submissionStatus ? ` · ${submissionStatus}` : ""}
          </p>
          <p className="mt-2 text-sm text-[var(--tfmc-stone)]">
            Discord review does not block saving name and lore. Use Refresh if
            status looks stale.
          </p>
          {onRefreshStatus ? (
            <button
              type="button"
              onClick={() => void onRefreshStatus()}
              disabled={refreshing || submitting}
              className="mt-3 text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline disabled:opacity-50"
            >
              {refreshing ? "Refreshing…" : "Refresh status"}
            </button>
          ) : null}
        </section>
      ) : null}

      {showError ? (
        <p className="text-sm text-[#e8a0a0]" role="alert">
          {showError}
        </p>
      ) : null}
      {successMessage ? (
        <p className="text-sm text-[var(--tfmc-accent)]" role="status">
          {successMessage}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={submitting || Boolean(nameErr)}
        className="inline-flex items-center justify-center rounded-sm bg-[var(--tfmc-accent)] px-5 py-2.5 text-sm font-semibold text-[var(--tfmc-forest-deep)] transition-opacity hover:opacity-90 disabled:opacity-50"
      >
        {submitting ? "Saving…" : "Save customise"}
      </button>
    </form>
  );
}
