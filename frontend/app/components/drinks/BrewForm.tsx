"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  createSubmission,
  getCatalog,
  getTextures,
  DrinksApiError,
  type DrinkCatalog,
  type DrinkIngredient,
  type DrinkTexture,
} from "../../../lib/drinks/api";
import {
  COMMON_EFFECTS,
  EXPECTED_PNG_SIZE,
  MAX_PNG_BYTES,
  WOOD_OPTIONS,
} from "../../../lib/drinks/constants";
import {
  setLastSubmissionId,
  type DrinksSession,
} from "../../../lib/drinks/session";

type IngredientRow = { id: string; amount: number };
type EffectRow = { type: string; level: number; duration: number };
type AppearanceMode = "color" | "upload" | "reuse";

type Props = {
  session: DrinksSession;
};

const fieldClass =
  "rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_40%,transparent)] px-3 py-2 text-[var(--tfmc-cream)] outline-none focus:border-[var(--tfmc-accent)] disabled:opacity-60";

export default function BrewForm({ session }: Props) {
  const router = useRouter();
  const allowTexture = session.allow_drink_texture === true;

  const [catalog, setCatalog] = useState<DrinkCatalog | null>(null);
  const [textures, setTextures] = useState<DrinkTexture[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loadingCatalog, setLoadingCatalog] = useState(true);

  const [name, setName] = useState("");
  const [nameBad, setNameBad] = useState("");
  const [nameGood, setNameGood] = useState("");
  const [ingredients, setIngredients] = useState<IngredientRow[]>([
    { id: "", amount: 1 },
  ]);
  const [cookingTime, setCookingTime] = useState(5);
  const [distillRuns, setDistillRuns] = useState(0);
  const [distillTime, setDistillTime] = useState(40);
  const [wood, setWood] = useState("oak");
  const [age, setAge] = useState(0);
  const [difficulty, setDifficulty] = useState(3);
  const [alcohol, setAlcohol] = useState(0);
  const [loreText, setLoreText] = useState("");
  const [drinkMessage, setDrinkMessage] = useState("");
  const [drinkTitle, setDrinkTitle] = useState("");
  const [glint, setGlint] = useState(false);
  const [effects, setEffects] = useState<EffectRow[]>([]);
  const [appearance, setAppearance] = useState<AppearanceMode>("color");
  const [color, setColor] = useState("#C45A12");
  const [textureFile, setTextureFile] = useState<File | null>(null);
  const [existingTextureId, setExistingTextureId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoadingCatalog(true);
      setLoadError(null);
      try {
        const cat = await getCatalog();
        if (cancelled) return;
        setCatalog(cat);
        if (allowTexture) {
          const tex = await getTextures(session.session_token);
          if (!cancelled) setTextures(tex);
        }
      } catch (err) {
        if (cancelled) return;
        setLoadError(
          err instanceof DrinksApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Failed to load catalog"
        );
      } finally {
        if (!cancelled) setLoadingCatalog(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [allowTexture, session.session_token]);

  const byCategory = useMemo(() => {
    const map = new Map<string, DrinkIngredient[]>();
    for (const item of catalog?.ingredients || []) {
      const cat = (item.category || "other").trim() || "other";
      const list = map.get(cat) || [];
      list.push(item);
      map.set(cat, list);
    }
    return [...map.entries()].sort(([a], [b]) => a.localeCompare(b));
  }, [catalog]);

  const effectChoices = useMemo(() => {
    const blacklist = new Set(
      (catalog?.effects_blacklist || []).map((e) => e.toLowerCase())
    );
    return COMMON_EFFECTS.filter((e) => !blacklist.has(e));
  }, [catalog]);

  function validateClient(): string | null {
    if (!name.trim()) return "Enter a drink name";
    if (!catalog || catalog.ingredients.length === 0) {
      return "Ingredient catalog is empty. Ask staff to sync DrinkBuilder.";
    }
    const rows = ingredients.filter((r) => r.id.trim());
    if (rows.length === 0) return "Add at least one ingredient";
    for (const row of rows) {
      if (!Number.isFinite(row.amount) || row.amount < 1) {
        return "Ingredient amounts must be at least 1";
      }
    }
    if (appearance === "color") {
      if (!/^#[0-9A-Fa-f]{6}$/.test(color.trim())) {
        return "Color must be #RRGGBB";
      }
    } else if (!allowTexture) {
      return "Your rank cannot use custom textures";
    } else if (appearance === "upload") {
      if (!textureFile) return "Choose a PNG texture";
      if (textureFile.size > MAX_PNG_BYTES) {
        return `PNG must be under ${MAX_PNG_BYTES} bytes`;
      }
      if (!textureFile.name.toLowerCase().endsWith(".png")) {
        return "Texture must be a PNG";
      }
    } else if (appearance === "reuse") {
      if (!existingTextureId.trim()) return "Pick an existing texture";
    }
    return null;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const clientError = validateClient();
    if (clientError) {
      setError(clientError);
      return;
    }
    if (!catalog) return;

    const names =
      nameBad.trim() || nameGood.trim()
        ? [
            nameBad.trim() || name.trim(),
            name.trim(),
            nameGood.trim() || name.trim(),
          ]
        : undefined;

    const recipe = {
      name: name.trim(),
      ...(names ? { names } : {}),
      ingredients: ingredients
        .filter((r) => r.id.trim())
        .map((r) => ({ id: r.id.trim(), amount: Math.floor(r.amount) })),
      cooking_time: Math.max(0, Math.floor(cookingTime)),
      distill_runs: Math.max(0, Math.floor(distillRuns)),
      distill_time: Math.max(0, Math.floor(distillTime)),
      wood: wood || null,
      age: Math.max(0, Math.floor(age)),
      difficulty: Math.min(10, Math.max(1, Math.floor(difficulty))),
      alcohol: Math.min(100, Math.max(0, Math.floor(alcohol))),
      effects: effects
        .filter((ef) => ef.type.trim())
        .map((ef) => ({
          type: ef.type.trim().toLowerCase(),
          level: Math.max(1, Math.floor(ef.level || 1)),
          duration: Math.max(1, Math.floor(ef.duration || 1)),
        })),
      lore: loreText
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean),
      drink_message: drinkMessage.trim() || null,
      drink_title: drinkTitle.trim() || null,
      glint,
      color: appearance === "color" ? color.trim() : null,
    };

    setSubmitting(true);
    try {
      if (appearance === "upload" && textureFile) {
        const dimsOk = await checkPngSize(textureFile);
        if (!dimsOk) {
          setError(
            `Texture should be ${EXPECTED_PNG_SIZE}×${EXPECTED_PNG_SIZE} PNG (potion icon).`
          );
          setSubmitting(false);
          return;
        }
      }
      const result = await createSubmission({
        sessionToken: session.session_token,
        recipe,
        texture: appearance === "upload" ? textureFile : null,
        existingTextureId:
          appearance === "reuse" ? existingTextureId.trim() : null,
      });
      setLastSubmissionId(result.id);
      router.push(`/drinks/${encodeURIComponent(result.id)}`);
    } catch (err) {
      setError(
        err instanceof DrinksApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Submit failed"
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (loadingCatalog) {
    return <p className="mt-8 text-[var(--tfmc-mist)]">Loading catalog…</p>;
  }

  if (loadError) {
    return (
      <p className="mt-8 text-sm text-[#e8a0a0]" role="alert">
        {loadError}
      </p>
    );
  }

  if (!catalog || catalog.ingredients.length === 0) {
    return (
      <div className="mt-8 space-y-3">
        <p className="text-[var(--tfmc-cream)]">
          Ingredient catalog is empty.
        </p>
        <p className="text-sm text-[var(--tfmc-mist)]">
          Staff need to run{" "}
          <code className="text-[var(--tfmc-accent)]">
            /drinkbuilder catalog sync
          </code>{" "}
          on the server before drinks can be submitted.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="mt-8 flex w-full flex-col gap-8">
      <section className="space-y-3">
        <h2 className="text-sm font-medium text-[var(--tfmc-stone)]">Names</h2>
        <label className="flex flex-col gap-1.5">
          <span className="text-xs text-[var(--tfmc-mist)]">
            Drink name (normal quality)
          </span>
          <input
            className={fieldClass}
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={48}
            required
          />
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="flex flex-col gap-1.5">
            <span className="text-xs text-[var(--tfmc-mist)]">
              Bad quality name (optional)
            </span>
            <input
              className={fieldClass}
              value={nameBad}
              onChange={(e) => setNameBad(e.target.value)}
              maxLength={48}
            />
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-xs text-[var(--tfmc-mist)]">
              Good quality name (optional)
            </span>
            <input
              className={fieldClass}
              value={nameGood}
              onChange={(e) => setNameGood(e.target.value)}
              maxLength={48}
            />
          </label>
        </div>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-[var(--tfmc-stone)]">
            Ingredients
          </h2>
          <button
            type="button"
            className="text-xs text-[var(--tfmc-accent)] hover:underline"
            onClick={() =>
              setIngredients((rows) => [...rows, { id: "", amount: 1 }])
            }
          >
            Add
          </button>
        </div>
        {ingredients.map((row, idx) => (
          <div key={idx} className="flex flex-wrap gap-2">
            <select
              className={`${fieldClass} min-w-[12rem] flex-1`}
              value={row.id}
              onChange={(e) => {
                const id = e.target.value;
                setIngredients((rows) =>
                  rows.map((r, i) => (i === idx ? { ...r, id } : r))
                );
              }}
            >
              <option value="">Select…</option>
              {byCategory.map(([cat, items]) => (
                <optgroup key={cat} label={cat}>
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.label || item.id}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
            <input
              type="number"
              min={1}
              className={`${fieldClass} w-20`}
              value={row.amount}
              onChange={(e) => {
                const amount = Number(e.target.value);
                setIngredients((rows) =>
                  rows.map((r, i) => (i === idx ? { ...r, amount } : r))
                );
              }}
            />
            {ingredients.length > 1 ? (
              <button
                type="button"
                className="text-xs text-[#e8a0a0]"
                onClick={() =>
                  setIngredients((rows) => rows.filter((_, i) => i !== idx))
                }
              >
                Remove
              </button>
            ) : null}
          </div>
        ))}
      </section>

      <section className="grid gap-3 sm:grid-cols-2">
        <h2 className="text-sm font-medium text-[var(--tfmc-stone)] sm:col-span-2">
          Brew settings
        </h2>
        <NumberField
          label="Cooking time (minutes)"
          value={cookingTime}
          onChange={setCookingTime}
          min={0}
        />
        <NumberField
          label="Distill runs"
          value={distillRuns}
          onChange={setDistillRuns}
          min={0}
        />
        <NumberField
          label="Distill time (seconds)"
          value={distillTime}
          onChange={setDistillTime}
          min={0}
        />
        <NumberField label="Age (years)" value={age} onChange={setAge} min={0} />
        <NumberField
          label="Difficulty (1–10)"
          value={difficulty}
          onChange={setDifficulty}
          min={1}
          max={10}
        />
        <NumberField
          label="Alcohol (0–100)"
          value={alcohol}
          onChange={setAlcohol}
          min={0}
          max={100}
        />
        <label className="flex flex-col gap-1.5 sm:col-span-2">
          <span className="text-xs text-[var(--tfmc-mist)]">Barrel wood</span>
          <select
            className={fieldClass}
            value={wood}
            onChange={(e) => setWood(e.target.value)}
          >
            {WOOD_OPTIONS.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-[var(--tfmc-stone)]">
            Effects
          </h2>
          <button
            type="button"
            className="text-xs text-[var(--tfmc-accent)] hover:underline"
            onClick={() =>
              setEffects((rows) => [
                ...rows,
                { type: effectChoices[0] || "nausea", level: 1, duration: 20 },
              ])
            }
            disabled={effectChoices.length === 0}
          >
            Add
          </button>
        </div>
        {effects.length === 0 ? (
          <p className="text-xs text-[var(--tfmc-mist)]">No effects (optional).</p>
        ) : (
          effects.map((ef, idx) => (
            <div key={idx} className="flex flex-wrap gap-2">
              <select
                className={`${fieldClass} min-w-[10rem] flex-1`}
                value={ef.type}
                onChange={(e) => {
                  const type = e.target.value;
                  setEffects((rows) =>
                    rows.map((r, i) => (i === idx ? { ...r, type } : r))
                  );
                }}
              >
                {effectChoices.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))}
              </select>
              <input
                type="number"
                min={1}
                className={`${fieldClass} w-16`}
                value={ef.level}
                onChange={(e) => {
                  const level = Number(e.target.value);
                  setEffects((rows) =>
                    rows.map((r, i) => (i === idx ? { ...r, level } : r))
                  );
                }}
                title="Level"
              />
              <input
                type="number"
                min={1}
                className={`${fieldClass} w-20`}
                value={ef.duration}
                onChange={(e) => {
                  const duration = Number(e.target.value);
                  setEffects((rows) =>
                    rows.map((r, i) => (i === idx ? { ...r, duration } : r))
                  );
                }}
                title="Duration (seconds)"
              />
              <button
                type="button"
                className="text-xs text-[#e8a0a0]"
                onClick={() =>
                  setEffects((rows) => rows.filter((_, i) => i !== idx))
                }
              >
                Remove
              </button>
            </div>
          ))
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-medium text-[var(--tfmc-stone)]">
          Appearance
        </h2>
        <div className="flex flex-wrap gap-3 text-sm text-[var(--tfmc-cream)]">
          <label className="inline-flex items-center gap-2">
            <input
              type="radio"
              name="appearance"
              checked={appearance === "color"}
              onChange={() => setAppearance("color")}
            />
            Potion color
          </label>
          {allowTexture ? (
            <>
              <label className="inline-flex items-center gap-2">
                <input
                  type="radio"
                  name="appearance"
                  checked={appearance === "upload"}
                  onChange={() => setAppearance("upload")}
                />
                Upload PNG
              </label>
              <label className="inline-flex items-center gap-2">
                <input
                  type="radio"
                  name="appearance"
                  checked={appearance === "reuse"}
                  onChange={() => setAppearance("reuse")}
                  disabled={textures.length === 0}
                />
                Reuse texture
              </label>
              {textures.length === 0 ? (
                <p className="basis-full text-xs text-[var(--tfmc-mist)]">
                  No applied textures yet. Upload one first (or wait for pack
                  apply).
                </p>
              ) : null}
            </>
          ) : (
            <p className="text-xs text-[var(--tfmc-mist)]">
              Your rank is color-only (no custom texture).
            </p>
          )}
        </div>
        {appearance === "color" ? (
          <label className="flex flex-col gap-1.5">
            <span className="text-xs text-[var(--tfmc-mist)]">#RRGGBB</span>
            <div className="flex gap-2">
              <input
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="h-10 w-14 cursor-pointer rounded-sm border border-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] bg-transparent"
              />
              <input
                className={`${fieldClass} flex-1`}
                value={color}
                onChange={(e) => setColor(e.target.value)}
                maxLength={7}
              />
            </div>
          </label>
        ) : null}
        {appearance === "upload" ? (
          <label className="flex flex-col gap-1.5">
            <span className="text-xs text-[var(--tfmc-mist)]">
              {EXPECTED_PNG_SIZE}×{EXPECTED_PNG_SIZE} PNG potion icon (max{" "}
              {Math.floor(MAX_PNG_BYTES / 1024)} KB)
            </span>
            <input
              type="file"
              accept="image/png,.png"
              onChange={(e) => setTextureFile(e.target.files?.[0] || null)}
              className="text-sm text-[var(--tfmc-cream)]"
            />
          </label>
        ) : null}
        {appearance === "reuse" ? (
          textures.length === 0 ? (
            <p className="text-sm text-[var(--tfmc-mist)]">
              You have no applied textures to reuse yet.
            </p>
          ) : (
            <label className="flex flex-col gap-1.5">
              <span className="text-xs text-[var(--tfmc-mist)]">
                Applied textures you own
              </span>
              <select
                className={fieldClass}
                value={existingTextureId}
                onChange={(e) => setExistingTextureId(e.target.value)}
              >
                <option value="">Select…</option>
                {textures.map((tex) => {
                  const label =
                    (tex.ia_item_id && tex.ia_item_id.trim()) ||
                    tex.id.slice(0, 12);
                  return (
                    <option key={tex.id} value={tex.id}>
                      {label} — CMD {tex.cmd}
                    </option>
                  );
                })}
              </select>
            </label>
          )
        ) : null}
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-medium text-[var(--tfmc-stone)]">Extras</h2>
        <label className="flex flex-col gap-1.5">
          <span className="text-xs text-[var(--tfmc-mist)]">
            Lore (one line per row)
          </span>
          <textarea
            className={`${fieldClass} min-h-[5rem]`}
            value={loreText}
            onChange={(e) => setLoreText(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1.5">
          <span className="text-xs text-[var(--tfmc-mist)]">Drink message</span>
          <input
            className={fieldClass}
            value={drinkMessage}
            onChange={(e) => setDrinkMessage(e.target.value)}
            maxLength={120}
          />
        </label>
        <label className="flex flex-col gap-1.5">
          <span className="text-xs text-[var(--tfmc-mist)]">Drink title</span>
          <input
            className={fieldClass}
            value={drinkTitle}
            onChange={(e) => setDrinkTitle(e.target.value)}
            maxLength={48}
          />
        </label>
        <label className="inline-flex items-center gap-2 text-sm text-[var(--tfmc-cream)]">
          <input
            type="checkbox"
            checked={glint}
            onChange={(e) => setGlint(e.target.checked)}
          />
          Enchantment glint
        </label>
      </section>

      {error ? (
        <p className="text-sm text-[#e8a0a0]" role="alert">
          {error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={submitting}
        className="inline-flex items-center justify-center rounded-sm bg-[var(--tfmc-accent)] px-5 py-2.5 text-sm font-semibold text-[var(--tfmc-forest-deep)] transition-opacity hover:opacity-90 disabled:opacity-50"
      >
        {submitting ? "Submitting…" : "Submit drink"}
      </button>
    </form>
  );
}

function NumberField({
  label,
  value,
  onChange,
  min,
  max,
}: {
  label: string;
  value: number;
  onChange: (n: number) => void;
  min?: number;
  max?: number;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs text-[var(--tfmc-mist)]">{label}</span>
      <input
        type="number"
        className={fieldClass}
        value={value}
        min={min}
        max={max}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </label>
  );
}

function checkPngSize(file: File): Promise<boolean> {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img.width === EXPECTED_PNG_SIZE && img.height === EXPECTED_PNG_SIZE);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(false);
    };
    img.src = url;
  });
}
