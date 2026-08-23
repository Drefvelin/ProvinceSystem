import { parseRgbString } from "@/app/lib/map/titleRgb";
import {
  resolveCountyProvinces,
  type TitleEntity,
  type TitleLayers,
} from "@/app/lib/titleProvinces";

import type { ProvincePixelIndex } from "./buildProvinceIndex";
import { EDITOR_SELECTION_HIGHLIGHT } from "./editorConstants";

function parseLayerRgb(rgb: string | undefined): [number, number, number] | null {
  if (!rgb) return null;
  return parseRgbString(rgb);
}

export function paintPixelIndices(
  imageData: ImageData,
  indices: Uint32Array | readonly number[],
  rgb: [number, number, number]
): void {
  const { data } = imageData;
  const [r, g, b] = rgb;

  for (let j = 0; j < indices.length; j++) {
    const i = indices[j]!;
    const offset = i * 4;
    data[offset] = r;
    data[offset + 1] = g;
    data[offset + 2] = b;
    data[offset + 3] = 255;
  }
}

export function clearPixelIndices(
  imageData: ImageData,
  indices: Uint32Array | readonly number[]
): void {
  const { data } = imageData;

  for (let j = 0; j < indices.length; j++) {
    const i = indices[j]!;
    const offset = i * 4;
    data[offset] = 0;
    data[offset + 1] = 0;
    data[offset + 2] = 0;
    data[offset + 3] = 0;
  }
}

function resolveCountySelectionRgb(
  pid: number,
  provinceToRgb: Record<number, string>,
  provinceToCounty: Map<number, string>,
  countyColors: Record<string, string>
): [number, number, number] | null {
  const countyId = provinceToCounty.get(pid);
  if (countyId) {
    return parseLayerRgb(countyColors[countyId]);
  }
  return parseLayerRgb(provinceToRgb[pid]);
}

export function fillProvincePixels(
  imageData: ImageData,
  provinceMap: Int32Array,
  provinceIds: ReadonlySet<number> | readonly number[],
  rgb: [number, number, number]
): void {
  const idSet =
    provinceIds instanceof Set ? provinceIds : new Set(provinceIds);
  const { data } = imageData;
  const [r, g, b] = rgb;

  for (let i = 0; i < provinceMap.length; i++) {
    const pid = provinceMap[i];
    if (pid < 0 || !idSet.has(pid)) continue;
    const offset = i * 4;
    data[offset] = r;
    data[offset + 1] = g;
    data[offset + 2] = b;
    data[offset + 3] = 255;
  }
}

export function paintSelectionLayerFull(
  imageData: ImageData,
  provinceMap: Int32Array,
  provinceToRgb: Record<number, string>,
  provinceToCounty: Map<number, string>,
  countyColors: Record<string, string>
): void {
  const { data } = imageData;

  for (let i = 0; i < provinceMap.length; i++) {
    const pid = provinceMap[i];
    if (pid < 0) continue;

    const rgb = resolveCountySelectionRgb(
      pid,
      provinceToRgb,
      provinceToCounty,
      countyColors
    );
    if (!rgb) continue;

    const offset = i * 4;
    data[offset] = rgb[0];
    data[offset + 1] = rgb[1];
    data[offset + 2] = rgb[2];
    data[offset + 3] = 255;
  }
}

export function paintSelectionLayer(
  ctx: CanvasRenderingContext2D,
  provinceMap: Int32Array,
  provinceToRgb: Record<number, string>,
  provinceToCounty: Map<number, string>,
  countyColors: Record<string, string>
): void {
  const { width, height } = ctx.canvas;
  const imageData = ctx.createImageData(width, height);

  paintSelectionLayerFull(
    imageData,
    provinceMap,
    provinceToRgb,
    provinceToCounty,
    countyColors
  );

  ctx.clearRect(0, 0, width, height);
  ctx.putImageData(imageData, 0, 0);
}

