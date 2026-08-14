import { useRef } from "react";
import { buildRegionInfo } from "../components/map/regionInfo";
import { canDrillIntoRegion } from "../components/map/drillUtils";
import type { HoverOverlay, MapMode, RegionInfo, RegionRecord } from "../components/map/types";

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
  drillStack,
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
    imagePath: string | null;
    region: Record<string, unknown> | null;
    overlay?: HoverOverlay["overlay"];
  };
  setHoveredOverlay: (overlay: HoverOverlay | null) => void;
  setRegionInfo: (info: RegionInfo | null) => void;
  setSelectedRegionId: (id: string | null) => void;
  mapDisplayName: string;
  drillStack: string[];
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
    const id = rgbToId[rgb];

    if (!id) {
      lastRgbRef.current = null;
      setHoveredOverlay(null);
      setRegionInfo(null);
      setCursorTooltip(null);
      return;
    }

    setSelectedRegionId(id);

    const region = regionData[id];
    const info = buildRegionInfo(
      id,
      region,
      mapType,
      mapDisplayName,
      regionData
    );

    const tooltipText =
      mapType === "nation"
        ? info.title
        : `${info.title} · ${info.tier}`;

    const hintLines = ["Click to view"];
    if (canDrillIntoRegion(id, regionData, drillStack)) {
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

      const { imagePath, overlay } = getHoverRegion(
        mapType,
        mapId,
        id,
        regionData
      );

      setHoveredOverlay(imagePath ? { url: imagePath, overlay } : null);
      setRegionInfo(info);
    }
  };

  return { handleRegionHover };
}
