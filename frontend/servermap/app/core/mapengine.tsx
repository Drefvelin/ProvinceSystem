import { useState } from "react";

let mapObjectsState: { id: string; visible: boolean; path: string }[] = [];

export function useMapObjects() {
  const [mapObjects, setMapObjects] = useState(mapObjectsState);

  const loadData = (regionData: Record<string, any>) => {
    const objects = Object.keys(regionData).flatMap((regionId) => {
      const region = regionData[regionId];
      const entries: { id: string; visible: boolean; path: string }[] = [];

      const rgbPath = region.rgb.replace(/,/g, "_");

      // Add main layer
      entries.push({
        id: regionId,
        visible: !region.overlord, // hide if it's a subject
        path: rgbPath,
      });

      // Only add nested layer if the region has subjects
      if (Array.isArray(region.subjects) && region.subjects.length > 0) {
        entries.push({
          id: `${regionId}_nested`,
          visible: false, // nested version also starts hidden if it's a subject
          path: `${rgbPath}_nested`,
        });
      }

      return entries;
    });

    setMapObjects(objects);
    mapObjectsState = objects; // Ensure consistency across renders
  };

  /**
   * Finds the correct hover image and region info, falling back to overlords if necessary.
   */
  const getHoverRegion = (
    mapType: string,
    regionId: string,
    regionData: Record<string, any>
  ): { imagePath: string | null; region: any } => {
    let currentRegionId = regionId;
  
    while (currentRegionId) {
      const region = regionData[currentRegionId];
      if (!region) return { imagePath: null, region: null }; // If region is undefined, stop
  
      // Check the main region first
      const mainObject = mapObjects.find(obj => obj.id === currentRegionId);
      if (mainObject && mainObject.visible) {
        return {
          imagePath: `/data/regions/${mapType}/${mainObject.path}_hover.png`,
          region: region,
        };
      }
  
      // If the main region is NOT visible, check the _nested version
      const nestedId = `${currentRegionId}_nested`;
      const nestedObject = mapObjects.find(obj => obj.id === nestedId);
      if (nestedObject && nestedObject.visible) {
        return {
          imagePath: `/data/regions/${mapType}/${nestedObject.path}_hover.png`,
          region: region,
        };
      }
  
      // Move up to the overlord
      currentRegionId = region.overlord || null;
    }
  
    return { imagePath: null, region: null };
  };

  // 🧠 Find and update visibility in the mapObjects list
  const drillDownRegion = (regionId: string, regionData: Record<string, any>) => {
    const updatedObjects = [...mapObjects];

    const region = regionData[regionId];
    if (!region || !region.subjects || region.subjects.length === 0) return;

    // 1. Hide the main region layer
    const mainIndex = updatedObjects.findIndex(obj => obj.id === regionId);
    if (mainIndex !== -1) updatedObjects[mainIndex].visible = false;

    // 2. Show the nested version of the overlord
    const nestedId = `${regionId}_nested`;
    const nestedIndex = updatedObjects.findIndex(obj => obj.id === nestedId);
    if (nestedIndex !== -1) updatedObjects[nestedIndex].visible = true;

    // 3. Show all subject layers
    for (const subjectId of region.subjects) {
      const subjectIndex = updatedObjects.findIndex(obj => obj.id === subjectId);
      if (subjectIndex !== -1) updatedObjects[subjectIndex].visible = true;
    }

    setMapObjects(updatedObjects);
  };

  return { mapObjects, loadData, getHoverRegion, drillDownRegion };
}
