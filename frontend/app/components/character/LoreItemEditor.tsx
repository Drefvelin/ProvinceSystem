"use client";

import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import ModelPreview from "../skins/ModelPreview";
import NameColourPicker from "../shared/NameColourPicker";
import {
  authHeaders,
  loreItemDefaultTextureUrl,
  loreItemSkinTextureUrl,
  type LoreItemRow,
} from "../../../lib/characters/api";
import { parseLoreRuns } from "../../../lib/characters/lorePreview";
import {
  DISPLAY_NAME_HINT,
  displayNameError,
  proseError,
} from "../../../lib/textValidation";
import { previewSpans } from "../../../lib/skins/namePreview";
import { ITEM_SIZE, assertFileSize } from "../../../lib/skins/sizes";

const LORE_MAX_LINES = 6;
const LORE_LINE_MAX = 48;
const DISPLAY_NAME_MAX = 80;

const FILE_INPUT_CLASS =
  "text-sm text-[var(--tfmc-mist)] file:mr-3 file:rounded-sm file:border-0 file:bg-[var(--tfmc-moss)] file:px-3 file:py-1.5 file:text-[var(--tfmc-cream)]";

type SkinMode = "upload" | "pick";

type Props = {
  item: LoreItemRow;
  sessionToken: string;
  nameColourStops?: number;
  submitting?: boolean;
  refreshing?: boolean;
  error?: string | null;
  successMessage?: string | null;
  onSubmit: (input: {
    displayName: string;
    lore: string[];
    existingSkinId?: string | null;
    textureFile?: File | null;
    modelFile?: File | null;
    use3d?: boolean;
    nameColours?: string[];
  }) => void | Promise<void>;
  onRefreshStatus?: () => void | Promise<void>;
};

const inputClass =
  "w-full rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_22%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_55%,transparent)] px-3 py-2 text-sm text-[var(--tfmc-cream)] placeholder:text-[var(--tfmc-stone)] focus:border-[var(--tfmc-accent)] focus:outline-none";

