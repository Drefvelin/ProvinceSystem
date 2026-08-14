export const MIN_PROVINCES = 3;
export const MIN_PIXEL_AREA = 15000;
export const LABEL_AXIS_DEBUG_COLOR = "#ff2222";
export const LABEL_INK = "#2a1f14";
export const LABEL_HALO = "#e8e4d9";
export const LABEL_STROKE_WIDTH = 4;
export const LABEL_FONT_WEIGHT = 500;
export const LABEL_MAX_ZOOM = 1.5;
export const DEFAULT_MAP_ZOOM = 1;

export function shouldShowLabelsAtZoom(zoom: number): boolean {
  return zoom <= LABEL_MAX_ZOOM;
}

export type ProvinceNeighbors = Record<string, number[]>;
export type ProvinceCentroid = { x: number; y: number; pixel_count: number };
export type ProvinceCentroids = Record<string, ProvinceCentroid>;

export type NationRegionInput = {
  name?: string;
  provinces?: number[];
  subjects?: string[];
};

export type LabelMapObject = {
  id: string;
  visible: boolean;
};

export type NationLabelScope = "full" | "direct";

export type NationLabelSpec = {
  nationId: string;
  componentIndex: number;
  text: string;
  scope: NationLabelScope;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  cx: number;
  cy: number;
  angleDeg: number;
  segmentPx: number;
  textLength: number;
  fontSize: number;
};

export type ComputeNationLabelsOptions = {
  minProvinces?: number;
  minPixelArea?: number;
};

function neighborList(
  neighbors: ProvinceNeighbors,
  provinceId: number
): number[] {
  return neighbors[String(provinceId)] ?? [];
}

export function connectedComponents(
  provinceIds: number[],
  neighbors: ProvinceNeighbors
): number[][] {
  const allowed = new Set(provinceIds);
  const visited = new Set<number>();
  const components: number[][] = [];

  for (const start of provinceIds) {
    if (visited.has(start)) continue;

    const component: number[] = [];
    const queue = [start];
    visited.add(start);

    while (queue.length > 0) {
      const current = queue.shift()!;
      component.push(current);

      for (const next of neighborList(neighbors, current)) {
        if (!allowed.has(next) || visited.has(next)) continue;
        visited.add(next);
        queue.push(next);
      }
    }

    components.push(component);
  }

  return components;
}

function bfsFarthest(
  start: number,
  allowed: Set<number>,
  neighbors: ProvinceNeighbors
): { id: number; distance: number } {
  const distances = new Map<number, number>([[start, 0]]);
  const queue = [start];
  let farthest = { id: start, distance: 0 };

  while (queue.length > 0) {
    const current = queue.shift()!;
    const currentDistance = distances.get(current) ?? 0;

    for (const next of neighborList(neighbors, current)) {
      if (!allowed.has(next) || distances.has(next)) continue;
      const nextDistance = currentDistance + 1;
      distances.set(next, nextDistance);
      queue.push(next);
      if (
        nextDistance > farthest.distance ||
        (nextDistance === farthest.distance && next < farthest.id)
      ) {
        farthest = { id: next, distance: nextDistance };
      }
    }
  }

  return farthest;
}

export function graphDiameterEndpoints(
  componentIds: number[],
  neighbors: ProvinceNeighbors
): [number, number] {
  if (componentIds.length === 0) {
    throw new Error("graphDiameterEndpoints requires at least one province");
  }

  if (componentIds.length === 1) {
    return [componentIds[0], componentIds[0]];
  }

  const allowed = new Set(componentIds);
  const start = [...componentIds].sort((a, b) => a - b)[0];
  const endA = bfsFarthest(start, allowed, neighbors);
  const endB = bfsFarthest(endA.id, allowed, neighbors);
  const a = endA.id;
  const b = endB.id;
  return a <= b ? [a, b] : [b, a];
}

