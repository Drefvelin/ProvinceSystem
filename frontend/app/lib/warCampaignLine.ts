import type { WarExport } from "../components/map/types";
import type { ProvinceCentroids } from "./mapLabels";

export type MapPoint = { x: number; y: number };

export type CatmullRomOptions = {
  tension?: number;
  samplesPerSegment?: number;
};

export type WarLineStrokeStyle = {
  borderColor: string;
  dashColor: string;
  borderWidth: number;
  dashWidth: number;
  dashArray: string;
  opacity: number;
};

export const WAR_LINE_BORDER_COLOR = "#2a1810";
export const WAR_LINE_DASH_COLOR = "#8b3a3a";
export const WAR_LINE_OPACITY = 0.85;
export const WAR_LINE_DASH_WIDTH = 4;
export const WAR_LINE_BORDER_WIDTH = WAR_LINE_DASH_WIDTH * 1.5;
export const WAR_LINE_DASH_ARRAY = "6 8";
export const CATMULL_ROM_TENSION = 0.5;
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

  const x =
    s *
    (2 * p1.x +
      (-p0.x + p2.x) * t +
      (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 +
      (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3);
  const y =
    s *
    (2 * p1.y +
      (-p0.y + p2.y) * t +
      (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 +
      (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3);

  return { x, y };
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

    const segmentSamples = i === points.length - 2 ? samplesPerSegment + 1 : samplesPerSegment;
    for (let step = 0; step < segmentSamples; step += 1) {
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

function stableHash(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash * 31 + value.charCodeAt(i)) | 0;
  }
  return Math.abs(hash);
}

function shiftHexHue(hex: string, degrees: number): string {
  const normalized = hex.replace("#", "");
  if (normalized.length !== 6) return hex;

  const r = parseInt(normalized.slice(0, 2), 16) / 255;
  const g = parseInt(normalized.slice(2, 4), 16) / 255;
  const b = parseInt(normalized.slice(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const delta = max - min;

  let h = 0;
  if (delta !== 0) {
    if (max === r) h = ((g - b) / delta) % 6;
    else if (max === g) h = (b - r) / delta + 2;
    else h = (r - g) / delta + 4;
    h *= 60;
    if (h < 0) h += 360;
  }

  const l = (max + min) / 2;
  const s = delta === 0 ? 0 : delta / (1 - Math.abs(2 * l - 1));

  const shifted = (h + degrees) % 360;
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((shifted / 60) % 2) - 1));
  const m = l - c / 2;

  let r1 = 0;
  let g1 = 0;
  let b1 = 0;
  if (shifted < 60) {
    r1 = c;
    g1 = x;
  } else if (shifted < 120) {
    r1 = x;
    g1 = c;
  } else if (shifted < 180) {
    g1 = c;
    b1 = x;
  } else if (shifted < 240) {
    g1 = x;
    b1 = c;
  } else if (shifted < 300) {
    r1 = x;
    b1 = c;
  } else {
    r1 = c;
    b1 = x;
  }

  const toHex = (channel: number) =>
    Math.round((channel + m) * 255)
      .toString(16)
      .padStart(2, "0");

  return `#${toHex(r1)}${toHex(g1)}${toHex(b1)}`;
}

export function warLineStrokeStyle(
  warId: string,
  warCount = 1
): WarLineStrokeStyle {
  const hueShift =
    warCount > 1 ? (stableHash(warId) % 7) * 18 - 54 : 0;

  return {
    borderColor: WAR_LINE_BORDER_COLOR,
    dashColor: shiftHexHue(WAR_LINE_DASH_COLOR, hueShift),
    borderWidth: WAR_LINE_BORDER_WIDTH,
    dashWidth: WAR_LINE_DASH_WIDTH,
    dashArray: WAR_LINE_DASH_ARRAY,
    opacity: WAR_LINE_OPACITY,
  };
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
