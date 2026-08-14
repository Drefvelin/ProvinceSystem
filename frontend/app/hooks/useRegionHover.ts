import { useRef } from "react";
import { buildRegionInfo } from "../components/map/regionInfo";
import { canDrillIntoRegion } from "../components/map/drillUtils";
import type { HoverOverlay, MapMode, MapObject, RegionInfo, RegionRecord } from "../components/map/types";

export function useRegionHover({
  mapId,
  mapType,
  regionData,
  rgbToId,
  getHoverRegion,
  setHoveredOverlay,
  setRegionInfo,
  setSelectedRegionId,
  mapDisplayName,
  mapObjects,
}: {
  mapId: string;
  mapType: MapMode;
  regionData: RegionRecord | null;
  rgbToId: Record<string, string>;
  getHoverRegion: (
    mapType: string,
    mapId: string,
    regionId: string,
    regionData: RegionRecord
  ) => {
    regionId: string | null;
    imagePath: string | null;
    region: Record<string, unknown> | null;
    overlay?: HoverOverlay["overlay"];
  };
  setHoveredOverlay: (overlay: HoverOverlay | null) => void;
  setRegionInfo: (info: RegionInfo | null) => void;
  setSelectedRegionId: (id: string | null) => void;
  mapDisplayName: string;
  mapObjects: MapObject[];
}) {
  const lastRgbRef = useRef<string | null>(null);

  const handleRegionHover = (
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    screenX: number,
    screenY: number,
    setCursorTooltip: (tooltip: { x: number; y: number; text: string; hint?: string } | null) => void
  ) => {
    if (!regionData) return;

    const pixel = ctx.getImageData(x, y, 1, 1).data;
    const rgb = `${pixel[0]},${pixel[1]},${pixel[2]}`;
    const pickId = rgbToId[rgb];

    if (!pickId) {
      lastRgbRef.current = null;
      setHoveredOverlay(null);
      setRegionInfo(null);
      setCursorTooltip(null);
      return;
    }

    const { regionId, imagePath, overlay, region } = getHoverRegion(
      mapType,
      mapId,
      pickId,
      regionData
    );

    if (!regionId || !region) {
      lastRgbRef.current = null;
      setHoveredOverlay(null);
      setRegionInfo(null);
      setCursorTooltip(null);
      return;
    }

    setSelectedRegionId(regionId);

    const info = buildRegionInfo(
      regionId,
      regionData[regionId],
      mapType,
      mapDisplayName,
      regionData
    );

    const tooltipText =
      mapType === "nation"
        ? info.title
        : `${info.title} · ${info.tier}`;

    const hintLines = ["Click to view"];
    if (canDrillIntoRegion(regionId, regionData, mapObjects)) {
      hintLines.push("CTRL+Click to see subjects");
    }

    setCursorTooltip({
      x: screenX,
      y: screenY,
      text: tooltipText,
      hint: hintLines.join("\n"),
    });

    if (rgb !== lastRgbRef.current) {
      lastRgbRef.current = rgb;

      setHoveredOverlay(imagePath ? { url: imagePath, overlay } : null);
      setRegionInfo(info);
    }
  };

  return { handleRegionHover };
}
