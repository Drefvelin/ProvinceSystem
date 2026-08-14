import type { MapObject, RegionRecord } from "./types";

export type DrillLayer = {
  regionId: string;
  name: string;
  rgb: string;
};

export function drillStackNames(layers: DrillLayer[]): string[] {
  return layers.map((layer) => layer.name);
}

export function applyDrillStack(
  layers: DrillLayer[],
  regionData: RegionRecord,
  loadData: (regionData: RegionRecord) => void,
  drillDownRegion: (regionId: string, regionData: RegionRecord) => void
) {
  loadData(regionData);
  for (const layer of layers) {
    drillDownRegion(layer.regionId, regionData);
  }
}

export function getAncestryChain(
  regionId: string,
  data: RegionRecord
): string[] {
  const chain: string[] = [];
  let currentId: string | null = regionId;
  while (currentId && data[currentId]) {
    chain.push(currentId);
    currentId = data[currentId].overlord || null;
  }
  return chain;
}

/** Realms whose subject layout is currently open (main hidden, nested visible). */
export function getDrilledRealmIds(mapObjects: MapObject[]): Set<string> {
  const ids = new Set<string>();

  for (const obj of mapObjects) {
    if (obj.id.endsWith("_nested")) continue;
    if (obj.visible) continue;

    const nested = mapObjects.find((entry) => entry.id === `${obj.id}_nested`);
    if (nested?.visible) {
      ids.add(obj.id);
    }
  }

  return ids;
}

function resolveNextDrillTarget(
  regionId: string,
  regionData: RegionRecord,
  drilledIds: Set<string>
): string | null {
  let currentId: string | null = regionId;

  while (currentId) {
    const region: RegionRecord[string] | undefined = regionData[currentId];
    if (!region) return null;

    if (region.overlord) {
      if (drilledIds.has(region.overlord)) {
        return currentId;
      }
    } else if (!drilledIds.has(currentId)) {
      return currentId;
    }

    currentId = region.overlord || null;
  }

  return null;
}

export function getNextDrillTarget(
  regionId: string,
  regionData: RegionRecord,
  drillStack: DrillLayer[]
): string | null {
  const drilledIds = new Set(drillStack.map((layer) => layer.regionId));
  return resolveNextDrillTarget(regionId, regionData, drilledIds);
}

export function getNextDrillTargetFromMap(
  regionId: string,
  regionData: RegionRecord,
  mapObjects: MapObject[]
): string | null {
  return resolveNextDrillTarget(
    regionId,
    regionData,
    getDrilledRealmIds(mapObjects)
  );
}

export function hasLandSubjects(
  regionId: string,
  regionData: RegionRecord
): boolean {
  const subjects = regionData[regionId]?.subjects;
  if (!subjects?.length) return false;

  return subjects.some((subjectId) => (regionData[subjectId]?.size ?? 0) > 0);
}

export function canDrillIntoRegion(
  regionId: string,
  regionData: RegionRecord,
  mapObjects: MapObject[]
): boolean {
  const drilledIds = getDrilledRealmIds(mapObjects);
  const targetId = resolveNextDrillTarget(regionId, regionData, drilledIds);
  if (!targetId || !hasLandSubjects(targetId, regionData)) {
    return false;
  }

  if (drilledIds.has(targetId)) {
    return false;
  }

  return true;
}
