import type {
  MapMode,
  SettlementMarker,
  SettlementMarkerKind,
  SettlementMarkerSize,
} from "../components/map/types";
import {
  cleanRegionName,
  isNationLabelVisible,
  type LabelMapObject,
} from "./mapLabels";
import {
  MARKER_LABEL_COLOR,
  MARKER_LABEL_FONT_LARGE,
  MARKER_LABEL_FONT_SMALL,
  MARKER_LABEL_GAP,
  MARKER_LABEL_MIN_SCREEN_PX,
  MARKER_LARGE_PX,
  MARKER_SMALL_PX,
  isMarkerMapMode,
  markerDimensions,
  markerLayout,
  resolveMarkerImageSrc,
  type MapMarker,
} from "./mapMarkers";

export const SETTLEMENT_LABEL_MIN_SCREEN_PX = MARKER_LABEL_MIN_SCREEN_PX;
export const SETTLEMENT_MARKER_SMALL_PX = MARKER_SMALL_PX;
export const SETTLEMENT_MARKER_LARGE_PX = MARKER_LARGE_PX;
export const SETTLEMENT_LABEL_FONT_SMALL = MARKER_LABEL_FONT_SMALL;
export const SETTLEMENT_LABEL_FONT_LARGE = MARKER_LABEL_FONT_LARGE;
export const SETTLEMENT_LABEL_GAP = MARKER_LABEL_GAP;
export const SETTLEMENT_LABEL_COLOR = MARKER_LABEL_COLOR;

export function isSettlementMapMode(mapType: MapMode): boolean {
  return isMarkerMapMode(mapType);
}

export { markerDimensions, resolveMarkerImageSrc };

export function shouldShowSettlementMarker(
  fontSize: number,
  displayScale: number
): boolean {
  if (displayScale <= 0 || fontSize <= 0) return false;
  return fontSize * displayScale >= MARKER_LABEL_MIN_SCREEN_PX;
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

export function visibleSettlementKind(
  kind: SettlementMarkerKind | undefined,
  factionId: string | undefined,
  mapObjects: LabelMapObject[]
): SettlementMarkerKind {
  const resolved = kind ?? "settlement";
  if (resolved === "settlement") {
    return "settlement";
  }
  if (!factionId) {
    return resolved;
  }
  if (!isNationLabelVisible(factionId, mapObjects)) {
    return "settlement";
  }
  return resolved;
}

export function settlementToMapMarker(settlement: SettlementMarker): MapMarker {
  const displayName = cleanRegionName(settlement.name);
  return {
    id: settlement.id,
    kind: settlement.kind ?? "settlement",
    markerSize: settlement.marker_size,
    mapX: settlement.map_x!,
    mapY: settlement.map_y!,
    label: displayName,
    title:
      settlement.population != null
        ? `${displayName} (${settlement.population})`
        : displayName,
  };
}

export function settlementMarkerLayout(
  mapX: number,
  mapY: number,
  markerSize: SettlementMarkerSize | undefined
) {
  return markerLayout(mapX, mapY, markerSize);
}
