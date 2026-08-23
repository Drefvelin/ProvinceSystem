import type { TitleDraft } from "@/app/hooks/useEditorDraft";

import {
  buildRgbToTitleId,
  buildTitlePickIndex,
  pickTitleIdAt,
  type TitlePickIndex,
} from "./buildTitlePickIndex";

export type CountyPickIndex = TitlePickIndex & {
  rgbToCountyId: Record<string, string>;
};

export function buildRgbToCountyId(draft: TitleDraft): Record<string, string> {
  return buildRgbToTitleId(draft);
}

export function pickCountyIdAt(
  imageData: ImageData,
  x: number,
  y: number,
  rgbToCountyId: Record<string, string>
): string | null {
  return pickTitleIdAt(imageData, x, y, rgbToCountyId);
}

export function buildCountyPickIndex(
  countyDraft: TitleDraft,
  imageData: ImageData
): CountyPickIndex {
  const index = buildTitlePickIndex(countyDraft, imageData);
  return {
    ...index,
    rgbToCountyId: index.rgbToTitleId,
  };
}
