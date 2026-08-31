"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import MapViewer from "../MapViewer";
import MapAccessGate, { type MapAccessGateReason } from "../map/MapAccessGate";
import { MAP_DISPLAY_NAMES, type MapId } from "../map/types";
import { useCharacterSessionToken } from "../../hooks/useCharacterSessionToken";
import {
  MapAccessError,
  mapRequiresAuth,
  staffMapAccessReason,
} from "@/lib/map/api";
import {
  fetchChronicleIndex,
  type ChronicleIndex,
} from "../../lib/map/chronicleData";
import {
  chronicleStudioHref,
  liveMapHref,
} from "../../lib/map/chronicleDayRoute";
import { useChronicleDay } from "../../lib/map/chronicleDayContext";
import { chroniclePanelClass } from "./ChroniclePanels";

const bannerLinkClass =
  "text-xs text-[var(--tfmc-accent)] underline-offset-2 hover:underline";

const shellClass =
  "flex min-h-[calc(100dvh-var(--tfmc-header-h))] flex-col items-center justify-center gap-3 bg-[var(--tfmc-forest-deep)] px-6 text-center";

/**
 * What the chronicle index says about the requested day.
 *
 * `unknown-day` is deliberately separate from `error`: a day that was never
 * captured, or that has since been wiped, is a normal answer and must produce
 * a page that says so. Rendering the map anyway would put an empty world under
 * a real date, which reads as "everything vanished on this day" rather than
 * "we have no record of this day".
 */
type DayStatus =
  | { kind: "loading" }
  | { kind: "gated"; reason: MapAccessGateReason }
  | { kind: "error"; message: string }
  | { kind: "unknown-day" }
  | { kind: "ready"; incomplete: boolean; staleGeometry: boolean };

/**
 * Everything read out of the index is shape-checked before it is iterated.
 * There is no React error boundary anywhere under `app/`, so a `null` or a
 * bare string where an array is expected would blank the entire page instead
 * of one panel.
 *
 * Note `incomplete_days` is an array of `{ day, missing, invalid }` objects,
 * not an array of day strings — see `ChronicleIncompleteDay` in
 * `chronicleData.ts`.
 */
export function describeChronicleDay(
  index: ChronicleIndex,
  day: string
): DayStatus {
  const days = Array.isArray(index.days) ? index.days : [];
  if (!days.includes(day)) return { kind: "unknown-day" };

  const entries = Array.isArray(index.incomplete_days)
    ? index.incomplete_days
    : [];
  const incomplete = entries.some(
    (entry) =>
      typeof entry === "object" &&
      entry !== null &&
      (entry as { day?: unknown }).day === day
  );

  /**
   * Optional field: the backend may not send `stale_geometry_days` at all, and
   * when it does it is a plain array of day strings. Read through a cast
   * rather than the `ChronicleIndex` type so an older backend (field absent)
   * behaves exactly as before.
   */
  const staleDays = (index as { stale_geometry_days?: unknown })
    .stale_geometry_days;
  const staleGeometry = Array.isArray(staleDays) ? staleDays.includes(day) : false;

  return { kind: "ready", incomplete, staleGeometry };
}

/**
 * The date banner, and the single most important element on this page: a
 * screenshot of a stored day must carry its date.
 *
 * Fixed rather than in normal flow because `MapPageLayout` claims the whole
 * viewport below the site header on desktop and hides its own overflow —
 * anything stacked above it would push the map into a scroll region, and a
 * banner that can scroll out of frame is a banner that can be missing from the
 * screenshot. Pinned top-centre, the one strip of the map shell with no
 * floating panel in it (mode selector top-left, nation detail top-right,
 * drill stack and controls along the bottom).
 */
