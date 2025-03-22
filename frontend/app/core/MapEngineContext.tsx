// core/MapEngineContext.tsx
"use client";

import React, { createContext, useContext, useState } from "react";

type MapObject = {
  id: string;
  visible: boolean;
  path: string;
};

type MapEngineContextType = {
  mapObjects: MapObject[];
  loadData: (regionData: Record<string, any>) => void;
  getHoverRegion: (mapType: string, regionId: string, regionData: Record<string, any>) => { imagePath: string | null; region: any };
  drillDownRegion: (regionId: string, regionData: Record<string, any>) => void;
};

const MapEngineContext = createContext<MapEngineContextType | undefined>(undefined);

export const MapEngineProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mapObjects, setMapObjects] = useState<MapObject[]>([]);

  const loadData = (regionData: Record<string, any>) => {
    const objects = Object.keys(regionData).flatMap((regionId) => {
      const region = regionData[regionId];
      const rgbPath = region.rgb.replace(/,/g, "_");

      const entries: MapObject[] = [
        {
          id: regionId,
          visible: !region.overlord,
          path: rgbPath,
        },
      ];

      if (region.subjects?.length > 0) {
        entries.push({
          id: `${regionId}_nested`,
          visible: false,
          path: `${rgbPath}_nested`,
        });
      }

      return entries;
    });

    setMapObjects(objects);
  };

  const getHoverRegion = (mapType: string, regionId: string, regionData: Record<string, any>) => {
    let currentRegionId = regionId;

    while (currentRegionId) {
      const region = regionData[currentRegionId];
      if (!region) return { imagePath: null, region: null };

      const main = mapObjects.find(obj => obj.id === currentRegionId);
      if (main?.visible) {
        return {
          imagePath: `/data/regions/${mapType}/${main.path}_hover.png`,
          region,
        };
      }

      const nestedId = `${currentRegionId}_nested`;
      const nested = mapObjects.find(obj => obj.id === nestedId);
      if (nested?.visible) {
        return {
          imagePath: `/data/regions/${mapType}/${nested.path}_hover.png`,
          region,
        };
      }

      currentRegionId = region.overlord || null;
    }

    return { imagePath: null, region: null };
  };

  const drillDownRegion = (regionId: string, regionData: Record<string, any>) => {
    const updated = [...mapObjects];
    const region = regionData[regionId];
    if (!region || !region.subjects?.length) return;

    const mainIndex = updated.findIndex(obj => obj.id === regionId);
    if (mainIndex !== -1) updated[mainIndex].visible = false;

    const nestedIndex = updated.findIndex(obj => obj.id === `${regionId}_nested`);
    if (nestedIndex !== -1) updated[nestedIndex].visible = true;

    for (const subjectId of region.subjects) {
      const subjectIndex = updated.findIndex(obj => obj.id === subjectId);
      if (subjectIndex !== -1) updated[subjectIndex].visible = true;
    }

    setMapObjects(updated);
  };

  return (
    <MapEngineContext.Provider value={{ mapObjects, loadData, getHoverRegion, drillDownRegion }}>
      {children}
    </MapEngineContext.Provider>
  );
};

export const useMapEngine = () => {
  const context = useContext(MapEngineContext);
  if (!context) throw new Error("useMapEngine must be used inside a MapEngineProvider");
  return context;
};
