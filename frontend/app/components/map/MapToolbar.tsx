import type { MapId, MapMode } from "./types";

const panelClass =
  "rounded-lg border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-moss)_35%,var(--tfmc-forest-deep))] shadow-lg";

type MapToolbarProps = {
  mapId: MapId;
  mapType: MapMode;
  onMapTypeChange: (mode: MapMode) => void;
  variant?: "sidebar" | "mobile" | "bar";
};

export default function MapToolbar({
  mapId,
  mapType,
  onMapTypeChange,
  variant = "sidebar",
}: MapToolbarProps) {
  const isMobile = variant === "mobile";
  const isBar = variant === "bar";

  return (
    <div
      className={`${panelClass} ${
        isMobile
          ? "sticky top-[calc(var(--tfmc-header-h)+0.5rem)] z-20 p-3"
          : isBar
            ? "p-3 sm:p-4"
            : "p-4"
      }`}
    >
      <h2
        className={`font-semibold uppercase tracking-wide text-[var(--tfmc-stone)] ${
          isMobile || isBar ? "mb-2 text-xs sm:text-sm" : "mb-3 text-sm"
        }`}
      >
        Map mode
      </h2>
      <select
        value={mapType}
        onChange={(e) => onMapTypeChange(e.target.value as MapMode)}
        className={`w-full rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-cream)_92%,transparent)] px-3 text-[var(--tfmc-forest-deep)] focus:outline-none focus:ring-2 focus:ring-[var(--tfmc-accent)] ${
          isMobile || isBar
            ? "min-h-11 text-base sm:text-sm sm:py-2"
            : "py-2 text-sm"
        }`}
      >
        <option value="nation">Nation Map</option>
        <option value="county">County Map</option>
        <option value="duchy">Duchy Map</option>
        <option value="kingdom">Kingdom Map</option>
        <option value="empire">Empire Map</option>
        {(mapId === "main" || mapId === "dev") && (
          <>
            <option value="terrain">Terrain</option>
            <option value="fertility">Fertility</option>
            <option value="trade">Trade</option>
            <option value="prosperity">Prosperity</option>
            <option value="infestation">Infestation</option>
          </>
        )}
      </select>
    </div>
  );
}
