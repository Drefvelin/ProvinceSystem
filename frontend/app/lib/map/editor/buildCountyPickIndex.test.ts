import { describe, expect, it } from "vitest";

import {
  buildRgbToCountyId,
  pickCountyIdAt,
} from "./buildCountyPickIndex";

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

describe("buildCountyPickIndex", () => {
  it("buildRgbToCountyId maps county rgb to ids", () => {
    const map = buildRgbToCountyId({
      COUNTY_1: { name: "A", rgb: "58,132,60" },
      COUNTY_2: { name: "B", rgb: "40,123,42" },
    });
    expect(map["58,132,60"]).toBe("COUNTY_1");
    expect(map["40,123,42"]).toBe("COUNTY_2");
  });

  it("pickCountyIdAt resolves county from pixel", () => {
    const imageData = makeImageData(2, 1, [
      [58, 132, 60],
      [40, 123, 42],
    ]);
    const rgbToCountyId = {
      "58,132,60": "COUNTY_1",
      "40,123,42": "COUNTY_2",
    };
    expect(pickCountyIdAt(imageData, 0, 0, rgbToCountyId)).toBe("COUNTY_1");
    expect(pickCountyIdAt(imageData, 1, 0, rgbToCountyId)).toBe("COUNTY_2");
    expect(pickCountyIdAt(imageData, 5, 0, rgbToCountyId)).toBeNull();
  });
});
