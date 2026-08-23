import { describe, expect, it } from "vitest";

import { buildProvinceToCountyId } from "./countyAssignment";
import {
  buildProvinceIndexFromGrid,
  buildProvinceIndexFromImageData,
  deserializeProvinceIdGrid,
} from "./buildProvinceIndex";

function makeImageData(
  width: number,
  height: number,
  pixels: Array<[number, number, number]>
): ImageData {
  const data = new Uint8ClampedArray(width * height * 4);
  for (let i = 0; i < pixels.length; i++) {
    const [r, g, b] = pixels[i]!;
    const offset = i * 4;
    data[offset] = r;
    data[offset + 1] = g;
    data[offset + 2] = b;
    data[offset + 3] = 255;
  }
  return { width, height, data } as ImageData;
}

describe("buildProvinceIndexFromImageData", () => {
  it("maps pick pixels to province ids", () => {
    const provinces = [
      { id: 1, rgb: "58,132,60" },
      { id: 2, rgb: "40,123,42" },
    ];
    const imageData = makeImageData(2, 2, [
      [58, 132, 60],
      [40, 123, 42],
      [58, 132, 60],
      [40, 123, 42],
    ]);

    const index = buildProvinceIndexFromImageData(provinces, imageData);

    expect(index.width).toBe(2);
    expect(index.height).toBe(2);
    expect(index.rgbToProvinceId["58,132,60"]).toBe(1);
    expect(index.rgbToProvinceId["40,123,42"]).toBe(2);
    expect(index.provinceMap[0]).toBe(1);
    expect(index.provinceMap[1]).toBe(2);
    expect(index.provinceMap[2]).toBe(1);
    expect(index.provinceMap[3]).toBe(2);
  });

  it("leaves unknown pixels as -1", () => {
    const provinces = [{ id: 1, rgb: "10,20,30" }];
    const imageData = makeImageData(2, 2, [
      [10, 20, 30],
      [0, 0, 0],
      [0, 0, 0],
      [0, 0, 0],
    ]);

    const index = buildProvinceIndexFromImageData(provinces, imageData);
    expect(index.provinceMap[0]).toBe(1);
    expect(index.provinceMap[1]).toBe(-1);
  });
});

describe("deserializeProvinceIdGrid", () => {
  it("unpacks width height and row-major ids", () => {
    const header = new ArrayBuffer(8);
    const headerView = new DataView(header);
    headerView.setInt32(0, 2, true);
    headerView.setInt32(4, 2, true);

    const body = new Uint16Array([1, 2, 1, 2]);
    const bytes = new Uint8Array(8 + body.byteLength);
    bytes.set(new Uint8Array(header), 0);
    bytes.set(new Uint8Array(body.buffer), 8);

    const { width, height, ids } = deserializeProvinceIdGrid(bytes.buffer);
    expect(width).toBe(2);
    expect(height).toBe(2);
    expect(Array.from(ids)).toEqual([1, 2, 1, 2]);
  });
});

describe("buildProvinceIndexFromGrid", () => {
  it("matches buildProvinceIndexFromImageData on a 2x2 fixture", () => {
    const provinces = [
      { id: 1, rgb: "58,132,60" },
      { id: 2, rgb: "40,123,42" },
    ];
    const imageData = makeImageData(2, 2, [
      [58, 132, 60],
      [40, 123, 42],
      [58, 132, 60],
      [40, 123, 42],
    ]);

    const fromImage = buildProvinceIndexFromImageData(provinces, imageData);

    const header = new ArrayBuffer(8);
    const headerView = new DataView(header);
    headerView.setInt32(0, 2, true);
    headerView.setInt32(4, 2, true);
    const packed = new Uint16Array(fromImage.provinceMap.length);
    for (let i = 0; i < fromImage.provinceMap.length; i++) {
      const id = fromImage.provinceMap[i]!;
      packed[i] = id === -1 ? 0 : id;
    }
    const bytes = new Uint8Array(8 + packed.byteLength);
    bytes.set(new Uint8Array(header), 0);
    bytes.set(new Uint8Array(packed.buffer), 8);

    const { width, height, ids } = deserializeProvinceIdGrid(bytes.buffer);
    const fromGrid = buildProvinceIndexFromGrid(provinces, width, height, ids);

    expect(fromGrid.width).toBe(fromImage.width);
    expect(fromGrid.height).toBe(fromImage.height);
    expect(fromGrid.rgbToProvinceId).toEqual(fromImage.rgbToProvinceId);
    expect(fromGrid.provinceToRgb).toEqual(fromImage.provinceToRgb);
    expect(Array.from(fromGrid.provinceMap)).toEqual(
      Array.from(fromImage.provinceMap)
    );
  });
});

describe("buildProvinceToCountyId", () => {
  it("maps province ids to county ids", () => {
    const map = buildProvinceToCountyId({
      COUNTY_1: { provinces: [1, 2] },
      COUNTY_2: { provinces: [3] },
    });
    expect(map.get(1)).toBe("COUNTY_1");
    expect(map.get(3)).toBe("COUNTY_2");
    expect(map.get(99)).toBeUndefined();
  });
});
