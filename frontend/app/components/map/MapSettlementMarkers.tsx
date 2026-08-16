import { memo } from "react";

import type { MapMode, SettlementMarker } from "./types";
import {
  SETTLEMENT_LABEL_COLOR,
  isSettlementMapMode,
  resolveMarkerImageSrc,
  settlementMarkerLayout,
  shouldShowSettlementMarker,
} from "../../lib/settlementMarkers";

type MapSettlementMarkersProps = {
  settlements: SettlementMarker[];
  mapW: number;
  mapH: number;
  displayScale: number;
  mapType: MapMode;
};

export default memo(MapSettlementMarkers);

function MapSettlementMarkers({
  settlements,
  mapW,
  mapH,
  displayScale,
  mapType,
}: MapSettlementMarkersProps) {
  if (
    !isSettlementMapMode(mapType) ||
    !settlements.length ||
    !mapW ||
    !mapH ||
    displayScale <= 0
  ) {
    return null;
  }

  return (
    <svg
      className="pointer-events-none absolute left-0 top-0 z-[16] h-full w-full"
      viewBox={`0 0 ${mapW} ${mapH}`}
      preserveAspectRatio="xMidYMid meet"
      aria-hidden
    >
      {settlements.map((settlement) => {
        const mapX = settlement.map_x!;
        const mapY = settlement.map_y!;
        const { imageX, imageY, size, fontSize, textY } = settlementMarkerLayout(
          mapX,
          mapY,
          settlement.marker_size
        );

        if (!shouldShowSettlementMarker(fontSize, displayScale)) {
          return null;
        }

        const src = resolveMarkerImageSrc(
          settlement.kind,
          settlement.marker_size
        );
        const title =
          settlement.population != null
            ? `${settlement.name} (${settlement.population})`
            : settlement.name;

        return (
          <g key={settlement.id}>
            <image
              href={src}
              x={imageX}
              y={imageY}
              width={size}
              height={size}
            >
              <title>{title}</title>
            </image>
            <text
              x={mapX}
              y={textY}
              textAnchor="middle"
              dominantBaseline="hanging"
              fontSize={fontSize}
              fill={SETTLEMENT_LABEL_COLOR}
              style={{
                fontFamily: "var(--font-fraunces), serif",
                fontWeight: 500,
              }}
            >
              <title>{title}</title>
              {settlement.name}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
