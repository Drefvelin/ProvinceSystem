import boundsByTexture from "../../wiki/data/generated/recipeIconBounds.json";

/** Canvas width/height followed by the nontransparent pixel bounds (right/bottom exclusive). */
export type IconBounds = readonly [number, number, number, number, number, number];

export function iconTranslation(bounds: IconBounds): [number, number] {
  const [width, height, left, top, right, bottom] = bounds;
  // object-contain fits the whole canvas into a square. Translate by the opaque
  // centre's distance from the canvas centre at that same, undistorted scale.
  const size = Math.max(width, height);
  return [((width - left - right) / (2 * size)) * 100, ((height - top - bottom) / (2 * size)) * 100];
}

export function recipeIconTransform(texture: string): string | undefined {
  const bounds = (boundsByTexture as Record<string, number[]>)[texture];
  if (!bounds) return undefined;
  const [x, y] = iconTranslation(bounds as unknown as IconBounds);
  return `translate(${x}%, ${y}%)`;
}
