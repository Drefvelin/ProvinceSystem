import type { RegionRecord } from "./types";

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

export function getNextDrillTarget(
  regionId: string,
  regionData: RegionRecord,
  drillStack: string[]
): string | null {
  let currentId: string | null = regionId;

  while (currentId) {
    const region: RegionRecord[string] | undefined = regionData[currentId];
    if (!region) return null;

    const name = region.name || currentId;

    if (region.overlord) {
      const overlord = regionData[region.overlord];
      const overlordName = overlord?.name || currentId;
      if (drillStack.includes(overlordName)) {
        return currentId;
      }
    } else if (!drillStack.includes(name)) {
      return currentId;
    }

    currentId = region.overlord || null;
  }

  return null;
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
  drillStack: string[]
): boolean {
  const targetId = getNextDrillTarget(regionId, regionData, drillStack);
  if (!targetId) return false;

  return hasLandSubjects(targetId, regionData);
}
