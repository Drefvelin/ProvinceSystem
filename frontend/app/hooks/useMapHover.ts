import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  getMapCoords,
  mapPixelToPickCanvas,
  type MapPickViewport,
} from "./useMapCoords";
import { useProvinceHover } from "./useProvinceHover";
import { useRegionHover } from "./useRegionHover";
import type { MapId, MapMode, MapObject, RegionInfo, RegionRecord, FortMarker } from "../components/map/types";
import type { HoverOverlay } from "../components/map/types";
import type { MapMarker } from "../lib/mapMarkers";
import { filterVisibleMapMarkers, isMarkerMapMode, pickMapMarkerAt } from "../lib/mapMarkers";
import { lookupFortZocOverlay } from "../lib/fortZoc";

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
  markers?: MapMarker[];
  forts?: FortMarker[];
  setHoveredMarkerId?: (id: string | null) => void;
  setHoveredFortZoc?: (overlay: HoverOverlay | null) => void;
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
    markers,
    forts,
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

    // Must match the pick canvas' own getContext options; this path calls
    // getImageData once per hover frame.
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) return;

    const coords = getMapCoords(
      event,
      canvas,
      current.mapId,
      current.viewportCoordsRef.current
    );
    if (!coords) {
      current.setCursorTooltip(null);
      current.setHoveredMarkerId?.(null);
      current.setHoveredFortZoc?.(null);
      setIsHoveringClickable(false);
      return;
    }

    const displayScale = current.viewportCoordsRef.current?.displayScale ?? 0;
    const visibleMarkers = current.markers?.length
      ? filterVisibleMapMarkers(current.markers, displayScale)
      : [];
    const markerHit = visibleMarkers.length
      ? pickMapMarkerAt(visibleMarkers, coords.x, coords.y)
      : null;
    current.setHoveredMarkerId?.(markerHit?.id ?? null);
    if (markerHit) {
      current.setCursorTooltip(null);
      current.setHoveredOverlay(null);
      resetHoverCacheRef.current();
      if (isMarkerMapMode(current.mapType)) {
        current.setHoveredFortZoc?.(
          lookupFortZocOverlay(markerHit, current.forts ?? [])
        );
      } else {
        current.setHoveredFortZoc?.(null);
      }
      setIsHoveringClickable(true);
      return;
    }

    current.setHoveredFortZoc?.(null);

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

    const pickPixel = mapPixelToPickCanvas(
      coords.x,
      coords.y,
      current.viewportCoordsRef.current?.mapSize,
      canvas
    );
    if (!pickPixel) {
      current.setCursorTooltip(null);
      current.setHoveredOverlay(null);
      setIsHoveringClickable(false);
      return;
    }

    const clickable = handleRegionHoverRef.current(
      ctx,
      pickPixel.x,
      pickPixel.y,
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

  const fortsKey = useMemo(
    () => (forts ?? []).map((fort) => fort.id).join("|"),
    [forts]
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
  }, [loading, mapObjectsVisibility, fortsKey, markers?.length, processHover]);

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
    propsRef.current.setHoveredMarkerId?.(null);
    propsRef.current.setHoveredFortZoc?.(null);
    setIsHoveringClickable(false);
  };

  return { onMouseMove, onMouseLeave, isHoveringClickable };
}
