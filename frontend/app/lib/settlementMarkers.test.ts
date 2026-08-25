import { describe, expect, it } from "vitest";

import {
  SETTLEMENT_LABEL_FONT_LARGE,
  SETTLEMENT_LABEL_MIN_SCREEN_PX,
  filterPlacedSettlements,
  isSettlementMapMode,
  markerDimensions,
  resolveMarkerImageSrc,
  shouldShowSettlementMarker,
} from "./settlementMarkers";

describe("settlementMarkers", () => {
  it("resolveMarkerImageSrc picks capital and normal assets", () => {
    expect(resolveMarkerImageSrc("faction_capital", "small")).toBe(
      "/capital_settlement_small.png"
    );
    expect(resolveMarkerImageSrc("faction_capital", "large")).toBe(
      "/capital_settlement_large.png"
    );
    expect(resolveMarkerImageSrc("settlement", "small")).toBe(
      "/settlement_small.png"
    );
    expect(resolveMarkerImageSrc("settlement", "large")).toBe(
      "/settlement_large.png"
    );
    expect(resolveMarkerImageSrc(undefined, undefined)).toBe(
      "/settlement_small.png"
    );
  });

  it("markerDimensions returns tier sizes", () => {
    expect(markerDimensions("large").fontSize).toBe(SETTLEMENT_LABEL_FONT_LARGE);
    expect(markerDimensions("small").size).toBeLessThan(
      markerDimensions("large").size
    );
  });

  it("shouldShowSettlementMarker gates on screen font size", () => {
    const fontSize = 10;
    const below = SETTLEMENT_LABEL_MIN_SCREEN_PX / fontSize - 0.01;
    const above = SETTLEMENT_LABEL_MIN_SCREEN_PX / fontSize + 0.01;
    expect(shouldShowSettlementMarker(fontSize, below)).toBe(false);
    expect(shouldShowSettlementMarker(fontSize, above)).toBe(true);
  });

  it("isSettlementMapMode matches political label modes", () => {
    expect(isSettlementMapMode("nation")).toBe(true);
    expect(isSettlementMapMode("trade")).toBe(true);
    expect(isSettlementMapMode("terrain")).toBe(false);
    expect(isSettlementMapMode("fertility")).toBe(false);
  });

  it("filterPlacedSettlements keeps only finite map coords", () => {
    const out = filterPlacedSettlements([
      { id: "a", name: "A", map_x: 1, map_y: 2 },
      { id: "b", name: "B", map_x: undefined, map_y: 2 },
      { id: "c", name: "C" },
    ]);
    expect(out).toHaveLength(1);
    expect(out[0].id).toBe("a");
  });
});
