import type { WarExport } from "../components/map/types";
import type { ProvinceCentroids } from "./mapLabels";

export type MapPoint = { x: number; y: number };

export type CatmullRomOptions = {
  tension?: number;
  samplesPerSegment?: number;
};

export type WarLineStrokeStyle = {
  dashColor: string;
  dashWidth: number;
  dashArray: string;
  opacity: number;
};

export type WarCampaignPathPair = {
  progressedD: string;
  remainingD: string;
};

export const WAR_LINE_PROGRESSED_COLOR = "#ffffff";
export const WAR_LINE_REMAINING_COLOR = "#c4c4c4";
export const WAR_LINE_OPACITY = 1;
export const WAR_LINE_DASH_WIDTH = 8;
export const WAR_LINE_DASH_ARRAY = "12 16";
export const CATMULL_ROM_TENSION = 0;
export const CATMULL_ROM_SAMPLES_PER_SEGMENT = 12;

function isFinitePoint(point: MapPoint): boolean {
  return Number.isFinite(point.x) && Number.isFinite(point.y);
}

function pointsEqual(a: MapPoint, b: MapPoint, epsilon = 0.5): boolean {
  return Math.abs(a.x - b.x) <= epsilon && Math.abs(a.y - b.y) <= epsilon;
}

function linePointsFromCampaign(war: WarExport): MapPoint[] {
  const linePoints = war.campaign_line_points;
  if (!linePoints?.length) return [];

  const resolved: MapPoint[] = [];
  for (const point of linePoints) {
    if (!Number.isFinite(point.map_x) || !Number.isFinite(point.map_y)) {
      continue;
    }
    resolved.push({ x: point.map_x, y: point.map_y });
  }
  return resolved;
}

function linePointsFromCentroids(
  war: WarExport,
  centroids: ProvinceCentroids
): MapPoint[] {
  const provinces = war.campaign_provinces;
  if (!provinces?.length) return [];

  const resolved: MapPoint[] = [];
  for (const provinceId of provinces) {
    const centroid = centroids[String(provinceId)];
    if (!centroid || !Number.isFinite(centroid.x) || !Number.isFinite(centroid.y)) {
      continue;
    }
    resolved.push({ x: centroid.x, y: centroid.y });
  }
  return resolved;
}

function maybePrependAttackerCapital(
  waypoints: MapPoint[],
  war: WarExport
): MapPoint[] {
  const capital = war.attacker_capital;
  if (
    !capital ||
    !Number.isFinite(capital.map_x) ||
    !Number.isFinite(capital.map_y)
  ) {
    return waypoints;
  }

  const capitalPoint = { x: capital.map_x!, y: capital.map_y! };
  if (!waypoints.length) {
    return [capitalPoint];
  }

  const capitalProvinceId = capital.province_id;
  const firstLineProvinceId = war.campaign_line_points?.[0]?.province_id;
  if (
    capitalProvinceId != null &&
    firstLineProvinceId != null &&
    capitalProvinceId === firstLineProvinceId
  ) {
    return waypoints;
  }

  if (pointsEqual(waypoints[0], capitalPoint)) {
    return waypoints;
  }

  return [capitalPoint, ...waypoints];
}

export function resolveWarWaypoints(
  war: WarExport,
  centroids?: ProvinceCentroids | null
): MapPoint[] {
  let waypoints = linePointsFromCampaign(war);
  if (waypoints.length < 2 && centroids) {
    waypoints = linePointsFromCentroids(war, centroids);
  }

  waypoints = maybePrependAttackerCapital(waypoints, war);

  const valid = waypoints.filter(isFinitePoint);
  if (valid.length < 2) {
    return [];
  }
  return valid;
}

function catmullRomPoint(
  p0: MapPoint,
  p1: MapPoint,
  p2: MapPoint,
  p3: MapPoint,
  t: number,
  tension: number
): MapPoint {
  const t2 = t * t;
  const t3 = t2 * t;
  const s = (1 - tension) / 2;
  const h00 = 2 * t3 - 3 * t2 + 1;
  const h10 = t3 - 2 * t2 + t;
  const h01 = -2 * t3 + 3 * t2;
  const h11 = t3 - t2;

  const m1x = s * (p2.x - p0.x);
  const m1y = s * (p2.y - p0.y);
  const m2x = s * (p3.x - p1.x);
  const m2y = s * (p3.y - p1.y);

  return {
    x: h00 * p1.x + h10 * m1x + h01 * p2.x + h11 * m2x,
    y: h00 * p1.y + h10 * m1y + h01 * p2.y + h11 * m2y,
  };
}