function ChronicleDateBanner({
  mapId,
  day,
  incomplete,
  staleGeometry,
}: {
  mapId: MapId;
  day: string;
  incomplete: boolean;
  staleGeometry: boolean;
}) {
  return (
    <div className="pointer-events-none fixed left-1/2 top-[calc(var(--tfmc-header-h)+0.5rem)] z-30 w-[min(92vw,32rem)] -translate-x-1/2">
      <div
        className={`${chroniclePanelClass} pointer-events-auto px-4 py-2.5 text-center`}
        role="status"
      >
        <p className="text-[0.65rem] font-medium uppercase tracking-widest text-[var(--tfmc-mist)]">
          Stored day — not the live map
        </p>
        <p className="font-[family-name:var(--font-fraunces)] text-2xl font-medium tracking-tight text-[var(--tfmc-cream)]">
          {day}
        </p>
        {incomplete ? (
          <p className="mt-0.5 text-xs leading-snug text-[var(--tfmc-accent)]">
            Some sources were missing when this day was captured, so parts of
            this map may be blank.
          </p>
        ) : null}
        {staleGeometry ? (
          <p className="mt-0.5 text-xs leading-snug text-[var(--tfmc-accent)]">
            The province map has been redrawn since this day was captured, so
            borders may not line up.
          </p>
        ) : null}
        <div className="mt-1 flex flex-wrap items-center justify-center gap-x-4 gap-y-1">
          <Link href={chronicleStudioHref(mapId)} className={bannerLinkClass}>
            &larr; Timelapse
          </Link>
          <Link href={liveMapHref(mapId)} className={bannerLinkClass}>
            Live map &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}

function ChronicleDayFallbackLinks({ mapId }: { mapId: MapId }) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1">
      <Link href={chronicleStudioHref(mapId)} className={bannerLinkClass}>
        &larr; Back to the timelapse
      </Link>
      <Link href={liveMapHref(mapId)} className={bannerLinkClass}>
        Live map &rarr;
      </Link>
    </div>
  );
}

/**
 * One stored day of a map, explorable with the full live-map interaction set.
 *
 * `MapViewer` takes the day as a **prop**, not from `ChronicleDayContext`, so
 * the data flow stays visible at the call site. The provider wrapped around
 * this component by the route is there for anything deeper that needs the day
 * without a prop chain; it is read here and preferred, with the prop as the
 * guaranteed fallback so a missing provider can never quietly hand `null` to
 * `MapViewer` and render the live map under a historical date.
 */
export default function ChronicleDayViewer({
  mapId,
  day,
}: {
  mapId: MapId;
  day: string;
}) {
  const sessionToken = useCharacterSessionToken();
  const authToken = mapRequiresAuth(mapId) ? sessionToken : null;
  const mapDisplayName = MAP_DISPLAY_NAMES[mapId];

  const contextDay = useChronicleDay();
  const activeDay = contextDay ?? day;

  const [status, setStatus] = useState<DayStatus>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    setStatus({ kind: "loading" });

    fetchChronicleIndex(mapId, authToken)
      .then((index) => {
        if (cancelled) return;
        // A 200 whose body is not an object at all would otherwise reach
        // `Array.isArray(index.days)` on a null and throw during the effect.
        if (typeof index !== "object" || index === null) {
          setStatus({
            kind: "error",
            message: "The chronicle index came back in an unreadable shape.",
          });
          return;
        }
        setStatus(describeChronicleDay(index, activeDay));
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof MapAccessError && err.status === 403) {
          setStatus({ kind: "gated", reason: staffMapAccessReason(err) });
          return;
        }
        setStatus({
          kind: "error",
          message:
            err instanceof Error
              ? err.message
              : "Failed to load the chronicle index.",
        });
      });

    return () => {
      cancelled = true;
    };
  }, [mapId, authToken, activeDay]);

  if (status.kind === "gated") {
    return (
      <MapAccessGate reason={status.reason} mapDisplayName={mapDisplayName} />
    );
  }

  if (status.kind === "loading") {
    return (
      <div className={shellClass}>
        <p className="text-lg font-medium text-[var(--tfmc-cream)]">
          Looking up {activeDay} in the chronicle…
        </p>
      </div>
    );
  }

  if (status.kind === "error") {
    return (
      <div className={shellClass}>
        <p className="font-[family-name:var(--font-fraunces)] text-2xl text-[var(--tfmc-cream)]">
          Could not read the chronicle
        </p>
        <p className="max-w-md text-sm leading-snug text-[var(--tfmc-accent)]">
          {status.message}
        </p>
        <ChronicleDayFallbackLinks mapId={mapId} />
      </div>
    );
  }

  if (status.kind === "unknown-day") {
    return (
      <div className={shellClass}>
        <p className="text-xs font-medium uppercase tracking-widest text-[var(--tfmc-mist)]">
          {mapDisplayName} chronicle
        </p>
        <p className="font-[family-name:var(--font-fraunces)] text-2xl text-[var(--tfmc-cream)]">
          No record of {activeDay}
        </p>
        <p className="max-w-md text-sm leading-snug text-[var(--tfmc-stone)]">
          This map has no stored snapshot for that day — it was either never
          captured or has since been removed. Showing nothing is deliberate: an
          empty map under a real date would look like a real historical state.
        </p>
        <ChronicleDayFallbackLinks mapId={mapId} />
      </div>
    );
  }

  return (
    <>
      <ChronicleDateBanner
        mapId={mapId}
        day={activeDay}
        incomplete={status.incomplete}
        staleGeometry={status.staleGeometry}
      />
      <MapViewer mapId={mapId} day={activeDay} />
    </>
  );
}
