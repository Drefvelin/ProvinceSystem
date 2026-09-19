import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { createStationTextureAnimation, createStationTextureAtlasFallback } from "./stationTextureAnimation";

describe("station texture animation", () => {
  it("maps the actual Alloy Forge atlas to one full frame and advances on Minecraft ticks", () => {
    const texturePath = resolve(process.cwd(), "public/wiki/textures/stations/alloy-forge.png");
    const png = readFileSync(texturePath);
    const metadata = JSON.parse(readFileSync(`${texturePath}.mcmeta`, "utf8"));
    const width = png.readUInt32BE(16);
    const height = png.readUInt32BE(20);
    expect([width, height]).toEqual([64, 512]);
    const frameAt = createStationTextureAnimation(width, height, metadata);
    expect(frameAt(0)).toEqual({ repeatX: 1, repeatY: 1 / 8, offsetX: 0, offsetY: 7 / 8 });
    expect(frameAt(99)).toEqual(frameAt(0));
    expect(frameAt(100)).toEqual({ repeatX: 1, repeatY: 1 / 8, offsetX: 0, offsetY: 6 / 8 });
    expect(frameAt(799).offsetY).toBe(0);
    expect(frameAt(800)).toEqual(frameAt(0));
    // The base's north face spans v=0..4 in Minecraft's 0..16 grid:
    // it must sample source rows 0..16 of one frame, never all eight frames.
    const first = frameAt(0);
    const imageRow = (v: number) => (1 - ((1 - v / 16) * first.repeatY + first.offsetY)) * height;
    expect([imageRow(0), imageRow(4)]).toEqual([0, 16]);
  });

  it("honors explicit frame ordering and durations", () => {
    const frameAt = createStationTextureAnimation(16, 48, {
      animation: { frametime: 2, frames: [2, { index: 0, time: 4 }] },
    });
    expect(frameAt(99).offsetY).toBe(0);
    expect(frameAt(100).offsetY).toBeCloseTo(2 / 3);
    expect(frameAt(299).offsetY).toBeCloseTo(2 / 3);
    expect(frameAt(300).offsetY).toBe(0);
  });

  it("rejects invalid frame geometry and indices", () => {
    expect(() => createStationTextureAnimation(64, 500, { animation: {} })).toThrow("dimensions");
    expect(() => createStationTextureAnimation(64, 512, { animation: { frames: [8] } })).toThrow("frames");
  });

  it("keeps a proven vertical atlas on its first frame when metadata is unavailable", () => {
    const frameAt = createStationTextureAtlasFallback(64, 512, [64, 64]);
    expect(frameAt?.()).toEqual({ repeatX: 1, repeatY: 1 / 8, offsetX: 0, offsetY: 7 / 8 });
    expect(createStationTextureAtlasFallback(64, 64, [64, 64])).toBeUndefined();
    expect(createStationTextureAtlasFallback(128, 512, [64, 64])).toBeUndefined();
  });
});