export function catmullRomSpline(
  points: MapPoint[],
  options: CatmullRomOptions = {}
): MapPoint[] {
  if (points.length < 2) return [];
  if (points.length === 2) return [...points];

  const tension = options.tension ?? CATMULL_ROM_TENSION;
  const samplesPerSegment = options.samplesPerSegment ?? CATMULL_ROM_SAMPLES_PER_SEGMENT;
  const result: MapPoint[] = [];

  for (let i = 0; i < points.length - 1; i += 1) {
    const p0 = points[Math.max(0, i - 1)];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[Math.min(points.length - 1, i + 2)];

    for (let step = 0; step <= samplesPerSegment; step += 1) {
      if (i > 0 && step === 0) continue;
      const t = step / samplesPerSegment;
      result.push(catmullRomPoint(p0, p1, p2, p3, t, tension));
    }
  }

  if (result.length === 0) return [...points];
  result[0] = points[0];
  result[result.length - 1] = points[points.length - 1];
  return result;
}

export function buildSvgPathD(points: MapPoint[]): string {
  if (points.length === 0) return "";
  const [first, ...rest] = points;
  const segments = rest.map((point) => `L ${point.x} ${point.y}`);
  return `M ${first.x} ${first.y} ${segments.join(" ")}`;
}

export function warLineStrokeStyle(
  segment: "progressed" | "remaining"
): WarLineStrokeStyle {
  return {
    dashColor:
      segment === "progressed"
        ? WAR_LINE_PROGRESSED_COLOR
        : WAR_LINE_REMAINING_COLOR,
    dashWidth: WAR_LINE_DASH_WIDTH,
    dashArray: WAR_LINE_DASH_ARRAY,
    opacity: WAR_LINE_OPACITY,
  };
}

export function campaignFrontAxisIndex(war: WarExport): number {
  const axis = war.campaign_provinces ?? [];
  const fallbackLength = war.campaign_line_points?.length ?? 0;
  const length = axis.length || fallbackLength;
  if (!length) return 0;

  let front = war.cursor_index ?? 0;
  if (!Number.isFinite(front)) front = 0;
  front = Math.max(0, Math.min(length - 1, front));

  for (const provinceId of war.occupied_by_attacker ?? []) {
    const index = axis.indexOf(provinceId);
    if (index > front) front = index;
  }
  return front;
}

function prependedCapital(waypoints: MapPoint[], war: WarExport): boolean {
  if (waypoints.length < 2) return false;
  const capital = war.attacker_capital;
  if (
    !capital ||
    !Number.isFinite(capital.map_x) ||
    !Number.isFinite(capital.map_y)
  ) {
    return false;
  }
  return pointsEqual(waypoints[0], { x: capital.map_x!, y: capital.map_y! });
}

export function frontWaypointIndex(war: WarExport, waypoints: MapPoint[]): number {
  if (waypoints.length === 0) return 0;
  const axisFront = campaignFrontAxisIndex(war);
  const offset = prependedCapital(waypoints, war) ? 1 : 0;
  return Math.max(0, Math.min(waypoints.length - 1, axisFront + offset));
}

function nearestSplineIndex(spline: MapPoint[], target: MapPoint): number {
  let best = 0;
  let bestDist = Number.POSITIVE_INFINITY;
  for (let i = 0; i < spline.length; i += 1) {
    const dx = spline[i].x - target.x;
    const dy = spline[i].y - target.y;
    const dist = dx * dx + dy * dy;
    if (dist < bestDist) {
      bestDist = dist;
      best = i;
    }
  }
  return best;
}

export function splitSplineAtIndex(
  spline: MapPoint[],
  splitIndex: number
): { before: MapPoint[]; after: MapPoint[] } {
  if (spline.length < 2) {
    return { before: [], after: [] };
  }
  const index = Math.max(0, Math.min(spline.length - 1, splitIndex));
  const before = spline.slice(0, index + 1);
  const after = spline.slice(index);
  return { before, after };
}

export function buildWarCampaignPathD(
  war: WarExport,
  centroids?: ProvinceCentroids | null
): string {
  const waypoints = resolveWarWaypoints(war, centroids);
  if (waypoints.length < 2) return "";
  const spline = catmullRomSpline(waypoints);
  return buildSvgPathD(spline);
}

export function buildWarCampaignPathPair(
  war: WarExport,
  centroids?: ProvinceCentroids | null
): WarCampaignPathPair {
  const empty = { progressedD: "", remainingD: "" };
  const waypoints = resolveWarWaypoints(war, centroids);
  if (waypoints.length < 2) return empty;

  const spline = catmullRomSpline(waypoints);
  const frontWp = waypoints[frontWaypointIndex(war, waypoints)];
  const splitAt = nearestSplineIndex(spline, frontWp);
  const { before, after } = splitSplineAtIndex(spline, splitAt);

  return {
    progressedD: before.length >= 2 ? buildSvgPathD(before) : "",
    remainingD: after.length >= 2 ? buildSvgPathD(after) : "",
  };
}
