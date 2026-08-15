import type { MapObject, OverlayBBox } from "../components/map/types";

export function buildMapObjectsFromRegionData(
  regionData: Record<string, unknown>
): MapObject[] {
  return Object.keys(regionData).flatMap((regionId) => {
    const region = regionData[regionId] as Record<string, unknown>;
    const rgb = region.rgb as string | undefined;
    if (!rgb) return [];

    const rgbPath = rgb.replace(/,/g, "_");
    const overlay = region.overlay as OverlayBBox | undefined;
    const overlayNested = region.overlay_nested as OverlayBBox | undefined;

    const entries: MapObject[] = [
      {
        id: regionId,
        visible: !region.overlord,
        path: rgbPath,
        overlay,
      },
    ];

    const subjects = region.subjects as string[] | undefined;
    if (subjects?.length) {
      entries.push({
        id: `${regionId}_nested`,
        visible: false,
        path: `${rgbPath}_nested`,
        overlay: overlayNested,
      });
    }

    return entries;
  });
}

export function initialMapObjectVisibility(
  obj: MapObject,
  regionData: Record<string, unknown>
): boolean {
  if (obj.id.endsWith("_nested")) {
    return false;
  }

  const region = regionData[obj.id] as Record<string, unknown> | undefined;
  if (!region) return obj.visible;
  return !region.overlord;
}
