import NationDetailContent from "./NationDetailContent";
import type { MapId, MapMode, RegionInfo, RegionRecord } from "./types";

const panelClass =
  "rounded-lg border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-moss)_35%,var(--tfmc-forest-deep))] shadow-lg overflow-hidden transition-all duration-300";

type NationDetailPanelProps = {
  mapId: MapId;
  mapType: MapMode;
  regionInfo: RegionInfo | null;
  regionData: RegionRecord | null;
  sessionToken?: string | null;
};

export default function NationDetailPanel({
  mapId,
  mapType,
  regionInfo,
  regionData,
  sessionToken,
}: NationDetailPanelProps) {
  const showPanel =
    regionInfo && mapType !== "terrain" && mapType !== "fertility";

  return (
    <div
      className={`${panelClass} ${
        showPanel ? "max-h-[600px] opacity-100 p-4" : "max-h-0 opacity-0 p-0 border-0"
      }`}
    >
      {showPanel && regionInfo && (
        <NationDetailContent
          mapId={mapId}
          mapType={mapType}
          regionInfo={regionInfo}
          regionData={regionData}
          sessionToken={sessionToken}
        />
      )}
    </div>
  );
}
