import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { marketBlockRecipe } from "../../wiki/data/market-blocks";
import {
  faceUvCoordinates,
  loadTextureBindings,
  textureMaterialIndices,
} from "./StationModelViewer";

describe("StationModelViewer multi-texture models", () => {
  it("assigns each box face to the material named by its texture reference", () => {
    const faces = {
      east: { uv: [0, 0, 1, 1] as [number, number, number, number], texture: "#coin" },
      west: { uv: [0, 0, 1, 1] as [number, number, number, number], texture: "#wood" },
    };

    expect(textureMaterialIndices(faces, ["wood", "coin"])).toEqual([1, 0, -1, -1, -1, -1]);
  });

  it("settles a failed texture binding without rejecting the model load", async () => {
    const loaded: string[] = [];
    const result = await loadTextureBindings(["wood.png", "missing.png", "coin.png"], async (url) => {
      loaded.push(url);
      if (url === "missing.png") throw new Error("404");
      return { url };
    });

    expect(loaded).toEqual(["wood.png", "missing.png", "coin.png"]);
    expect(result).toEqual([{ url: "wood.png" }, null, { url: "coin.png" }]);
  });

  it.each([
    [0, [[0.125, 0.75], [0.625, 0.75], [0.125, 0.25], [0.625, 0.25]]],
    [90, [[0.125, 0.25], [0.125, 0.75], [0.625, 0.25], [0.625, 0.75]]],
    [180, [[0.625, 0.25], [0.125, 0.25], [0.625, 0.75], [0.125, 0.75]]],
    [270, [[0.625, 0.75], [0.625, 0.25], [0.125, 0.75], [0.125, 0.25]]],
  ] as const)("maps an asymmetric UV rectangle at %i degrees", (rotation, expected) => {
    expect(faceUvCoordinates({
      uv: [2, 4, 10, 12],
      texture: "#crop",
      rotation,
    })).toEqual(expected);
  });

  it("provides an existing authentic asset for every Market Block texture key", () => {
    const model = marketBlockRecipe.output.model;
    expect(model?.textures).toBeDefined();
    const source = JSON.parse(
      readFileSync(join(process.cwd(), "public/wiki/models/market-block.json"), "utf8"),
    ) as { textures: Record<string, string> };
    const referencedKeys = new Set(
      Object.entries(source.textures)
        .filter(([key]) => key !== "particle")
        .map(([key]) => key),
    );

    expect(new Set(Object.keys(model!.textures!))).toEqual(referencedKeys);
    for (const url of Object.values(model!.textures!)) {
      expect(readFileSync(join(process.cwd(), "public", url)).length).toBeGreaterThan(0);
    }
  });
});
