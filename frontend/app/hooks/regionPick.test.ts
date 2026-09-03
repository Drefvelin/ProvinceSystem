import { describe, expect, it } from "vitest";

import { resolveRegionAtPickPixel } from "./regionPick";
import type { RegionRecord } from "../components/map/types";

function mockCtx(
  width: number,
  height: number,
  pixelAt: (x: number, y: number) => [number, number, number, number]
): CanvasRenderingContext2D {
  return {
    canvas: { width, height },
    getImageData: (x: number, y: number, w: number, h: number) => {
      const data = new Uint8ClampedArray(w * h * 4);
      for (let dy = 0; dy < h; dy++) {
        for (let dx = 0; dx < w; dx++) {
          const [r, g, b, a] = pixelAt(x + dx, y + dy);
          const i = (dy * w + dx) * 4;
          data[i] = r;
          data[i + 1] = g;
          data[i + 2] = b;
          data[i + 3] = a;
        }
      }
      return { data, width: w, height: h };
    },
  } as CanvasRenderingContext2D;
}

const regionData: RegionRecord = {
  Vassal: { rgb: "10,20,30", name: "Vassal", overlord: "Overlord" },
  Overlord: { rgb: "40,50,60", name: "Overlord" },
};

describe("resolveRegionAtPickPixel", () => {
  it("maps a pick pixel to the resolved visible region", () => {
    const ctx = mockCtx(4, 4, (x, y) =>
      x === 1 && y === 2 ? [10, 20, 30, 255] : [0, 0, 0, 0]
    );
    const rgbToId = { "10,20,30": "Vassal" };
    const picked = resolveRegionAtPickPixel(
      ctx,
      1,
      2,
      rgbToId,
      (_mapType, _mapId, pickId) => ({
        regionId: pickId === "Vassal" ? "Overlord" : pickId,
        imagePath: "/hover.png",
        region: { name: "Overlord" },
      }),
      "nation",
      "main",
      regionData
    );

    expect(picked).toEqual({
      pickId: "Vassal",
      regionId: "Overlord",
      region: { name: "Overlord" },
      imagePath: "/hover.png",
      overlay: undefined,
    });
  });

  it("returns null for an unknown rgb", () => {
    const ctx = mockCtx(2, 2, () => [99, 88, 77, 255]);
    const picked = resolveRegionAtPickPixel(
      ctx,
      0,
      0,
      { "10,20,30": "Vassal" },
      () => ({
        regionId: "Vassal",
        imagePath: null,
        region: { name: "Vassal" },
      }),
      "nation",
      "main",
      regionData
    );
    expect(picked).toBeNull();
  });

  it("returns null when getHoverRegion finds no visible ancestor", () => {
    const ctx = mockCtx(2, 2, () => [10, 20, 30, 255]);
    const picked = resolveRegionAtPickPixel(
      ctx,
      0,
      0,
      { "10,20,30": "Vassal" },
      () => ({
        regionId: null,
        imagePath: null,
        region: null,
      }),
      "nation",
      "main",
      regionData
    );
    expect(picked).toBeNull();
  });

  it("returns null for out-of-bounds pixels", () => {
    const ctx = mockCtx(2, 2, () => [10, 20, 30, 255]);
    const picked = resolveRegionAtPickPixel(
      ctx,
      5,
      5,
      { "10,20,30": "Vassal" },
      () => ({
        regionId: "Vassal",
        imagePath: null,
        region: { name: "Vassal" },
      }),
      "nation",
      "main",
      regionData
    );
    expect(picked).toBeNull();
  });
});