export function updateCountySelectionSubset(
  imageData: ImageData,
  pixelIndex: ProvincePixelIndex,
  provinceIds: readonly number[],
  provinceToRgb: Record<number, string>,
  provinceToCounty: Map<number, string>,
  countyColors: Record<string, string>
): void {
  for (const pid of provinceIds) {
    const indices = pixelIndex.get(pid);
    if (!indices) continue;

    const rgb = resolveCountySelectionRgb(
      pid,
      provinceToRgb,
      provinceToCounty,
      countyColors
    );
    if (!rgb) continue;

    paintPixelIndices(imageData, indices, rgb);
  }
}

export function paintActiveLayerFull(
  imageData: ImageData,
  provinceMap: Int32Array,
  activeMembers: readonly number[] | undefined,
  activeRgb: string | undefined,
  selectionIds: ReadonlySet<number>,
  highlightRgb: string = EDITOR_SELECTION_HIGHLIGHT
): void {
  const activeParsed = parseLayerRgb(activeRgb);
  if (activeMembers && activeParsed) {
    fillProvincePixels(imageData, provinceMap, activeMembers, activeParsed);
  }

  const highlightParsed = parseLayerRgb(highlightRgb);
  if (highlightParsed && selectionIds.size > 0) {
    fillProvincePixels(imageData, provinceMap, selectionIds, highlightParsed);
  }
}

export function paintActiveLayer(
  ctx: CanvasRenderingContext2D,
  provinceMap: Int32Array,
  activeMembers: readonly number[] | undefined,
  activeRgb: string | undefined,
  selectionIds: ReadonlySet<number>,
  highlightRgb: string = EDITOR_SELECTION_HIGHLIGHT
): void {
  const { width, height } = ctx.canvas;
  const imageData = ctx.createImageData(width, height);

  paintActiveLayerFull(
    imageData,
    provinceMap,
    activeMembers,
    activeRgb,
    selectionIds,
    highlightRgb
  );

  ctx.clearRect(0, 0, width, height);
  ctx.putImageData(imageData, 0, 0);
}

export function updateCountyActiveSubset(
  imageData: ImageData,
  pixelIndex: ProvincePixelIndex,
  activeProvinceIds: readonly number[],
  activeRgb: string | undefined,
  clearProvinceIds: readonly number[] = []
): void {
  for (const pid of clearProvinceIds) {
    const indices = pixelIndex.get(pid);
    if (indices) clearPixelIndices(imageData, indices);
  }

  const parsed = parseLayerRgb(activeRgb);
  if (!parsed) return;

  for (const pid of activeProvinceIds) {
    const indices = pixelIndex.get(pid);
    if (indices) paintPixelIndices(imageData, indices, parsed);
  }
}

type ChildPaintEntry = TitleEntity & { rgb?: string };

export function paintChildSelectionLayerFull(
  imageData: ImageData,
  provinceMap: Int32Array,
  childDraft: Record<string, ChildPaintEntry>,
  resolveFn: (childId: string, layers: TitleLayers) => number[],
  layers: TitleLayers
): void {
  for (const [childId, entry] of Object.entries(childDraft)) {
    const rgb = parseLayerRgb(entry.rgb);
    if (!rgb) continue;
    const provinceIds = resolveFn(childId, layers);
    fillProvincePixels(imageData, provinceMap, provinceIds, rgb);
  }
}

export function paintChildSelectionLayer(
  ctx: CanvasRenderingContext2D,
  provinceMap: Int32Array,
  childDraft: Record<string, ChildPaintEntry>,
  resolveFn: (childId: string, layers: TitleLayers) => number[],
  layers: TitleLayers
): void {
  const { width, height } = ctx.canvas;
  const imageData = ctx.createImageData(width, height);

  paintChildSelectionLayerFull(
    imageData,
    provinceMap,
    childDraft,
    resolveFn,
    layers
  );

  ctx.clearRect(0, 0, width, height);
  ctx.putImageData(imageData, 0, 0);
}

