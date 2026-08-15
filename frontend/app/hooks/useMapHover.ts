import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { getMapCoords, type MapPickViewport } from "./useMapCoords";
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
  viewportCoordsRef: React.MutableRefObject<MapPickViewport | null>;
  guildNameCacheRef: React.MutableRefObject<Record<string, string>> | null;
  sessionToken?: string | null;
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

type PointerPosition = {
  clientX: number;
  clientY: number;
};

function mapObjectsVisibilityKey(mapObjects: MapObject[]): string {
  return mapObjects
    .map((obj) => `${obj.id}:${obj.visible ? 1 : 0}`)
    .join("|");
}

export function useMapHover(props: UseMapHoverProps) {
  const {
    canvasRef,
    viewportCoordsRef,
    mapId,
    mapType,
    loading,
    regionData,
    setCursorTooltip,
    guildNameCacheRef,
    mapObjects,
  } = props;

  const propsRef = useRef(props);
  propsRef.current = props;

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
    sessionToken: props.sessionToken,
  });

  const { handleRegionHover, resetHoverCache } = useRegionHover({
    ...props,
    rgbToId,
  });

  const handleRegionHoverRef = useRef(handleRegionHover);
  const resetHoverCacheRef = useRef(resetHoverCache);
  handleRegionHoverRef.current = handleRegionHover;
  resetHoverCacheRef.current = resetHoverCache;

  const handleProvinceHoverRef = useRef(handleProvinceHover);
  handleProvinceHoverRef.current = handleProvinceHover;

  const rafRef = useRef<number | null>(null);
  const pendingEventRef = useRef<React.MouseEvent<HTMLCanvasElement> | null>(null);
  const lastPointerRef = useRef<PointerPosition | null>(null);
  const [isHoveringClickable, setIsHoveringClickable] = useState(false);

  const processHover = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const current = propsRef.current;
    if (current.loading) return;

    const canvas = current.canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const coords = getMapCoords(
      event,
      canvas,
      current.mapId,
      current.viewportCoordsRef.current
    );
    if (!coords) {
      current.setCursorTooltip(null);
      setIsHoveringClickable(false);
      return;
    }

    if (
      handleProvinceHoverRef.current(
        coords.x,
        coords.y,
        coords.screenX,
        coords.screenY
      )
    ) {
      setIsHoveringClickable(false);
      return;
    }

    const clickable = handleRegionHoverRef.current(
      ctx,
      coords.x,
      coords.y,
      coords.screenX,
      coords.screenY,
      current.setCursorTooltip
    );
    setIsHoveringClickable(clickable);
  }, []);

  const mapObjectsVisibility = useMemo(
    () => mapObjectsVisibilityKey(mapObjects),
    [mapObjects]
  );

  useEffect(() => {
    if (loading) return;

    const pointer = lastPointerRef.current;
    if (!pointer) return;

    resetHoverCacheRef.current();
    processHover({
      clientX: pointer.clientX,
      clientY: pointer.clientY,
    } as React.MouseEvent<HTMLCanvasElement>);
  }, [loading, mapObjectsVisibility, processHover]);

  const onMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (loading) return;

    lastPointerRef.current = {
      clientX: event.clientX,
      clientY: event.clientY,
    };
    pendingEventRef.current = event;

    if (rafRef.current !== null) return;

    rafRef.current = requestAnimationFrame(() => {
      rafRef.current = null;
      const pendingEvent = pendingEventRef.current;
      if (!pendingEvent) return;
      processHover(pendingEvent);
    });
  };

  const onMouseLeave = () => {
    setIsHoveringClickable(false);
  };

  return { onMouseMove, onMouseLeave, isHoveringClickable };
}
