import MapAuthImage from "./MapAuthImage";
import type { MapId, MapMode, RegionInfo, RegionRecord } from "./types";

type NationDetailContentProps = {
  mapId: MapId;
  mapType: MapMode;
  regionInfo: RegionInfo;
  regionData: RegionRecord | null;
  sessionToken?: string | null;
};

export default function NationDetailContent({
  mapId,
  mapType,
  regionInfo,
  regionData,
  sessionToken,
}: NationDetailContentProps) {
  return (
    <div className="flex gap-4">
      <div className="min-w-0 flex-1">
        <h2 className="font-[family-name:var(--font-fraunces)] text-xl font-medium text-[var(--tfmc-cream)]">
          {regionInfo.title}
        </h2>
        <p className="mt-1 text-sm text-[var(--tfmc-stone)]">
          <strong className="text-[var(--tfmc-mist)]">
            {mapType === "trade" ? "Type:" : "Tier:"}
          </strong>{" "}
          {regionInfo.tier}
        </p>

        {mapType === "nation" && (
          <>
            <p className="mt-1 text-sm text-[var(--tfmc-stone)]">
              <strong className="text-[var(--tfmc-mist)]">Type:</strong>{" "}
              {regionInfo.overlord
                ? `Subject of ${regionInfo.overlord}`
                : "Independent"}
            </p>
            <p className="mt-1 text-sm text-[var(--tfmc-stone)]">
              <strong className="text-[var(--tfmc-mist)]">Realm size:</strong>{" "}
              {regionInfo.subject_size > 0
                ? `${regionInfo.size} (${regionInfo.subject_size} from subjects)`
                : regionInfo.size}
            </p>
          </>
        )}

        {regionInfo.subjects.length > 0 && (
          <div className="mt-3">
            <p className="text-sm font-semibold text-[var(--tfmc-mist)]">
              Subjects
            </p>
            <ul className="mt-1 list-inside list-disc text-sm text-[var(--tfmc-stone)]">
              {regionInfo.subjects.map((subjectId) => (
                <li key={subjectId}>
                  {regionData?.[subjectId]?.name || subjectId}
                </li>
              ))}
            </ul>
          </div>
        )}

        <p className="mt-3 text-sm text-[var(--tfmc-stone)]">
          {regionInfo.description}
        </p>
      </div>

      {regionInfo.banner && (
        <div className="flex shrink-0 flex-col items-center">
          <MapAuthImage
            mapId={mapId}
            // `banner` is a raw field out of region data, which on a stored
            // day is an immutable file this app did not produce. Unencoded,
            // `"../../.."` walks to a different backend path and `"x?next=/e"`
            // smuggles a query and drops the `.png`.
            path={`/${mapId}/banners/${mapType}/${encodeURIComponent(
              regionInfo.banner
            )}.png`}
            sessionToken={sessionToken}
            alt={`${regionInfo.title} banner`}
            className="image-render-pixel w-24 rounded border border-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)] shadow-md"
          />
          <p className="mt-1 text-center text-xs text-[var(--tfmc-mist)]">
            Official flag
          </p>
        </div>
      )}
    </div>
  );
}
