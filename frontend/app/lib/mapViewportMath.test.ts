import { describe, expect, it } from "vitest";

import {
  MAP_ZOOM_WHEEL_FACTOR,
  clampTranslate,
  computeDisplayScale,
  computeFitScale,
  mapToScreen,
  screenToMap,
  viewportTransformStyle,
  zoomAtPoint,
} from "./mapViewportMath";

const viewport = { w: 1000, h: 1000 };
const map = { w: 2000, h: 2000 };

describe("computeFitScale", () => {
  it("fits map width to viewport width", () => {
    expect(computeFitScale(viewport, map)).toBe(0.5);
  });
});

describe("clampTranslate", () => {
  it("forces translate to zero at user zoom 1", () => {
    const fitScale = computeFitScale(viewport, map);
    const displayScale = computeDisplayScale(fitScale, 1);
    expect(clampTranslate(viewport, map, displayScale, -200, -300)).toEqual({
      x: 0,
      y: 0,
    });
  });

  it("cannot pan past edges at zoom 2", () => {
    const fitScale = computeFitScale(viewport, map);
    const displayScale = computeDisplayScale(fitScale, 2);
    const minX = viewport.w - map.w * displayScale;
    const minY = viewport.h - map.h * displayScale;

    expect(
      clampTranslate(viewport, map, displayScale, minX - 100, minY - 100)
    ).toEqual({ x: minX, y: minY });
    expect(
      clampTranslate(viewport, map, displayScale, 100, 100)
    ).toEqual({ x: 0, y: 0 });
  });

  it("cannot pan past edges at zoom 3", () => {
    const fitScale = computeFitScale(viewport, map);
    const displayScale = computeDisplayScale(fitScale, 3);
    const minX = viewport.w - map.w * displayScale;
    const minY = viewport.h - map.h * displayScale;

    expect(clampTranslate(viewport, map, displayScale, minX - 50, 50)).toEqual(
      { x: minX, y: 0 }
    );
  });

  it("cannot pan past edges at max zoom 4.5", () => {
    const fitScale = computeFitScale(viewport, map);
    const displayScale = computeDisplayScale(fitScale, 4.5);
    const minX = viewport.w - map.w * displayScale;

    expect(clampTranslate(viewport, map, displayScale, minX - 25, 0)).toEqual(
      { x: minX, y: 0 }
    );
  });
});

describe("screenToMap / mapToScreen", () => {
  it("round-trips through forward and inverse transforms", () => {
    const displayScale = 0.75;
    const translate = { x: -120, y: -80 };
    const mapPoint = { x: 640, y: 512 };

    const screen = mapToScreen(mapPoint.x, mapPoint.y, displayScale, translate);
    const back = screenToMap(screen.x, screen.y, displayScale, translate);

    expect(back.x).toBeCloseTo(mapPoint.x, 5);
    expect(back.y).toBeCloseTo(mapPoint.y, 5);
  });
});

describe("zoomAtPoint", () => {
  it("keeps the map point under the cursor stable across one zoom step", () => {
    const fitScale = computeFitScale(viewport, map);
    const start = { userScale: 1, translateX: 0, translateY: 0 };
    const cursor = { x: 400, y: 600 };
    const displayScale = computeDisplayScale(fitScale, start.userScale);
    const before = screenToMap(cursor.x, cursor.y, displayScale, {
      x: start.translateX,
      y: start.translateY,
    });

    const next = zoomAtPoint(viewport, map, start, cursor, -1);
    const nextDisplayScale = computeDisplayScale(fitScale, next.userScale);
    const after = screenToMap(cursor.x, cursor.y, nextDisplayScale, {
      x: next.translateX,
      y: next.translateY,
    });

    expect(next.userScale).toBeCloseTo(MAP_ZOOM_WHEEL_FACTOR, 5);
    expect(after.x).toBeCloseTo(before.x, 4);
    expect(after.y).toBeCloseTo(before.y, 4);
  });
});

describe("viewportTransformStyle", () => {
  it("emits translate then scale for transform-origin 0 0", () => {
    expect(viewportTransformStyle(0.5, -10, 20)).toBe(
      "translate(-10px, 20px) scale(0.5)"
    );
  });
});
