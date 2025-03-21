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

  return { mapObjects, loadData };
}