function SkinThumb({
  id,
  baseSet,
  token,
}: {
  id: string;
  baseSet: string;
  token: string;
}) {
  const [src, setSrc] = useState<string | null>(null);
  useEffect(() => {
    let dead = false;
    let objectUrl: string | null = null;
    void (async () => {
      try {
        const res = await fetch(loreItemSkinTextureUrl(id, baseSet), {
          headers: authHeaders(token),
        });
        if (!res.ok) return;
        const blob = await res.blob();
        objectUrl = URL.createObjectURL(blob);
        if (!dead) setSrc(objectUrl);
      } catch {
        /* ignore */
      }
    })();
    return () => {
      dead = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [id, baseSet, token]);
  if (!src) {
    return (
      <span className="inline-block h-8 w-8 rounded-sm bg-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)]" />
    );
  }
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt=""
      className="h-8 w-8 image-rendering-pixelated rounded-sm"
      style={{ imageRendering: "pixelated" }}
    />
  );
}

export default function LoreItemEditor({
  item,
  sessionToken,
  nameColourStops = 0,
  submitting = false,
  refreshing = false,
  error = null,
  successMessage = null,
  onSubmit,
  onRefreshStatus,
}: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const modelRef = useRef<HTMLInputElement>(null);
  const [displayName, setDisplayName] = useState(
    item.draft.display_name || ""
  );
  const [colours, setColours] = useState<string[]>(
    Array.isArray(item.draft.name_colours)
      ? [...item.draft.name_colours]
      : []
  );
  const [lore, setLore] = useState<string[]>(
    item.draft.lore.length > 0 ? [...item.draft.lore] : []
  );
  const [loreDraft, setLoreDraft] = useState("");
  const [skinMode, setSkinMode] = useState<SkinMode>(
    item.draft.existing_skin_id ? "pick" : "upload"
  );
  const [textureFile, setTextureFile] = useState<File | null>(null);
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [use3d, setUse3d] = useState(false);
  const [pickedSkinId, setPickedSkinId] = useState<string>(
    item.draft.existing_skin_id || ""
  );
  const [localError, setLocalError] = useState<string | null>(null);
  const [previewTexture, setPreviewTexture] = useState<File | null>(null);

  const isDenied =
    String(item.draft.state || "").toLowerCase() === "denied" ||
    String(item.draft.submission_status || "").toLowerCase() === "denied";
  const denyReason = String(item.draft.deny_reason || "").trim();

  const hasNewSkin =
    (skinMode === "upload" && Boolean(textureFile)) ||
    (skinMode === "pick" && Boolean(pickedSkinId.trim()));
  const submitBlocked = isDenied && !hasNewSkin;

  useEffect(() => {
    let dead = false;
    let objectUrl: string | null = null;

    async function loadPreview() {
      try {
        if (skinMode === "upload" && textureFile) {
          if (!dead) setPreviewTexture(textureFile);
          return;
        }
        let url: string | null = null;
        let filename = "preview.png";
        if (skinMode === "pick" && pickedSkinId.trim()) {
          url = loreItemSkinTextureUrl(pickedSkinId, item.base_set);
          filename = `${pickedSkinId.trim()}.png`;
        } else if (item.skin_png || item.kit_key) {
          url = loreItemDefaultTextureUrl(item.kit_key);
          filename = `${String(item.skin_png || item.kit_key).trim() || "default"}.png`;
        }
        if (!url) {
          if (!dead) setPreviewTexture(null);
          return;
        }
        const res = await fetch(url, { headers: authHeaders(sessionToken) });
        if (!res.ok) {
          if (!dead) setPreviewTexture(null);
          return;
        }
        const blob = await res.blob();
        const file = new File([blob], filename, {
          type: blob.type || "image/png",
        });
        if (!dead) setPreviewTexture(file);
      } catch {
        if (!dead) setPreviewTexture(null);
      }
    }

    void loadPreview();
    return () => {
      dead = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [
    skinMode,
    textureFile,
    pickedSkinId,
    item.kit_key,
    item.skin_png,
    item.base_set,
    sessionToken,
  ]);

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
          allowColourCodes: true,
        })
      : null;

  const previewName = displayName.trim() || item.base_preview.display_name || "Preview";
  const nameSpans = useMemo(
    () => previewSpans(previewName, colours),
    [previewName, colours]
  );
  const previewLore = useMemo(() => {
    const base = item.base_preview.lore || [];
    return [...base, ...lore.map((l) => l.trim()).filter(Boolean)];
  }, [item.base_preview.lore, lore]);

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
    setLore((prev) => [...prev, loreDraftTrimmed]);
    setLoreDraft("");
  }

  function removeLoreLine(index: number) {
    setLore((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLocalError(null);
    if (nameErr) {
      setLocalError(nameErr);
      return;
    }
    if (!displayName.trim()) {
      setLocalError("Display name is required");
      return;
    }
    if (submitBlocked) {
      setLocalError(
        "Skin was denied. Choose a different skin (upload or pick) and submit again."
      );
      return;
    }
    if (skinMode === "upload" && use3d && !modelFile) {
      setLocalError("3D upload requires a model JSON file");
      return;
    }
    await onSubmit({
      displayName: displayName.trim(),
      lore,
      nameColours: colours,
      existingSkinId:
        skinMode === "pick" ? pickedSkinId || null : undefined,
      textureFile: skinMode === "upload" ? textureFile : null,
      modelFile: skinMode === "upload" && use3d ? modelFile : null,
      use3d: skinMode === "upload" && use3d,
    });
  }

  const showError = localError || error;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-10">
      {showError ? (
        <p className="text-sm text-[#e8a0a0]">{showError}</p>
      ) : null}
      {successMessage ? (
        <p className="whitespace-pre-wrap text-sm text-[var(--tfmc-mist)]">
          {successMessage}
        </p>
      ) : null}
      {isDenied ? (
        <p className="rounded-sm border border-[color-mix(in_srgb,#e8a0a0_35%,transparent)] bg-[color-mix(in_srgb,#e8a0a0_10%,transparent)] px-3 py-2 text-sm text-[#e8a0a0]">
          Your custom skin was denied
          {denyReason ? `: ${denyReason}` : "."} Name and lore are kept.
          Choose a different skin and submit again. The kit is not ready to
          claim until a new skin is accepted.
        </p>
      ) : null}

      <section>
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
          Name
        </h2>
        <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
          {DISPLAY_NAME_HINT}. Colour stops use your rank perk.
        </p>
        <input
          type="text"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          maxLength={DISPLAY_NAME_MAX}
          className={`${inputClass} mt-3`}
          autoComplete="off"
        />
        {nameErr ? (
          <p className="mt-2 text-xs text-[#e8a0a0]">{nameErr}</p>
        ) : null}
        <div className="mt-4">
          <NameColourPicker
            colours={colours}
            onChange={setColours}
            previewText={previewName}
            maxStops={nameColourStops}
            lockedMessage="Name colours unlock with your rank perk"
            onError={setLocalError}
          />
        </div>
      </section>

      <section>
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
          Lore
        </h2>
        <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
          Up to {LORE_MAX_LINES} custom lines ({LORE_LINE_MAX} characters each).
          Use §c, &amp;c, or #RRGGBB mid-line. Plain lines get gray (§7) by
          default.
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
                <p className="font-mono text-sm text-[var(--tfmc-cream)]">
                  {line}
                </p>
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
              placeholder="Add a lore line (§c highlight)"
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
          Preview
        </h2>
        <div className="mt-3 rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_18%,transparent)] bg-[#1a1a1a] px-4 py-3 font-mono text-sm">
          <p className="leading-relaxed">
            {nameSpans.map((span, i) => (
              <span key={i} style={{ color: span.color }}>
                {span.char}
              </span>
            ))}
          </p>
          <ul className="mt-2 space-y-1">
            {previewLore.map((line, li) => (
              <li key={`${li}-${line.slice(0, 16)}`}>
                {parseLoreRuns(line).map((run, ri) => (
                  <span
                    key={ri}
                    style={{
                      color: run.color,
                      fontWeight: run.bold ? 700 : undefined,
                      fontStyle: run.italic ? "italic" : undefined,
                      textDecoration: [
                        run.underline ? "underline" : "",
                        run.strike ? "line-through" : "",
                      ]
                        .filter(Boolean)
                        .join(" "),
                    }}
                  >
                    {run.text}
                  </span>
                ))}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section>
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
          Skin
        </h2>
        <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
          Upload a new texture or pick one of your applied knives skins / staff
          i_tools knives. The renderer shows the default Iron Hunting Knife
          until you choose your own. After approval, uploads land in player
          skins for later use in-game.
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
              setModelFile(null);
              setUse3d(false);
              if (fileRef.current) fileRef.current.value = "";
              if (modelRef.current) modelRef.current.value = "";
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
          <div className="mt-4 flex flex-col gap-4">
            <label className="flex items-center gap-2 text-sm text-[var(--tfmc-mist)]">
              <input
                type="checkbox"
                checked={use3d}
                onChange={(e) => {
                  setUse3d(e.target.checked);
                  if (!e.target.checked) {
                    setModelFile(null);
                    if (modelRef.current) modelRef.current.value = "";
                  }
                }}
              />
              3D model (Item 3D template)
            </label>
            <input
              ref={fileRef}
              type="file"
              accept="image/png"
              onChange={(e) => void onPickFile(e.target.files?.[0] ?? null)}
              className={FILE_INPUT_CLASS}
            />
            {textureFile ? (
              <span className="text-xs text-[var(--tfmc-cream)]">
                Selected: {textureFile.name}
              </span>
            ) : null}
            {use3d ? (
              <>
                <input
                  ref={modelRef}
                  type="file"
                  accept="application/json,.json"
                  onChange={(e) => setModelFile(e.target.files?.[0] ?? null)}
                  className={FILE_INPUT_CLASS}
                />
                {modelFile ? (
                  <span className="text-xs text-[var(--tfmc-cream)]">
                    Selected: {modelFile.name}
                  </span>
                ) : null}
              </>
            ) : null}
          </div>
        ) : item.pickable_skins.length === 0 ? (
          <p className="mt-4 text-sm text-[var(--tfmc-mist)]">
            No pickable skins yet. Upload one first.
          </p>
        ) : (
          <ul className="mt-4 flex flex-col gap-2">
            {item.pickable_skins.map((skin) => {
              const selected = pickedSkinId === skin.id;
              return (
                <li key={skin.id}>
                  <button
                    type="button"
                    onClick={() => setPickedSkinId(skin.id)}
                    className={`flex w-full items-center gap-3 rounded-sm border px-3 py-2 text-left text-sm transition-colors ${
                      selected
                        ? "border-[var(--tfmc-accent)] bg-[color-mix(in_srgb,var(--tfmc-cream)_8%,transparent)] text-[var(--tfmc-cream)]"
                        : "border-[color-mix(in_srgb,var(--tfmc-cream)_14%,transparent)] text-[var(--tfmc-mist)] hover:border-[color-mix(in_srgb,var(--tfmc-cream)_28%,transparent)]"
                    }`}
                  >
                    <SkinThumb
                      id={skin.id}
                      baseSet={item.base_set}
                      token={sessionToken}
                    />
                    <span>
                      {skin.display_name || skin.id}
                      {skin.staff ? (
                        <span className="ml-2 text-xs text-[var(--tfmc-stone)]">
                          staff
                        </span>
                      ) : null}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}

        {previewTexture ? (
          <div className="mt-6">
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-[var(--tfmc-stone)]">
              {skinMode === "upload" && textureFile
                ? "Upload preview"
                : skinMode === "pick" && pickedSkinId
                  ? "Selected skin"
                  : "Default skin"}
            </p>
            <ModelPreview
              kind={
                skinMode === "upload" && use3d && modelFile
                  ? "item_3d"
                  : "handheld"
              }
              modelFile={
                skinMode === "upload" && use3d && modelFile ? modelFile : null
              }
              textureFile={previewTexture}
            />
          </div>
        ) : (
          <p className="mt-4 text-sm text-[var(--tfmc-mist)]">
            Default skin preview unavailable.
          </p>
        )}
      </section>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={submitting || submitBlocked}
          className="rounded-sm bg-[var(--tfmc-moss)] px-4 py-2 text-sm text-[var(--tfmc-cream)] disabled:opacity-50"
        >
          {submitting ? "Submitting…" : "Submit item"}
        </button>
        {onRefreshStatus ? (
          <button
            type="button"
            onClick={() => void onRefreshStatus()}
            disabled={refreshing || submitting}
            className="text-sm text-[var(--tfmc-stone)] underline-offset-2 hover:text-[var(--tfmc-cream)] hover:underline disabled:opacity-50"
          >
            {refreshing ? "Refreshing…" : "Refresh status"}
          </button>
        ) : null}
      </div>
    </form>
  );
}
