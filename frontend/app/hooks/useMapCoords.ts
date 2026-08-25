import type { MapId } from "../components/map/types";
import { MAP_BOUNDS } from "../components/map/types";
import { screenToMap, type Size } from "../lib/mapViewportMath";

export type MapPickViewport = {
  displayScale: number;
  translateX: number;
  translateY: number;
  viewportElement: HTMLDivElement | null;
  mapSize: Size;
};

export type MapCoords = {
  x: number;
  y: number;
  screenX: number;
  screenY: number;
};

function getLegacyMapCoords(
  event: React.MouseEvent,
  canvas: HTMLCanvasElement,
  mapId: MapId
): MapCoords | null {
  const rect = canvas.getBoundingClientRect();
  const mapSize =
    canvas.width > 0 && canvas.height > 0
      ? Math.max(canvas.width, canvas.height)
      : (MAP_BOUNDS[mapId] ?? 6400);

  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  if (
    mouseX < 0 ||
    mouseY < 0 ||
    mouseX >= rect.width ||
    mouseY >= rect.height
  ) {
    return null;
  }

  return {
    x: Math.floor((mouseX / rect.width) * mapSize),
    y: Math.floor((mouseY / rect.height) * mapSize),
    screenX: event.clientX,
    screenY: event.clientY,
  };
}

function getViewportMapCoords(
  event: React.MouseEvent,
  viewport: MapPickViewport
): MapCoords | null {
  const { viewportElement, displayScale, translateX, translateY, mapSize } =
    viewport;

  if (!viewportElement || displayScale <= 0) {
    return null;
  }

  const viewportRect = viewportElement.getBoundingClientRect();
  const viewportX = event.clientX - viewportRect.left;
  const viewportY = event.clientY - viewportRect.top;

  const point = screenToMap(viewportX, viewportY, displayScale, {
    x: translateX,
    y: translateY,
  });

  if (
    point.x < 0 ||
    point.y < 0 ||
    point.x >= mapSize.w ||
    point.y >= mapSize.h
  ) {
    return null;
  }

  return {
    x: Math.floor(point.x),
    y: Math.floor(point.y),
    screenX: event.clientX,
    screenY: event.clientY,
  };
}

export function getMapCoords(
  event: React.MouseEvent,
  canvas: HTMLCanvasElement,
  mapId: MapId,
  viewport?: MapPickViewport | null
): MapCoords | null {
  if (viewport?.viewportElement && viewport.displayScale > 0) {
    return getViewportMapCoords(event, viewport);
  }

  return getLegacyMapCoords(event, canvas, mapId);
}
