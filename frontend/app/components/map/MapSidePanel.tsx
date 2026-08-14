import NationDetailPanel from "./NationDetailPanel";
import type { DrillLayer } from "./drillUtils";
import type { MapId, MapMode, RegionInfo, RegionRecord } from "./types";

const panelClass =
  "rounded-lg border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-moss)_35%,var(--tfmc-forest-deep))] p-4 shadow-lg";

type MapDrillStackBarProps = {
  drillStack: DrillLayer[];
  onSelectLayer: (index: number) => void;
  onResetDrill: () => void;
};

function nationRgbColor(rgb: string): string {
  return `rgb(${rgb})`;
}

export function MapDrillStackBar({
  drillStack,
  onSelectLayer,
  onResetDrill,
}: MapDrillStackBarProps) {
  if (drillStack.length === 0) return null;

  return (
    <div className={`${panelClass} flex flex-col gap-3 sm:flex-row sm:items-center`}>
      <div className="min-w-0 flex-1">
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--tfmc-stone)] sm:mb-3 sm:text-sm">
          Active layers
        </h3>
        <div className="flex gap-2 overflow-x-auto pb-1 sm:flex-wrap sm:overflow-visible sm:pb-0">
          {drillStack.map((layer, index) => {
            const isCurrent = index === drillStack.length - 1;

            return (
              <button
                key={layer.regionId}
                type="button"
                onClick={() => onSelectLayer(index)}
                aria-current={isCurrent ? "step" : undefined}
                className={`inline-flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition-colors ${
                  isCurrent
                    ? "border-[color-mix(in_srgb,var(--tfmc-cream)_22%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_70%,transparent)] text-[var(--tfmc-stone)]"
                    : "border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_55%,transparent)] text-[var(--tfmc-stone)] hover:border-[color-mix(in_srgb,var(--tfmc-cream)_28%,transparent)] hover:bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_80%,transparent)]"
                }`}
              >
                <span
                  className="inline-block h-2 w-2 rounded-full ring-1 ring-[color-mix(in_srgb,var(--tfmc-cream)_20%,transparent)]"
                  style={{ backgroundColor: nationRgbColor(layer.rgb) }}
                />
                <span className="font-medium text-[var(--tfmc-cream)]">
                  {layer.name}
                </span>
              </button>
            );
          })}
        </div>
      </div>
      <button
        type="button"
        onClick={onResetDrill}
        className="inline-flex min-h-11 shrink-0 items-center justify-center rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-cream)_90%,transparent)] px-4 text-sm font-medium text-[var(--tfmc-forest-deep)] transition-colors hover:bg-[var(--tfmc-cream)] sm:self-end"
      >
        Reset view
      </button>
    </div>
  );
}

type MapDesktopSidePanelProps = {
  mapId: MapId;
  mapType: MapMode;
  regionInfo: RegionInfo | null;
  regionData: RegionRecord | null;
};

export function MapDesktopSidePanel({
  mapId,
  mapType,
  regionInfo,
  regionData,
}: MapDesktopSidePanelProps) {
  return (
    <NationDetailPanel
      mapId={mapId}
      mapType={mapType}
      regionInfo={regionInfo}
      regionData={regionData}
    />
  );
}
