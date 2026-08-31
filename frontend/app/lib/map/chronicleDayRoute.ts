import type { MapId } from "@/app/components/map/types";

/**
 * Exactly `YYYY-MM-DD`, anchored at both ends.
 *
 * The `day` route segment arrives from the URL bar, so it is attacker-supplied
 * text that ends up in a request path and, on the backend, in a
 * filesystem-backed lookup. This regex is *defence in depth*, not the only
 * guard: the backend is independently hardened against traversal, and every
 * helper in `chronicleData.ts` already runs the day through
 * `encodeURIComponent` before it reaches a URL. It exists so that a nonsense
 * segment produces a plain "not a valid date" page instead of a 404 from three
 * layers down, and so nothing arbitrary is ever handed to the data layer.
 *
 * Deliberately a *shape* check only. `2026-02-31` matches and is a real
 * `YYYY-MM-DD` string; whether that day was ever captured is answered by the
 * chronicle index, which is the only thing that actually knows.
 */
export const CHRONICLE_DAY_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Narrows unknown input — a route param is typed `string | string[]` at best —
 * to a day string of the right shape.
 */
export function isValidChronicleDay(value: unknown): value is string {
  return typeof value === "string" && CHRONICLE_DAY_PATTERN.test(value);
}

/**
 * `MapId` is the wire/API identifier; the public routes use a different word
 * for the dev map. Kept in one place so no component has to remember that
 * `"dev"` lives at `/map/r3b1rth`.
 */
const MAP_ROUTE_SEGMENT: Record<MapId, string> = {
  main: "main",
  dev: "r3b1rth",
};

/** `/map/main` or `/map/r3b1rth` — the live map. */
export function liveMapHref(mapId: MapId): string {
  return `/map/${MAP_ROUTE_SEGMENT[mapId]}`;
}

/** `/map/{map}/chronicle` — the timelapse studio. */
export function chronicleStudioHref(mapId: MapId): string {
  return `${liveMapHref(mapId)}/chronicle`;
}

/**
 * `/map/{map}/chronicle/{day}` — one stored day, explorable.
 *
 * The day is encoded rather than interpolated raw. A well-formed day has
 * nothing to encode, but this is the same rule `chronicleDayFilePath` follows,
 * and a day string is never concatenated into a path by hand anywhere in the
 * codebase.
 */
export function chronicleDayHref(mapId: MapId, day: string): string {
  return `${chronicleStudioHref(mapId)}/${encodeURIComponent(day)}`;
}
