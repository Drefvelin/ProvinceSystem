const SLUG_RE = /^[a-z][a-z0-9_]{1,47}$/;

const RESERVED = new Set([
  "test",
  "texture",
  "null",
  "undefined",
  "admin",
  "tfmc",
]);

export const ARMOR_SUFFIXES: Record<string, string> = {
  helmet: "_helmet.png",
  chestplate: "_chestplate.png",
  leggings: "_leggings.png",
  boots: "_boots.png",
  layer_1: "_layer_1.png",
  layer_2: "_layer_2.png",
};

export const BOW_SUFFIXES: Record<string, string> = {
  texture: ".png",
  pull_0: "_0.png",
  pull_1: "_1.png",
  pull_2: "_2.png",
};

export const CROSSBOW_SUFFIXES: Record<string, string> = {
  ...BOW_SUFFIXES,
  charged: "_charged.png",
};

const ARMOR_LABELS: Record<string, string> = {
  helmet: "Helmet",
  chestplate: "Chestplate",
  leggings: "Leggings",
  boots: "Boots",
  layer_1: "Layer 1",
  layer_2: "Layer 2",
};

const BOW_LABELS: Record<string, string> = {
  texture: "Standby texture",
  pull_0: "Pull 0",
  pull_1: "Pull 1",
  pull_2: "Pull 2",
  charged: "Charged",
};

export function assertSlugClient(id: string): void {
  const s = (id || "").trim();
  if (!SLUG_RE.test(s)) {
    throw new Error(
      "File name id must be 2–48 chars: start with a letter, then lowercase letters, numbers, underscores only"
    );
  }
  if (s.includes("__")) {
    throw new Error("File name id cannot contain double underscores");
  }
  if (RESERVED.has(s)) {
    throw new Error(`The name '${s}' is reserved - rename your PNG`);
  }
}

function basename(filename: string): string {
  const normalized = filename.replace(/\\/g, "/");
  const parts = normalized.split("/");
  return parts[parts.length - 1] || filename;
}

/** Texture kinds: file must be `{id}.png`. Returns skin id. */
export function skinIdFromTextureFilename(filename: string): string {
  const name = basename(filename);
  if (!name.endsWith(".png")) {
    throw new Error(
      "Texture must be a PNG named like `blue_knight.png` (lowercase letters, numbers, underscores)"
    );
  }
  const stem = name.slice(0, -".png".length);
  try {
    assertSlugClient(stem);
  } catch {
    throw new Error(
      `Texture file \`${name}\` is invalid. Use a name like \`blue_knight.png\`.`
    );
  }
  return stem;
}

/** Armor: each slot `{id}_helmet.png` etc., same id. Returns skin id. */
export function skinIdFromArmorFilenames(
  files: Record<string, File | null | undefined>
): string {
  const ids: string[] = [];
  for (const [field, suffix] of Object.entries(ARMOR_SUFFIXES)) {
    const label = ARMOR_LABELS[field] || field;
    const file = files[field];
    if (!file) {
      throw new Error(`Missing ${label} file.`);
    }
    const name = basename(file.name);
    if (!name.endsWith(suffix)) {
      throw new Error(
        `${label} file must be named exactly \`{id}${suffix}\` (example: \`blue_knight${suffix}\`). Got \`${name}\`.`
      );
    }
    const stem = name.slice(0, -suffix.length);
    try {
      assertSlugClient(stem);
    } catch {
      throw new Error(
        `${label} file \`${name}\` has an invalid id. Use lowercase letters, numbers, underscores only.`
      );
    }
    ids.push(stem);
  }
  const unique = new Set(ids);
  if (unique.size !== 1) {
    throw new Error(
      "All armor PNGs must share the same id prefix (check your file names)."
    );
  }
  return ids[0];
}

function skinIdFromPrefixedFilenames(
  files: Record<string, File | null | undefined>,
  suffixes: Record<string, string>,
  kindLabel: string
): string {
  const ids: string[] = [];
  for (const [field, suffix] of Object.entries(suffixes)) {
    const label = BOW_LABELS[field] || field;
    const file = files[field];
    if (!file) {
      throw new Error(`Missing ${label} file.`);
    }
    const name = basename(file.name);
    if (field === "texture") {
      if (!name.endsWith(".png") || name.slice(0, -4).endsWith("_0")
        || name.slice(0, -4).endsWith("_1")
        || name.slice(0, -4).endsWith("_2")
        || name.slice(0, -4).endsWith("_charged")) {
        throw new Error(
          `${label} must be named exactly \`{id}.png\` (example: \`blue_shortbow.png\`). Got \`${name}\`.`
        );
      }
      const stem = name.slice(0, -".png".length);
      try {
        assertSlugClient(stem);
      } catch {
        throw new Error(
          `${label} file \`${name}\` has an invalid id. Use lowercase letters, numbers, underscores only.`
        );
      }
      ids.push(stem);
      continue;
    }
    if (!name.endsWith(suffix)) {
      throw new Error(
        `${label} file must be named exactly \`{id}${suffix}\` (example: \`blue_shortbow${suffix}\`). Got \`${name}\`.`
      );
    }
    const stem = name.slice(0, -suffix.length);
    try {
      assertSlugClient(stem);
    } catch {
      throw new Error(
        `${label} file \`${name}\` has an invalid id. Use lowercase letters, numbers, underscores only.`
      );
    }
    ids.push(stem);
  }
  const unique = new Set(ids);
  if (unique.size !== 1) {
    throw new Error(
      `All ${kindLabel} PNGs must share the same id prefix as the base \`{id}.png\` (check your file names).`
    );
  }
  return ids[0];
}

export function assertUploadFilenames(
  kind: string,
  files: Record<string, File | null | undefined>
): string {
  if (kind === "armor_set") {
    return skinIdFromArmorFilenames(files);
  }
  if (kind === "bow" || kind === "large_bow") {
    return skinIdFromPrefixedFilenames(files, BOW_SUFFIXES, "bow");
  }
  if (kind === "crossbow") {
    return skinIdFromPrefixedFilenames(files, CROSSBOW_SUFFIXES, "crossbow");
  }
  const texture = files.texture;
  if (!texture) {
    throw new Error("Missing texture file.");
  }
  return skinIdFromTextureFilename(texture.name);
}