export function segmentPixelLength(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number {
  return Math.hypot(x2 - x1, y2 - y1);
}

export function pixelDiameterEndpoints(
  componentIds: number[],
  centroids: ProvinceCentroids
): [number, number] {
  if (componentIds.length === 0) {
    throw new Error("pixelDiameterEndpoints requires at least one province");
  }

  if (componentIds.length === 1) {
    return [componentIds[0], componentIds[0]];
  }

  const points = componentIds
    .map((id) => ({ id, centroid: centroidOf(id, centroids) }))
    .filter((entry): entry is { id: number; centroid: ProvinceCentroid } =>
      entry.centroid !== null
    );

  if (points.length === 0) {
    throw new Error("pixelDiameterEndpoints requires at least one centroid");
  }

  if (points.length === 1) {
    return [points[0].id, points[0].id];
  }

  let bestDistance = -1;
  let bestPair: [number, number] = [points[0].id, points[0].id];

  for (let i = 0; i < points.length; i += 1) {
    for (let j = i + 1; j < points.length; j += 1) {
      const a = points[i];
      const b = points[j];
      const distance = segmentPixelLength(a.centroid.x, a.centroid.y, b.centroid.x, b.centroid.y);
      const pair: [number, number] =
        a.id <= b.id ? [a.id, b.id] : [b.id, a.id];

      if (
        distance > bestDistance ||
        (distance === bestDistance &&
          (pair[0] < bestPair[0] ||
            (pair[0] === bestPair[0] && pair[1] < bestPair[1])))
      ) {
        bestDistance = distance;
        bestPair = pair;
      }
    }
  }

  return bestPair;
}

export function fontSizeForLabel(segmentPx: number, text: string): number {
  const units = text.trim().length || 1;
  return Math.round(segmentPx / units);
}

export function componentPixelArea(
  provinceIds: number[],
  centroids: ProvinceCentroids
): number {
  return provinceIds.reduce((sum, pid) => {
    return sum + (centroids[String(pid)]?.pixel_count ?? 0);
  }, 0);
}

export function labelAngleDeg(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number {
  const rad = Math.atan2(y2 - y1, x2 - x1);
  let deg = (rad * 180) / Math.PI;
  if (deg <= -90) deg += 180;
  else if (deg > 90) deg -= 180;
  return deg;
}

function centroidOf(
  provinceId: number,
  centroids: ProvinceCentroids
): ProvinceCentroid | null {
  return centroids[String(provinceId)] ?? null;
}

export function isNationLabelVisible(
  nationId: string,
  mapObjects: LabelMapObject[]
): boolean {
  const main = mapObjects.find((obj) => obj.id === nationId);
  const nested = mapObjects.find((obj) => obj.id === `${nationId}_nested`);
  return !!(main?.visible || nested?.visible);
}

export function isDrilledSuzerainView(
  nationId: string,
  mapObjects: LabelMapObject[]
): boolean {
  const main = mapObjects.find((obj) => obj.id === nationId);
  const nested = mapObjects.find((obj) => obj.id === `${nationId}_nested`);
  return !!main && !main.visible && nested?.visible === true;
}

export function directHoldingProvinces(
  nationId: string,
  regionData: Record<string, NationRegionInput>
): number[] {
  const region = regionData[nationId];
  const provinces = region?.provinces ?? [];
  const subjects = region?.subjects ?? [];
  if (!subjects.length) return provinces;

  const subjectProvinces = new Set<number>();
  for (const subjectId of subjects) {
    for (const provinceId of regionData[subjectId]?.provinces ?? []) {
      subjectProvinces.add(provinceId);
    }
  }

  return provinces.filter((provinceId) => !subjectProvinces.has(provinceId));
}

export function provincesForNationLabel(
  nationId: string,
  regionData: Record<string, NationRegionInput>,
  mapObjects: LabelMapObject[]
): { provinces: number[]; scope: NationLabelScope } | null {
  if (!isNationLabelVisible(nationId, mapObjects)) return null;

  const region = regionData[nationId];
  const allProvinces = region?.provinces ?? [];
  if (!allProvinces.length) return null;

  if (isDrilledSuzerainView(nationId, mapObjects) && region?.subjects?.length) {
    const directProvinces = directHoldingProvinces(nationId, regionData);
    if (!directProvinces.length) return null;
    return { provinces: directProvinces, scope: "direct" };
  }

  return { provinces: allProvinces, scope: "full" };
}

export function labelsForProvinces(
  nationId: string,
  name: string,
  provinces: number[],
  neighbors: ProvinceNeighbors,
  centroids: ProvinceCentroids,
  scope: NationLabelScope,
  options?: ComputeNationLabelsOptions
): NationLabelSpec[] {
  const minProvinces = options?.minProvinces ?? MIN_PROVINCES;
  const minPixelArea = options?.minPixelArea ?? MIN_PIXEL_AREA;
  const labels: NationLabelSpec[] = [];

  const withGeometry = provinces.filter(
    (pid) => centroidOf(pid, centroids) !== null
  );
  if (!withGeometry.length) return labels;

  const components = connectedComponents(withGeometry, neighbors);

  let componentIndex = 0;
  for (const component of components) {
    if (component.length < minProvinces) continue;
    if (componentPixelArea(component, centroids) < minPixelArea) continue;

    const [pidA, pidB] = pixelDiameterEndpoints(component, centroids);
    const cA = centroidOf(pidA, centroids)!;
    const cB = centroidOf(pidB, centroids)!;

    const x1 = cA.x;
    const y1 = cA.y;
    const x2 = cB.x;
    const y2 = cB.y;
    const cx = (x1 + x2) / 2;
    const cy = (y1 + y2) / 2;
    const segmentPx = segmentPixelLength(x1, y1, x2, y2);

    labels.push({
      nationId,
      componentIndex,
      text: name,
      scope,
      x1,
      y1,
      x2,
      y2,
      cx,
      cy,
      angleDeg: labelAngleDeg(x1, y1, x2, y2),
      segmentPx,
      textLength: segmentPx,
      fontSize: fontSizeForLabel(segmentPx, name),
    });
    componentIndex += 1;
  }

  return labels;
}

export function computeNationLabels(
  regionData: Record<string, NationRegionInput>,
  neighbors: ProvinceNeighbors,
  centroids: ProvinceCentroids,
  options?: ComputeNationLabelsOptions
): NationLabelSpec[] {
  const labels: NationLabelSpec[] = [];

  for (const [nationId, region] of Object.entries(regionData)) {
    const name = region.name?.trim();
    const provinces = region.provinces;
    if (!name || !provinces?.length) continue;

    labels.push(
      ...labelsForProvinces(
        nationId,
        name,
        provinces,
        neighbors,
        centroids,
        "full",
        options
      )
    );
  }

  return labels;
}

export function computeVisibleNationLabels(
  regionData: Record<string, NationRegionInput>,
  neighbors: ProvinceNeighbors,
  centroids: ProvinceCentroids,
  mapObjects: LabelMapObject[],
  options?: ComputeNationLabelsOptions
): NationLabelSpec[] {
  const labels: NationLabelSpec[] = [];

  for (const nationId of Object.keys(regionData)) {
    const resolved = provincesForNationLabel(nationId, regionData, mapObjects);
    if (!resolved) continue;

    const name = regionData[nationId]?.name?.trim();
    if (!name) continue;

    labels.push(
      ...labelsForProvinces(
        nationId,
        name,
        resolved.provinces,
        neighbors,
        centroids,
        resolved.scope,
        options
      )
    );
  }

  return labels;
}
