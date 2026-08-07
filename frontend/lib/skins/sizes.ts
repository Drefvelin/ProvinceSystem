export type SkinKind = "armor_set" | "item" | "handheld" | "large_handheld";

export type Size = { w: number; h: number };

export const ICON_SIZE: Size = { w: 16, h: 16 };
export const LAYER_SIZE: Size = { w: 64, h: 32 };
export const ITEM_SIZE: Size = { w: 16, h: 16 };
export const LARGE_SIZE: Size = { w: 32, h: 32 };

export const ARMOR_ICON_FIELDS = [
  "helmet",
  "chestplate",
  "leggings",
  "boots",
] as const;

export const ARMOR_LAYER_FIELDS = ["layer_1", "layer_2"] as const;

export const ARMOR_FIELDS = [
  ...ARMOR_ICON_FIELDS,
  ...ARMOR_LAYER_FIELDS,
] as const;

export function expectedSizeForField(
  kind: SkinKind,
  field: string
): Size | null {
  if (kind === "armor_set") {
    if ((ARMOR_ICON_FIELDS as readonly string[]).includes(field)) {
      return ICON_SIZE;
    }
    if ((ARMOR_LAYER_FIELDS as readonly string[]).includes(field)) {
      return LAYER_SIZE;
    }
    return null;
  }
  if (field === "texture") {
    return kind === "large_handheld" ? LARGE_SIZE : ITEM_SIZE;
  }
  return null;
}

export function sizeHint(kind: SkinKind): string {
  if (kind === "armor_set") {
    return "Icons must be 16×16; layers must be 64×32.";
  }
  if (kind === "large_handheld") {
    return "Texture must be 32×32.";
  }
  return "Texture must be 16×16.";
}

/** Read PNG IHDR width/height from a File. */
export function readPngSize(file: File): Promise<Size> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const buf = reader.result;
      if (!(buf instanceof ArrayBuffer) || buf.byteLength < 24) {
        reject(new Error(`${file.name}: not a valid PNG`));
        return;
      }
      const bytes = new Uint8Array(buf);
      const magic = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
      for (let i = 0; i < 8; i++) {
        if (bytes[i] !== magic[i]) {
          reject(new Error(`${file.name}: not a PNG`));
          return;
        }
      }
      const view = new DataView(buf);
      // IHDR type at offset 12
      const type = String.fromCharCode(
        bytes[12],
        bytes[13],
        bytes[14],
        bytes[15]
      );
      if (type !== "IHDR") {
        reject(new Error(`${file.name}: missing IHDR`));
        return;
      }
      resolve({ w: view.getUint32(16), h: view.getUint32(20) });
    };
    reader.onerror = () => reject(new Error(`${file.name}: could not read file`));
    reader.readAsArrayBuffer(file.slice(0, 24));
  });
}

export async function assertFileSize(
  file: File,
  expected: Size,
  label: string
): Promise<void> {
  const size = await readPngSize(file);
  if (size.w !== expected.w || size.h !== expected.h) {
    throw new Error(
      `${label} must be ${expected.w}×${expected.h}, got ${size.w}×${size.h}`
    );
  }
}
