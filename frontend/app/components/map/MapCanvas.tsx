import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";
import type { RefObject, MutableRefObject } from "react";
import type {
  CursorTooltip,
  HoverOverlay,
  MapId,
  MapMode,
  MapObject,
} from "./types";
import { MAP_BOUNDS } from "./types";
import type { MapMarker } from "../../lib/mapMarkers";
import { isMarkerMapMode } from "../../lib/mapMarkers";
import {
  HOVER_OVERLAY_EXPAND,
  overlayPathFromHoverUrl,
  overlayStyle,
} from "./overlayStyle";
import LabelLayer from "./LabelLayer";
import MapMarkerLayer from "./MapMarkerLayer";
import MapAuthImage from "./MapAuthImage";
import MapViewport from "./MapViewport";
import { useMapViewport } from "../../hooks/useMapViewport";
import { useMapAssetUrl } from "../../hooks/useMapAssetUrl";
import type { MapPickViewport } from "../../hooks/useMapCoords";
import type { NationLabelSpec } from "../../lib/mapLabels";
import { mapApiPathFromUrl } from "@/lib/map/api";

const panelClass =
  "rounded-lg border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-moss)_35%,var(--tfmc-forest-deep))] shadow-lg";

const HOVER_OVERLAY_OPACITY = 0.72;
const DRILL_STACK_OVERLAY_OPACITY = 0.88;
const PROVINCE_MODE_OVERLAY_OPACITY = 0.72;
const OVERLAY_TRANSITION_CLASS =
  "pointer-events-none absolute transition-[left,top,width,height,opacity] duration-150 ease-out";

function mapInteractionCursor(
  isPanning: boolean,
  isHoveringClickable: boolean
): string {
  if (isPanning) return "cursor-grabbing";
  if (isHoveringClickable) return "cursor-pointer";
  return "cursor-grab";
}

function applyNaturalMapSize(
  img: HTMLImageElement,
  setMapSize: Dispatch<SetStateAction<{ w: number; h: number }>>
) {
  const w = img.naturalWidth;
  const h = img.naturalHeight;
  if (w <= 0 || h <= 0) return;

  setMapSize((current) =>
    current.w === w && current.h === h ? current : { w, h }
  );
}

function HoverOverlayImage({
  mapId,
  sessionToken,
  overlay,
  mapW,
  mapH,
  opacity = HOVER_OVERLAY_OPACITY,
  alt = "Hovered region",
  imageClassName = "",
}: {
  mapId: MapId;
  sessionToken?: string | null;
  overlay: HoverOverlay;
  mapW: number;
  mapH: number;
  opacity?: number;
  alt?: string;
  imageClassName?: string;
}) {
  const [loadedUrl, setLoadedUrl] = useState<string | null>(null);
  const path = mapApiPathFromUrl(overlay.url);
  const { url } = useMapAssetUrl(mapId, path, sessionToken, Boolean(path));

  useEffect(() => {
    setLoadedUrl(null);
  }, [url]);

  const markLoaded = useCallback(() => {
    if (url) setLoadedUrl(url);
  }, [url]);

  const ready = Boolean(url) && loadedUrl === url;
  const positioned = overlayStyle(overlay.overlay, mapW, mapH, {
    expand: ready ? HOVER_OVERLAY_EXPAND : 0,
  });
  const show =
    Boolean(url) && positioned.visibility !== "hidden" && mapW > 0 && mapH > 0;
  const imageOpacity = show ? (ready ? opacity : opacity * 0.35) : 0;

  if (!url) return null;

  return (
    <img
      key={url}
      src={url}
      alt={alt}
      ref={(node) => {
        if (node?.complete && node.naturalWidth > 0) markLoaded();
      }}
      className={`${OVERLAY_TRANSITION_CLASS} z-10 ${imageClassName}`.trim()}
      style={{
        ...positioned,
        opacity: imageOpacity,
      }}
      onLoad={markLoaded}
      onError={() => {
        setLoadedUrl(null);
      }}
    />
  );
}

type MapCanvasProps = {
  mapId: MapId;
  mapType: MapMode;
  sessionToken?: string | null;
  canvasRef: RefObject<HTMLCanvasElement | null>;
  mapObjects: MapObject[];
  hoveredOverlay: HoverOverlay | null;
  hoveredFortZoc?: HoverOverlay | null;
  cursorTooltip: CursorTooltip | null;
  labels?: NationLabelSpec[];
  markers?: MapMarker[];
  hoveredMarkerId?: string | null;
  hoveredNationId?: string | null;
  viewportCoordsRef?: MutableRefObject<MapPickViewport | null>;
  onMouseMove: (e: React.MouseEvent<HTMLCanvasElement>) => void;
  onMouseLeave: () => void;
  onClick: (e: React.MouseEvent<HTMLCanvasElement>) => void;
  isHoveringClickable?: boolean;
};

