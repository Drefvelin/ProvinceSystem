import { describe, expect, it } from "vitest";

import { getMapCoords, type MapPickViewport } from "./useMapCoords";

function mockMouseEvent(clientX: number, clientY: number): React.MouseEvent {
  return { clientX, clientY } as React.MouseEvent;
}

function mockCanvas(
  rect: { left: number; top: number; width: number; height: number },
  size = { width: 2000, height: 2000 }
): HTMLCanvasElement {
  return {
    width: size.width,
    height: size.height,
    getBoundingClientRect: () => ({
      left: rect.left,
      top: rect.top,
      width: rect.width,
      height: rect.height,
      right: rect.left + rect.width,
      bottom: rect.top + rect.height,
      x: rect.left,
      y: rect.top,
      toJSON: () => ({}),
    }),
  } as HTMLCanvasElement;
}

function mockViewportElement(rect: {
  left: number;
  top: number;
  width: number;
  height: number;
}): HTMLDivElement {
  return {
    getBoundingClientRect: () => ({
      left: rect.left,
      top: rect.top,
      width: rect.width,
      height: rect.height,
      right: rect.left + rect.width,
      bottom: rect.top + rect.height,
      x: rect.left,
      y: rect.top,
      toJSON: () => ({}),
    }),
  } as HTMLDivElement;
}

describe("getMapCoords legacy path", () => {
  it("maps cursor position with uniform rect scaling", () => {
    const canvas = mockCanvas({ left: 100, top: 50, width: 1000, height: 1000 });

    const coords = getMapCoords(mockMouseEvent(600, 550), canvas, "main");

    expect(coords).toEqual({
      x: 1000,
      y: 1000,
      screenX: 600,
      screenY: 550,
    });
  });

  it("returns null when cursor is outside the canvas rect", () => {
    const canvas = mockCanvas({ left: 100, top: 50, width: 1000, height: 1000 });

    expect(getMapCoords(mockMouseEvent(50, 550), canvas, "main")).toBeNull();
  });
});

describe("getMapCoords viewport path", () => {
  const mapSize = { w: 2000, h: 2000 };
  const viewportRect = { left: 100, top: 50, width: 1000, height: 1000 };

  function viewport(overrides: Partial<MapPickViewport> = {}): MapPickViewport {
    return {
      displayScale: 1,
      translateX: 0,
      translateY: 0,
      viewportElement: mockViewportElement(viewportRect),
      mapSize,
      ...overrides,
    };
  }

  it("matches legacy mapping at fit-to-width scale", () => {
    const canvas = mockCanvas({ left: 100, top: 50, width: 1000, height: 1000 });

    const legacy = getMapCoords(mockMouseEvent(600, 550), canvas, "main");
    const transformed = getMapCoords(
      mockMouseEvent(600, 550),
      canvas,
      "main",
      viewport({ displayScale: 0.5 })
    );

    expect(transformed).toEqual(legacy);
  });

  it("maps zoomed viewport coordinates via screenToMap", () => {
    const canvas = mockCanvas({ left: 100, top: 50, width: 2000, height: 2000 });

    const coords = getMapCoords(
      mockMouseEvent(700, 650),
      canvas,
      "main",
      viewport({ displayScale: 2 })
    );

    expect(coords).toEqual({
      x: 300,
      y: 300,
      screenX: 700,
      screenY: 650,
    });
  });

  it("accounts for pan translate", () => {
    const canvas = mockCanvas({ left: 100, top: 50, width: 1000, height: 1000 });

    const coords = getMapCoords(
      mockMouseEvent(450, 450),
      canvas,
      "main",
      viewport({ displayScale: 0.5, translateX: -100, translateY: -50 })
    );

    expect(coords).toEqual({
      x: 900,
      y: 900,
      screenX: 450,
      screenY: 450,
    });
  });

  it("returns null when map point is outside map bounds", () => {
    const canvas = mockCanvas({ left: 100, top: 50, width: 1000, height: 1000 });

    expect(
      getMapCoords(
        mockMouseEvent(50, 550),
        canvas,
        "main",
        viewport()
      )
    ).toBeNull();
  });

  it("falls back to legacy when viewport element is missing", () => {
    const canvas = mockCanvas({ left: 100, top: 50, width: 1000, height: 1000 });

    const legacy = getMapCoords(mockMouseEvent(600, 550), canvas, "main");
    const coords = getMapCoords(
      mockMouseEvent(600, 550),
      canvas,
      "main",
      viewport({ viewportElement: null })
    );

    expect(coords).toEqual(legacy);
  });
});
