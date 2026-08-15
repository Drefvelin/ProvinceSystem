import { describe, expect, it } from "vitest";

import {
  LABEL_MIN_INSET_PX,
  LABEL_GLYPH_WIDTH_EM,
  buildComponentMask,
  corridorClear,
  distanceTransform,
  findLabelAnchor,
  insetLabelEndpoints,
  isLabelCorridorWaterCell,
  labelCorridorMargin,
  parseProvinceLabelGrid,
  tryRadialSegment,
  type ProvinceLabelGrid,
} from "./labelBlobGeometry";

function segmentPixelLength(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number {
  return Math.hypot(x2 - x1, y2 - y1);
}

function makeGrid(
  width: number,
  height: number,
  cells: number[],
  mapWidth = width * 10,
  mapHeight = height * 10
): ProvinceLabelGrid {
  return {
    mapWidth,
    mapHeight,
    gridWidth: width,
    gridHeight: height,
    cells: new Uint16Array(cells),
    scaleX: mapWidth / width,
    scaleY: mapHeight / height,
  };
}

describe("labelCorridorMargin", () => {
  it("uses at least LABEL_MIN_INSET_PX", () => {
    expect(labelCorridorMargin(100, 10)).toBeGreaterThanOrEqual(LABEL_MIN_INSET_PX);
  });

  it("grows with segment length and font size", () => {
    const small = labelCorridorMargin(200, 20);
    const large = labelCorridorMargin(600, 40);
    expect(large).toBeGreaterThan(small);
  });
});

describe("distanceTransform", () => {
  it("gives higher clearance in the interior of a solid block", () => {
    const grid = makeGrid(
      5,
      5,
      [
        0, 0, 0, 0, 0,
        0, 1, 1, 1, 0,
        0, 1, 1, 1, 0,
        0, 1, 1, 1, 0,
        0, 0, 0, 0, 0,
      ]
    );
    const mask = buildComponentMask(grid, [1]);
    const dist = distanceTransform(mask, grid);
    const center = dist[2 * grid.gridWidth + 2];
    const edge = dist[1 * grid.gridWidth + 2];
    expect(center).toBeGreaterThan(edge);
  });
});

describe("corridorClear", () => {
  it("rejects a chord that samples outside the blob", () => {
    const grid = makeGrid(
      7,
      3,
      [
        0, 0, 0, 0, 0, 0, 0,
        0, 1, 1, 1, 1, 1, 0,
        0, 0, 0, 0, 0, 0, 0,
      ],
      70,
      30
    );
    const mask = buildComponentMask(grid, [1]);
    const dist = distanceTransform(mask, grid);
    const len = 60;
    const fontSize = Math.round(len / (2 * LABEL_GLYPH_WIDTH_EM));

    expect(
      corridorClear(5, 15, 65, 15, labelCorridorMargin(len, fontSize), grid, dist)
    ).toBe(false);
    expect(corridorClear(15, 15, 55, 15, 10, grid, dist)).toBe(true);
  });

  it("allows a chord that crosses sea gaps between the same province", () => {
    const grid = makeGrid(
      7,
      3,
      [
        0, 1, 1, 0, 0, 1, 0,
        0, 1, 1, 0, 0, 1, 0,
        0, 0, 0, 0, 0, 0, 0,
      ],
      70,
      30
    );
    expect(isLabelCorridorWaterCell(grid, 3)).toBe(true);
    const mask = buildComponentMask(grid, [1]);
    const dist = distanceTransform(mask, grid);

    expect(corridorClear(15, 15, 55, 15, 10, grid, dist)).toBe(true);
  });

  it("still rejects a chord that crosses foreign land", () => {
    const grid = makeGrid(
      7,
      3,
      [
        0, 1, 1, 2, 2, 1, 0,
        0, 1, 1, 2, 2, 1, 0,
        0, 0, 0, 0, 0, 0, 0,
      ],
      70,
      30
    );
    const mask = buildComponentMask(grid, [1]);
    const dist = distanceTransform(mask, grid);
    const len = 50;
    const fontSize = Math.round(len / (2 * LABEL_GLYPH_WIDTH_EM));

    expect(
      corridorClear(15, 15, 55, 15, labelCorridorMargin(len, fontSize), grid, dist)
    ).toBe(false);
  });
});

describe("insetLabelEndpoints", () => {
  it("returns a short radial label on a tiny square blob", () => {
    const grid = makeGrid(3, 3, [1, 1, 1, 1, 1, 1, 1, 1, 1], 30, 30);
    const seed = { x1: 15, y1: 15, x2: 15, y2: 15 };
    const endpoints = insetLabelEndpoints([1], "Tiny", grid, seed);
    expect(endpoints).not.toBeNull();
    expect(
      segmentPixelLength(endpoints!.x1, endpoints!.y1, endpoints!.x2, endpoints!.y2)
    ).toBeGreaterThan(0);
  });

  it("uses radial fallback for a single-province strip", () => {
    const grid = makeGrid(
      7,
      3,
      [
        0, 1, 1, 1, 1, 1, 0,
        0, 1, 1, 1, 1, 1, 0,
        0, 0, 0, 0, 0, 0, 0,
      ],
      70,
      30
    );
    const seed = { x1: 35, y1: 15, x2: 35, y2: 15 };
    const endpoints = insetLabelEndpoints([1], "Realm", grid, seed);
    expect(endpoints).not.toBeNull();
    expect(endpoints!.x2 - endpoints!.x1).toBeGreaterThan(20);
  });

  it("can span across water when seed endpoints bridge two land masses", () => {
    const grid = makeGrid(
      7,
      3,
      [
        0, 1, 1, 0, 0, 1, 0,
        0, 1, 1, 0, 0, 1, 0,
        0, 0, 0, 0, 0, 0, 0,
      ],
      70,
      30
    );
    const seed = { x1: 15, y1: 15, x2: 55, y2: 15 };
    const endpoints = insetLabelEndpoints([1], "Realm", grid, seed);
    expect(endpoints).not.toBeNull();
    expect(endpoints!.x2 - endpoints!.x1).toBeGreaterThan(30);
  });
});

describe("tryRadialSegment", () => {
  it("places a vertical label on a narrow strip", () => {
    const grid = makeGrid(
      3,
      7,
      [
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
        0, 0, 0,
      ],
      30,
      70
    );
    const mask = buildComponentMask(grid, [1]);
    const dist = distanceTransform(mask, grid);
    const anchor = findLabelAnchor(mask, dist, grid);
    expect(anchor).not.toBeNull();

    const endpoints = tryRadialSegment(mask, dist, grid, "Isle", 1, anchor!);
    expect(endpoints).not.toBeNull();
    expect(
      Math.abs(endpoints!.y2 - endpoints!.y1)
    ).toBeGreaterThan(Math.abs(endpoints!.x2 - endpoints!.x1));
  });

  it("rejects segments that would cross foreign land", () => {
    const grid = makeGrid(
      7,
      3,
      [
        0, 1, 1, 2, 2, 1, 0,
        0, 1, 1, 2, 2, 1, 0,
        0, 0, 0, 0, 0, 0, 0,
      ],
      70,
      30
    );
    const mask = buildComponentMask(grid, [1]);
    const dist = distanceTransform(mask, grid);
    const anchor = findLabelAnchor(mask, dist, grid)!;
    const endpoints = tryRadialSegment(mask, dist, grid, "Realm", 1, anchor);
    expect(endpoints).not.toBeNull();
    expect(
      corridorClear(
        endpoints!.x1,
        endpoints!.y1,
        endpoints!.x2,
        endpoints!.y2,
        10,
        grid,
        dist
      )
    ).toBe(true);
    expect(endpoints!.x2 - endpoints!.x1).toBeLessThan(35);
  });
});

describe("parseProvinceLabelGrid", () => {
  it("parses uint16 cells from a binary buffer", () => {
    const buffer = new ArrayBuffer(8);
    const view = new DataView(buffer);
    view.setUint16(0, 5, true);
    view.setUint16(2, 9, true);
    view.setUint16(4, 0, true);
    view.setUint16(6, 12, true);

    const grid = parseProvinceLabelGrid(
      { mapWidth: 40, mapHeight: 20, gridWidth: 2, gridHeight: 2 },
      buffer
    );

    expect(Array.from(grid.cells)).toEqual([5, 9, 0, 12]);
    expect(grid.scaleX).toBe(20);
    expect(grid.scaleY).toBe(10);
  });
});