export default function MapCanvas({
  mapId,
  mapType,
  sessionToken,
  canvasRef,
  mapObjects,
  hoveredOverlay,
  hoveredFortZoc = null,
  cursorTooltip,
  labels = [],
  markers = [],
  hoveredMarkerId = null,
  hoveredNationId = null,
  viewportCoordsRef,
  onMouseMove,
  onMouseLeave,
  onClick,
  isHoveringClickable = false,
}: MapCanvasProps) {
  const [mapSize, setMapSize] = useState({
    w: MAP_BOUNDS[mapId],
    h: MAP_BOUNDS[mapId],
  });

  const viewport = useMapViewport({ mapSize });
  const appliedNaturalSizeRef = useRef<{ w: number; h: number } | null>(null);

  const syncNaturalMapSize = (img: HTMLImageElement) => {
    const w = img.naturalWidth;
    const h = img.naturalHeight;
    if (w <= 0 || h <= 0) return;

    const applied = appliedNaturalSizeRef.current;
    if (applied?.w === w && applied?.h === h) return;

    appliedNaturalSizeRef.current = { w, h };
    applyNaturalMapSize(img, setMapSize);
  };

  if (viewportCoordsRef) {
    viewportCoordsRef.current = {
      displayScale: viewport.displayScale,
      translateX: viewport.translateX,
      translateY: viewport.translateY,
      viewportElement: viewport.viewportRef.current,
      mapSize,
    };
  }

  useEffect(() => {
    appliedNaturalSizeRef.current = null;
    setMapSize({ w: MAP_BOUNDS[mapId], h: MAP_BOUNDS[mapId] });
  }, [mapId]);

  useEffect(() => {
    viewport.resetViewport({ animated: true });
  }, [mapId, mapType, viewport.resetViewport]);

  const showProvinceOverlay =
    mapType === "terrain" || mapType === "fertility" || mapType === "prosperity";

  const handleBaseMapLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    syncNaturalMapSize(e.currentTarget);
  };

  const hoveredPath = hoveredOverlay
    ? overlayPathFromHoverUrl(hoveredOverlay.url)
    : null;

  const interactionCursor = mapInteractionCursor(
    viewport.isPanning,
    isHoveringClickable
  );

  return (
    <div className={`relative max-w-full overflow-hidden ${panelClass}`}>
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
      <MapViewport
        mapSize={mapSize}
        viewportRef={viewport.viewportRef}
        transformStyle={viewport.transformStyle}
        transformTransition={viewport.transformTransition}
        cursorClassName={interactionCursor}
        isPanning={viewport.isPanning}
      >
        <MapAuthImage
          mapId={mapId}
          path={`/${mapId}/map`}
          sessionToken={sessionToken}
          alt="Map"
          className="pointer-events-none block h-full w-full"
          imgRef={(node) => {
            if (node?.complete) {
              syncNaturalMapSize(node);
            }
          }}
          onLoad={handleBaseMapLoad}
        />
        {showProvinceOverlay && (
          <MapAuthImage
            mapId={mapId}
            path={`/${mapId}/mapdata/${mapType}`}
            sessionToken={sessionToken}
            alt={`${mapType} overlay`}
            className="pointer-events-none absolute inset-0 h-full w-full"
            style={{ opacity: PROVINCE_MODE_OVERLAY_OPACITY }}
          />
        )}
        {mapObjects
          .filter((obj) => obj.visible)
          .map((obj) => (
            <MapAuthImage
              key={obj.id}
              mapId={mapId}
              path={`/${mapId}/regions/${mapType}/${obj.path}`}
              sessionToken={sessionToken}
              crossOrigin="anonymous"
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
        {isMarkerMapMode(mapType) && hoveredFortZoc && (
          <HoverOverlayImage
            mapId={mapId}
            sessionToken={sessionToken}
            overlay={hoveredFortZoc}
            mapW={mapSize.w}
            mapH={mapSize.h}
            opacity={0.85}
            alt="Fort zone of control"
          />
        )}
        {hoveredOverlay && (
          <HoverOverlayImage
            mapId={mapId}
            sessionToken={sessionToken}
            overlay={hoveredOverlay}
            mapW={mapSize.w}
            mapH={mapSize.h}
          />
        )}
        <MapMarkerLayer
          markers={markers}
          hoveredMarkerId={hoveredMarkerId}
          mapW={mapSize.w}
          mapH={mapSize.h}
          mapType={mapType}
          displayScale={viewport.displayScale}
          layer="base"
        />
        <LabelLayer
          labels={labels}
          mapW={mapSize.w}
          mapH={mapSize.h}
          displayScale={viewport.displayScale}
          hoveredNationId={hoveredNationId}
        />
        <MapMarkerLayer
          markers={markers}
          hoveredMarkerId={hoveredMarkerId}
          mapW={mapSize.w}
          mapH={mapSize.h}
          mapType={mapType}
          displayScale={viewport.displayScale}
          layer="hovered"
        />
        <canvas
          ref={canvasRef}
          className={`pointer-events-auto absolute inset-0 z-20 h-full w-full opacity-0 ${interactionCursor}`}
          onMouseMove={onMouseMove}
          onMouseLeave={onMouseLeave}
          onClick={onClick}
        />
      </MapViewport>
    </div>
  );
}
