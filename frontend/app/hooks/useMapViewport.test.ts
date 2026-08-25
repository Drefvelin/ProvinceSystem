import { describe, expect, it } from "vitest";

import { readViewportSize } from "./useMapViewport";

describe("readViewportSize", () => {
  it("returns width and height from getBoundingClientRect", () => {
    const element = {
      getBoundingClientRect: () => ({
        width: 1200,
        height: 800,
        left: 0,
        top: 0,
        right: 1200,
        bottom: 800,
        x: 0,
        y: 0,
        toJSON: () => ({}),
      }),
    } as HTMLElement;

    expect(readViewportSize(element)).toEqual({ w: 1200, h: 800 });
  });
});
