import { memo, useMemo } from "react";

import type { WarExport } from "./types";
import type { ProvinceCentroids } from "../../lib/mapLabels";
import {
  buildWarCampaignPathD,
  warLineStrokeStyle,
} from "../../lib/warCampaignLine";

type WarCampaignLineLayerProps = {
  wars: WarExport[];
  centroids?: ProvinceCentroids | null;
  mapW: number;
  mapH: number;
};

type WarLineRender = {
  warId: string;
  pathD: string;
  style: ReturnType<typeof warLineStrokeStyle>;
};

export default memo(WarCampaignLineLayer);

function WarCampaignLineLayer({
  wars,
  centroids = null,
  mapW,
  mapH,
}: WarCampaignLineLayerProps) {
  const lines = useMemo(() => {
    const rendered: WarLineRender[] = [];
    for (const war of wars) {
      const pathD = buildWarCampaignPathD(war, centroids);
      if (!pathD) continue;
      rendered.push({
        warId: war.id,
        pathD,
        style: warLineStrokeStyle(war.id, wars.length),
      });
    }
    return rendered;
  }, [wars, centroids]);

  if (!lines.length || !mapW || !mapH) {
    return null;
  }

  return (
    <svg
      className="pointer-events-none absolute left-0 top-0 z-[13] h-full w-full"
      viewBox={`0 0 ${mapW} ${mapH}`}
      preserveAspectRatio="xMidYMid meet"
      aria-hidden
    >
      {lines.map((line) => (
        <g
          key={line.warId}
          style={{ opacity: line.style.opacity }}
        >
          <path
            d={line.pathD}
            fill="none"
            stroke={line.style.borderColor}
            strokeWidth={line.style.borderWidth}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d={line.pathD}
            fill="none"
            stroke={line.style.dashColor}
            strokeWidth={line.style.dashWidth}
            strokeDasharray={line.style.dashArray}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>
      ))}
    </svg>
  );
}
