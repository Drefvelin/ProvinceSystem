import type { EditorProvinceRow } from "@/lib/map/api";
import { parseRgbString } from "@/app/lib/map/titleRgb";

export type ProvinceIndex = {
  rgbToProvinceId: Record<string, number>;
  provinceToRgb: Record<number, string>;
  provinceMap: Int32Array;
  width: number;
  height: number;
};

export type ProvincePixelIndex = Map<number, Uint32Array>;

export function buildProvincePixelIndex(
  provinceMap: Int32Array
): ProvincePixelIndex {
  const buckets = new Map<number, number[]>();

  for (let i = 0; i < provinceMap.length; i++) {
    const pid = provinceMap[i];
    if (pid < 0) continue;
    const list = buckets.get(pid);
    if (list) {
      list.push(i);
    } else {
      buckets.set(pid, [i]);
    }
  }

  const result: ProvincePixelIndex = new Map();
  for (const [pid, list] of buckets) {
    result.set(pid, Uint32Array.from(list));
  }
  return result;
}

function packRgb(r: number, g: number, b: number): number {
  return (r << 16) | (g << 8) | b;
}

function buildCatalogRgbMaps(provinces: EditorProvinceRow[]): {
  rgbToProvinceId: Record<string, number>;
  provinceToRgb: Record<number, string>;
  packedLookup: Record<number, number>;
} {
  const rgbToProvinceId: Record<string, number> = {};
  const provinceToRgb: Record<number, string> = {};
  const packedLookup: Record<number, number> = {};

  for (const row of provinces) {
    const parsed = parseRgbString(row.rgb);
    if (!parsed) continue;
    const [r, g, b] = parsed;
    rgbToProvinceId[row.rgb] = row.id;
    provinceToRgb[row.id] = row.rgb;
    packedLookup[packRgb(r, g, b)] = row.id;
  }

  return { rgbToProvinceId, provinceToRgb, packedLookup };
}

export function deserializeProvinceIdGrid(bytes: ArrayBuffer): {
  width: number;
  height: number;
  ids: Uint16Array;
} {
  if (bytes.byteLength < 8) {
    throw new Error("province id grid data too short for header");
  }

  const view = new DataView(bytes);
  const width = view.getInt32(0, true);
  const height = view.getInt32(4, true);
  const pixelCount = width * height;
  const expectedBody = pixelCount * 2;

  if (bytes.byteLength !== 8 + expectedBody) {
    throw new Error(
      `province id grid body length mismatch for ${width}x${height}`
    );
  }

  const ids = new Uint16Array(bytes, 8, pixelCount);
  return { width, height, ids };
}

export function buildProvinceIndexFromGrid(
  provinces: EditorProvinceRow[],
  width: number,
  height: number,
  ids: Uint16Array
): ProvinceIndex {
  const pixelCount = width * height;
  if (ids.length !== pixelCount) {
    throw new Error("province id grid ids length mismatch");
  }

  const provinceMap = new Int32Array(pixelCount);
  for (let i = 0; i < pixelCount; i++) {
    const id = ids[i]!;
    provinceMap[i] = id === 0 ? -1 : id;
  }

  const { rgbToProvinceId, provinceToRgb } = buildCatalogRgbMaps(provinces);

  return {
    rgbToProvinceId,
    provinceToRgb,
    provinceMap,
    width,
    height,
  };
}

export function buildProvinceIndexFromImageData(
  provinces: EditorProvinceRow[],
  imageData: ImageData
): ProvinceIndex {
  const { width, height, data } = imageData;
  const pixelCount = width * height;
  const provinceMap = new Int32Array(pixelCount);
  provinceMap.fill(-1);

  const { rgbToProvinceId, provinceToRgb, packedLookup } =
    buildCatalogRgbMaps(provinces);

  for (let i = 0; i < pixelCount; i++) {
    const offset = i * 4;
    const packed = packRgb(data[offset]!, data[offset + 1]!, data[offset + 2]!);
    const pid = packedLookup[packed];
    if (pid !== undefined) {
      provinceMap[i] = pid;
    }
  }

  return {
    rgbToProvinceId,
    provinceToRgb,
    provinceMap,
    width,
    height,
  };
}
