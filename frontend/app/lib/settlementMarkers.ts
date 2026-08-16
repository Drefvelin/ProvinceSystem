import type {
  MapMode,
  SettlementMarker,
  SettlementMarkerKind,
  SettlementMarkerSize,
} from "../components/map/types";
import { LABEL_MAP_MODES } from "./mapLabels";

export const SETTLEMENT_LABEL_MIN_SCREEN_PX = 9;
export const SETTLEMENT_MARKER_SMALL_PX = 20;
export const SETTLEMENT_MARKER_LARGE_PX = 32;
export const SETTLEMENT_LABEL_FONT_SMALL = 10;
export const SETTLEMENT_LABEL_FONT_LARGE = 14;
export const SETTLEMENT_LABEL_GAP = 4;
export const SETTLEMENT_LABEL_COLOR = "#000000";

export function isSettlementMapMode(mapType: MapMode): boolean {
  return LABEL_MAP_MODES.has(mapType);
}

export function resolveMarkerImageSrc(
  kind: SettlementMarkerKind | undefined,
  markerSize: SettlementMarkerSize | undefined
): string {
  const large = markerSize === "large";
  if (kind === "faction_capital") {
    return large ? "/capital_settlement_large.png" : "/capital_settlement_small.png";
  }
  return large ? "/settlement_large.png" : "/settlement_small.png";
}

export function markerDimensions(markerSize: SettlementMarkerSize | undefined): {
  size: number;
  fontSize: number;
} {
  if (markerSize === "large") {
    return {
      size: SETTLEMENT_MARKER_LARGE_PX,
      fontSize: SETTLEMENT_LABEL_FONT_LARGE,
    };
  }
  return {
    size: SETTLEMENT_MARKER_SMALL_PX,
    fontSize: SETTLEMENT_LABEL_FONT_SMALL,
  };
}

export function shouldShowSettlementMarker(
  fontSize: number,
  displayScale: number
): boolean {
  if (displayScale <= 0 || fontSize <= 0) return false;
  return fontSize * displayScale >= SETTLEMENT_LABEL_MIN_SCREEN_PX;
}

export function filterPlacedSettlements(
  settlements: SettlementMarker[]
): SettlementMarker[] {
  return settlements.filter(
    (s) =>
      typeof s.map_x === "number" &&
      Number.isFinite(s.map_x) &&
      typeof s.map_y === "number" &&
      Number.isFinite(s.map_y)
  );
}

export function settlementMarkerLayout(
  mapX: number,
  mapY: number,
  markerSize: SettlementMarkerSize | undefined
): {
  imageX: number;
  imageY: number;
  size: number;
  fontSize: number;
  textY: number;
} {
  const { size, fontSize } = markerDimensions(markerSize);
  return {
    imageX: mapX - size / 2,
    imageY: mapY - size,
    size,
    fontSize,
    textY: mapY + SETTLEMENT_LABEL_GAP,
  };
}
