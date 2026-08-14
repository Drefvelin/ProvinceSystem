import { useMemo, useRef } from "react";
import { getMapCoords } from "./useMapCoords";
import { useProvinceHover } from "./useProvinceHover";
import { useRegionHover } from "./useRegionHover";
import type { MapId, MapMode, MapObject, RegionInfo, RegionRecord } from "../components/map/types";
import type { HoverOverlay } from "../components/map/types";

type UseMapHoverProps = {
  mapId: MapId;
  mapType: MapMode;
  loading: boolean;
  regionData: RegionRecord | null;
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  guildNameCacheRef: React.MutableRefObject<Record<string, string>> | null;
  setCursorTooltip: (tooltip: { x: number; y: number; text: string; hint?: string } | null) => void;
  setHoveredOverlay: (overlay: HoverOverlay | null) => void;
  setRegionInfo: (info: RegionInfo | null) => void;
  setSelectedRegionId: (id: string | null) => void;
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
  mapDisplayName: string;
  mapObjects: MapObject[];
};

export function useMapHover(props: UseMapHoverProps) {
  const {
    canvasRef,
    mapId,
    mapType,
    loading,
    regionData,
    setCursorTooltip,
    guildNameCacheRef,
  } = props;

  const rgbToId = useMemo(() => {
    const map: Record<string, string> = {};
    if (!regionData) return map;

    for (const [id, region] of Object.entries(regionData)) {
      if (region.rgb) map[region.rgb] = id;
    }
    return map;
  }, [regionData]);

  const { handleProvinceHover } = useProvinceHover({
    mapId,
    mapType,
    setCursorTooltip,
    guildNameCacheRef,
  });

  const { handleRegionHover } = useRegionHover({
    ...props,
    rgbToId,
  });

  const rafRef = useRef<number | null>(null);
  const pendingEventRef = useRef<React.MouseEvent<HTMLDivElement> | null>(null);

  const onMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (loading) return;

    pendingEventRef.current = event;

    if (rafRef.current !== null) return;

    rafRef.current = requestAnimationFrame(() => {
      rafRef.current = null;
      const pendingEvent = pendingEventRef.current;
      if (!pendingEvent) return;

      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const coords = getMapCoords(pendingEvent, canvas, mapId);
      if (!coords) {
        setCursorTooltip(null);
        return;
      }

      if (
        handleProvinceHover(
          coords.x,
          coords.y,
          coords.screenX,
          coords.screenY
        )
      ) {
        return;
      }

      handleRegionHover(
        ctx,
        coords.x,
        coords.y,
        coords.screenX,
        coords.screenY,
        setCursorTooltip
      );
    });
  };

  return { onMouseMove };
}
