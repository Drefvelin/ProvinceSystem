"use client";

import { useEffect, useState } from "react";
import ModelPreview from "../../components/skins/ModelPreview";
import { composeTintedPotionFile } from "../../../lib/drinks/potionTint";
import { isCharacterUiDev } from "../../../lib/characters/uiDev";

export default function DrinksDevPreviewPage() {
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [color, setColor] = useState("#C45A12");

  useEffect(() => {
    if (!isCharacterUiDev()) return;
    let cancelled = false;
    void (async () => {
      const file = await composeTintedPotionFile(color);
      if (cancelled) return;
      setPreviewFile(file);
      setError(file ? null : "composeTintedPotionFile returned null");
    })();
    return () => {
      cancelled = true;
    };
  }, [color]);

  if (!isCharacterUiDev()) {
    return (
      <main className="mx-auto max-w-lg px-6 py-16 text-[var(--tfmc-mist)]">
        Dev preview is disabled. Set NEXT_PUBLIC_CHARACTER_UI_DEV=1.
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-lg space-y-4 px-6 py-16">
      <h1 className="text-2xl text-[var(--tfmc-cream)]">Drinks preview (dev)</h1>
      <label className="flex items-center gap-2 text-sm text-[var(--tfmc-stone)]">
        Color
        <input
          type="color"
          value={color}
          onChange={(e) => setColor(e.target.value)}
        />
        <code>{color}</code>
      </label>
      {error ? <p className="text-sm text-red-300">{error}</p> : null}
      {previewFile ? (
        <ModelPreview
          kind="handheld"
          flatDisplayPreset="generated"
          flatTextureFile={previewFile}
          textureFile={previewFile}
        />
      ) : (
        <p className="text-sm text-[var(--tfmc-mist)]">Building preview…</p>
      )}
    </main>
  );
}
