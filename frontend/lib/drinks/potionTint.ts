/** Compose tinted potion_overlay + untinted glass_bottle (vanilla layer tint). */

import { getApiBase } from "./api";

function parseHex(color: string): { r: number; g: number; b: number } | null {
  const text = (color || "").trim();
  if (!/^#[0-9A-Fa-f]{6}$/.test(text)) return null;
  return {
    r: parseInt(text.slice(1, 3), 16),
    g: parseInt(text.slice(3, 5), 16),
    b: parseInt(text.slice(5, 7), 16),
  };
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load ${src}`));
    img.src = src;
  });
}

export function drinkAssetUrl(filename: string): string {
  return `${getApiBase()}/drinks/assets/${filename}`;
}

export async function composeTintedPotionFile(
  color: string,
  overlayUrl = drinkAssetUrl("potion_overlay.png"),
  bottleUrl = drinkAssetUrl("glass_bottle.png")
): Promise<File | null> {
  const rgb = parseHex(color);
  if (!rgb) return null;
  try {
    const [overlayImg, bottleImg] = await Promise.all([
      loadImage(overlayUrl),
      loadImage(bottleUrl),
    ]);
    const w = Math.max(overlayImg.naturalWidth || 16, bottleImg.naturalWidth || 16);
    const h = Math.max(overlayImg.naturalHeight || 16, bottleImg.naturalHeight || 16);
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    ctx.drawImage(overlayImg, 0, 0, w, h);
    const imageData = ctx.getImageData(0, 0, w, h);
    const data = imageData.data;
    for (let i = 0; i < data.length; i += 4) {
      const a = data[i + 3]!;
      if (a === 0) continue;
      data[i] = Math.floor((data[i]! * rgb.r) / 255);
      data[i + 1] = Math.floor((data[i + 1]! * rgb.g) / 255);
      data[i + 2] = Math.floor((data[i + 2]! * rgb.b) / 255);
    }
    ctx.putImageData(imageData, 0, 0);
    ctx.drawImage(bottleImg, 0, 0, w, h);

    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob(resolve, "image/png")
    );
    if (!blob) return null;
    return new File([blob], "potion-preview.png", { type: "image/png" });
  } catch {
    return null;
  }
}