export function updateChildSelectionSubset(
  imageData: ImageData,
  pixelIndex: ProvincePixelIndex,
  childIds: readonly string[],
  childColors: Record<string, string>,
  resolveFn: (childId: string, layers: TitleLayers) => number[],
  layers: TitleLayers
): void {
  for (const childId of childIds) {
    const rgb = parseLayerRgb(childColors[childId]);
    if (!rgb) continue;

    const provinceIds = resolveFn(childId, layers);
    for (const pid of provinceIds) {
      const indices = pixelIndex.get(pid);
      if (indices) paintPixelIndices(imageData, indices, rgb);
    }
  }
}

export function paintParentActiveLayerFull(
  imageData: ImageData,
  provinceMap: Int32Array,
  memberChildIds: readonly string[] | undefined,
  parentRgb: string | undefined,
  resolveFn: (childId: string, layers: TitleLayers) => number[],
  layers: TitleLayers
): void {
  const activeParsed = parseLayerRgb(parentRgb);
  if (!memberChildIds || memberChildIds.length === 0 || !activeParsed) return;

  const provinceIds: number[] = [];
  for (const childId of memberChildIds) {
    provinceIds.push(...resolveFn(childId, layers));
  }
  fillProvincePixels(imageData, provinceMap, provinceIds, activeParsed);
}

export function paintParentActiveLayer(
  ctx: CanvasRenderingContext2D,
  provinceMap: Int32Array,
  memberChildIds: readonly string[] | undefined,
  parentRgb: string | undefined,
  resolveFn: (childId: string, layers: TitleLayers) => number[],
  layers: TitleLayers
): void {
  const { width, height } = ctx.canvas;
  const imageData = ctx.createImageData(width, height);

  paintParentActiveLayerFull(
    imageData,
    provinceMap,
    memberChildIds,
    parentRgb,
    resolveFn,
    layers
  );

  ctx.clearRect(0, 0, width, height);
  ctx.putImageData(imageData, 0, 0);
}

export function updateParentActiveSubset(
  imageData: ImageData,
  pixelIndex: ProvincePixelIndex,
  memberChildIds: readonly string[] | undefined,
  parentRgb: string | undefined,
  resolveFn: (childId: string, layers: TitleLayers) => number[],
  layers: TitleLayers,
  clearChildIds: readonly string[] = []
): void {
  for (const childId of clearChildIds) {
    const provinceIds = resolveFn(childId, layers);
    for (const pid of provinceIds) {
      const indices = pixelIndex.get(pid);
      if (indices) clearPixelIndices(imageData, indices);
    }
  }

  const parsed = parseLayerRgb(parentRgb);
  if (!parsed || !memberChildIds || memberChildIds.length === 0) return;

  for (const childId of memberChildIds) {
    const provinceIds = resolveFn(childId, layers);
    for (const pid of provinceIds) {
      const indices = pixelIndex.get(pid);
      if (indices) paintPixelIndices(imageData, indices, parsed);
    }
  }
}

function countyDraftToTitleLayers(
  countyDraft: Record<string, TitleEntity>
): TitleLayers {
  return { county: countyDraft };
}

export function paintDuchySelectionLayer(
  ctx: CanvasRenderingContext2D,
  provinceMap: Int32Array,
  countyDraft: Record<string, TitleEntity>
): void {
  const layers = countyDraftToTitleLayers(countyDraft);
  paintChildSelectionLayer(
    ctx,
    provinceMap,
    countyDraft,
    resolveCountyProvinces,
    layers
  );
}

export function paintDuchyActiveLayer(
  ctx: CanvasRenderingContext2D,
  provinceMap: Int32Array,
  memberCountyIds: readonly string[] | undefined,
  duchyRgb: string | undefined,
  countyDraft: Record<string, TitleEntity>
): void {
  const layers = countyDraftToTitleLayers(countyDraft);
  paintParentActiveLayer(
    ctx,
    provinceMap,
    memberCountyIds,
    duchyRgb,
    resolveCountyProvinces,
    layers
  );
}
