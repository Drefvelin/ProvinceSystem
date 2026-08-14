import { useEffect, useState } from "react";
import type { RefObject } from "react";
import type {
  CursorTooltip,
  HoverOverlay,
  MapId,
  MapMode,
  MapObject,
} from "./types";
import { MAP_BOUNDS, apiBase, mapBaseImageUrl } from "./types";
import { overlayPathFromHoverUrl, overlayStyle } from "./overlayStyle";

const panelClass =
  "rounded-lg border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-moss)_35%,var(--tfmc-forest-deep))] shadow-lg";

const HOVER_OVERLAY_OPACITY = 0.72;
const HOVER_OVERLAY_EXPAND = 0.01;
const DRILL_STACK_OVERLAY_OPACITY = 0.88;
const PROVINCE_MODE_OVERLAY_OPACITY = 0.72;
const OVERLAY_TRANSITION_CLASS =
  "pointer-events-none absolute transition-[left,top,width,height,opacity] duration-150 ease-out";

function HoverOverlayImage({
  overlay,
  mapW,
  mapH,
}: {
  overlay: HoverOverlay;
  mapW: number;
  mapH: number;
}) {
  const [loadedUrl, setLoadedUrl] = useState<string | null>(null);
  const url = overlay.url;

  const markLoaded = () => setLoadedUrl(url);

  const ready = loadedUrl === url;
  const positioned = overlayStyle(overlay.overlay, mapW, mapH, {
    expand: ready ? HOVER_OVERLAY_EXPAND : 0,
  });
  const visible = ready && positioned.visibility !== "hidden";

  return (
    <img
      key={url}
      src={url}
      alt="Hovered region"
      ref={(node) => {
        if (node?.complete) markLoaded();
      }}
      className={OVERLAY_TRANSITION_CLASS}
      style={{
        ...positioned,
        opacity: visible ? HOVER_OVERLAY_OPACITY : 0,
      }}
      onLoad={markLoaded}
    />
  );
}

type MapCanvasProps = {
  mapId: MapId;
  mapType: MapMode;
  canvasRef: RefObject<HTMLCanvasElement | null>;
  mapObjects: MapObject[];
  hoveredOverlay: HoverOverlay | null;
  cursorTooltip: CursorTooltip | null;
  onMouseMove: (e: React.MouseEvent<HTMLDivElement>) => void;
  onMouseLeave: () => void;
  onClick: (e: React.MouseEvent<HTMLDivElement>) => void;
};

export default function MapCanvas({
  mapId,
  mapType,
  canvasRef,
  mapObjects,
  hoveredOverlay,
  cursorTooltip,
  onMouseMove,
  onMouseLeave,
  onClick,
}: MapCanvasProps) {
  const base = apiBase();
  const [mapSize, setMapSize] = useState({
    w: MAP_BOUNDS[mapId],
    h: MAP_BOUNDS[mapId],
  });

  useEffect(() => {
    setMapSize({ w: MAP_BOUNDS[mapId], h: MAP_BOUNDS[mapId] });
  }, [mapId]);

  const baseMapSrc = mapBaseImageUrl(mapId);

  const showProvinceOverlay =
    mapType === "terrain" || mapType === "fertility" || mapType === "prosperity";

  const handleBaseMapLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    if (img.naturalWidth > 0 && img.naturalHeight > 0) {
      setMapSize({ w: img.naturalWidth, h: img.naturalHeight });
    }
  };

  const hoveredPath = hoveredOverlay
    ? overlayPathFromHoverUrl(hoveredOverlay.url)
    : null;

  return (
    <div
      className={`relative max-w-full overflow-hidden ${panelClass}`}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
    >
      {cursorTooltip?.text && (
        <div
          className="pointer-events-none fixed z-50 rounded-md bg-[var(--tfmc-forest-deep)] px-3 py-1.5 shadow-lg"
          style={{
            left: cursorTooltip.x + 12,
            top: cursorTooltip.y + 12,
          }}
        >
          <p className="whitespace-pre-line text-sm text-[var(--tfmc-cream)]">
            {cursorTooltip.text}
          </p>
          {cursorTooltip.hint && (
            <p className="mt-1 whitespace-pre-line text-xs leading-snug text-[var(--tfmc-stone)]">
              {cursorTooltip.hint}
            </p>
          )}
        </div>
      )}
      <img
        key={baseMapSrc}
        src={baseMapSrc}
        alt="Map"
        className="h-auto w-full"
        onLoad={handleBaseMapLoad}
      />
      <canvas
        ref={canvasRef}
        className="pointer-events-none absolute left-0 top-0 h-auto w-full opacity-0"
      />
      {showProvinceOverlay && (
        <img
          src={`${base}/${mapId}/mapdata/${mapType}`}
          alt={`${mapType} overlay`}
          className="pointer-events-none absolute left-0 top-0 h-auto w-full"
          style={{ opacity: PROVINCE_MODE_OVERLAY_OPACITY }}
        />
      )}
      {hoveredOverlay && (
        <HoverOverlayImage
          overlay={hoveredOverlay}
          mapW={mapSize.w}
          mapH={mapSize.h}
        />
      )}
      {mapObjects
        .filter((obj) => obj.visible)
        .map((obj) => (
          <img
            key={obj.id}
            crossOrigin="anonymous"
            src={`${base}/${mapId}/regions/${mapType}/${obj.path}`}
            alt={`Overlay ${obj.id}`}
            className={OVERLAY_TRANSITION_CLASS}
            style={{
              ...overlayStyle(obj.overlay, mapSize.w, mapSize.h, {
                expand:
                  hoveredPath && obj.path === hoveredPath
                    ? HOVER_OVERLAY_EXPAND
                    : 0,
              }),
              opacity: DRILL_STACK_OVERLAY_OPACITY,
            }}
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
        ))}
    </div>
  );
}
