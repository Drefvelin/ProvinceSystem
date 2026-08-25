export const MAP_ZOOM_MIN = 1;
export const MAP_ZOOM_MAX = 4.5;
export const MAP_ZOOM_WHEEL_FACTOR = 1.1;

export type Size = {
  w: number;
  h: number;
};

export type ViewportTransform = {
  userScale: number;
  translateX: number;
  translateY: number;
};

export type ViewportPoint = {
  x: number;
  y: number;
};

/** Width-fit scale so map matches current `w-full` behaviour at user zoom 1. */
export function computeFitScale(viewport: Size, map: Size): number {
  if (map.w <= 0) return 1;
  return viewport.w / map.w;
}

export function computeDisplayScale(fitScale: number, userScale: number): number {
  return fitScale * userScale;
}

export function clampUserScale(scale: number): number {
  return Math.min(MAP_ZOOM_MAX, Math.max(MAP_ZOOM_MIN, scale));
}

export function clampTranslate(
  viewport: Size,
  map: Size,
  displayScale: number,
  translateX: number,
  translateY: number
): ViewportPoint {
  const displayW = map.w * displayScale;
  const displayH = map.h * displayScale;

  let tx = translateX;
  let ty = translateY;

  if (displayW <= viewport.w) {
    tx = 0;
  } else {
    const minX = viewport.w - displayW;
    tx = Math.min(0, Math.max(minX, tx));
  }

  if (displayH <= viewport.h) {
    ty = 0;
  } else {
    const minY = viewport.h - displayH;
    ty = Math.min(0, Math.max(minY, ty));
  }

  return { x: tx, y: ty };
}

export function mapToScreen(
  mapX: number,
  mapY: number,
  displayScale: number,
  translate: ViewportPoint
): ViewportPoint {
  return {
    x: mapX * displayScale + translate.x,
    y: mapY * displayScale + translate.y,
  };
}

export function screenToMap(
  viewportX: number,
  viewportY: number,
  displayScale: number,
  translate: ViewportPoint
): ViewportPoint {
  if (displayScale === 0) {
    return { x: 0, y: 0 };
  }

  return {
    x: (viewportX - translate.x) / displayScale,
    y: (viewportY - translate.y) / displayScale,
  };
}

export function viewportTransformStyle(
  displayScale: number,
  translateX: number,
  translateY: number
): string {
  return `translate(${translateX}px, ${translateY}px) scale(${displayScale})`;
}

export function zoomAtPoint(
  viewport: Size,
  map: Size,
  transform: ViewportTransform,
  cursor: ViewportPoint,
  wheelDelta: number
): ViewportTransform {
  const fitScale = computeFitScale(viewport, map);
  const displayScale = computeDisplayScale(fitScale, transform.userScale);
  const translate = { x: transform.translateX, y: transform.translateY };

  const mapPoint = screenToMap(cursor.x, cursor.y, displayScale, translate);

  const zoomFactor =
    wheelDelta < 0 ? MAP_ZOOM_WHEEL_FACTOR : 1 / MAP_ZOOM_WHEEL_FACTOR;
  const nextUserScale = clampUserScale(transform.userScale * zoomFactor);
  const nextDisplayScale = computeDisplayScale(fitScale, nextUserScale);

  let nextTranslateX = cursor.x - mapPoint.x * nextDisplayScale;
  let nextTranslateY = cursor.y - mapPoint.y * nextDisplayScale;

  const clamped = clampTranslate(
    viewport,
    map,
    nextDisplayScale,
    nextTranslateX,
    nextTranslateY
  );

  return {
    userScale: nextUserScale,
    translateX: clamped.x,
    translateY: clamped.y,
  };
}
