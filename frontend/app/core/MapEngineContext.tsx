// core/MapEngineContext.tsx
"use client";

import React, { createContext, useContext, useState } from "react";
import type { MapObject, OverlayBBox } from "../components/map/types";
import { apiBase } from "../components/map/types";

type HoverRegionResult = {
  regionId: string | null;
  imagePath: string | null;
  region: Record<string, unknown> | null;
  overlay?: OverlayBBox;
};

type MapEngineContextType = {
  mapObjects: MapObject[];
  loadData: (regionData: Record<string, unknown>) => void;
  resetMapObjects: () => void;
  getHoverRegion: (
    mapType: string,
    mapId: string,
    regionId: string,
    regionData: Record<string, unknown>
  ) => HoverRegionResult;
  drillDownRegion: (
    regionId: string,
    regionData: Record<string, unknown>
  ) => void;
};

const MapEngineContext = createContext<MapEngineContextType | undefined>(
  undefined
);

export const MapEngineProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [mapObjects, setMapObjects] = useState<MapObject[]>([]);

  const loadData = (regionData: Record<string, unknown>) => {
    const objects = Object.keys(regionData).flatMap((regionId) => {
      const region = regionData[regionId] as Record<string, unknown>;
      const rgb = region.rgb as string | undefined;
      if (!rgb) return [];

      const rgbPath = rgb.replace(/,/g, "_");
      const overlay = region.overlay as OverlayBBox | undefined;
      const overlayNested = region.overlay_nested as OverlayBBox | undefined;

      const entries: MapObject[] = [
        {
          id: regionId,
          visible: !region.overlord,
          path: rgbPath,
          overlay,
        },
      ];

      const subjects = region.subjects as string[] | undefined;
      if (subjects?.length) {
        entries.push({
          id: `${regionId}_nested`,
          visible: false,
          path: `${rgbPath}_nested`,
          overlay: overlayNested,
        });
      }

      return entries;
    });

    setMapObjects(objects);
  };

  const resetMapObjects = () => setMapObjects([]);

  const getHoverRegion = (
    mapType: string,
    mapId: string,
    regionId: string,
    regionData: Record<string, unknown>
  ): HoverRegionResult => {
    const base = apiBase();
    let currentRegionId: string | null = regionId;

    while (currentRegionId) {
      const region = regionData[currentRegionId] as Record<string, unknown>;
      if (!region) return { regionId: null, imagePath: null, region: null };

      const main = mapObjects.find((obj) => obj.id === currentRegionId);
      if (main?.visible) {
        return {
          regionId: currentRegionId,
          imagePath: `${base}/${mapId}/regions/${mapType}/${main.path}_hover`,
          region,
          overlay: main.overlay,
        };
      }

      const nestedId = `${currentRegionId}_nested`;
      const nested = mapObjects.find((obj) => obj.id === nestedId);
      if (nested?.visible) {
        return {
          regionId: currentRegionId,
          imagePath: `${base}/${mapId}/regions/${mapType}/${nested.path}_hover`,
          region,
          overlay: nested.overlay,
        };
      }

      currentRegionId = (region.overlord as string) || null;
    }

    return { regionId: null, imagePath: null, region: null };
  };

  const drillDownRegion = (
    regionId: string,
    regionData: Record<string, unknown>
  ) => {
    const updated = [...mapObjects];
    const region = regionData[regionId] as Record<string, unknown>;
    const subjects = region?.subjects as string[] | undefined;
    if (!region || !subjects?.length) return;

    const mainIndex = updated.findIndex((obj) => obj.id === regionId);
    if (mainIndex !== -1) updated[mainIndex].visible = false;

    const nestedIndex = updated.findIndex(
      (obj) => obj.id === `${regionId}_nested`
    );
    if (nestedIndex !== -1) updated[nestedIndex].visible = true;

    for (const subjectId of subjects) {
      const subjectIndex = updated.findIndex((obj) => obj.id === subjectId);
      if (subjectIndex !== -1) updated[subjectIndex].visible = true;
    }

    setMapObjects(updated);
  };

  return (
    <MapEngineContext.Provider
      value={{
        mapObjects,
        loadData,
        resetMapObjects,
        getHoverRegion,
        drillDownRegion,
      }}
    >
      {children}
    </MapEngineContext.Provider>
  );
};

export const useMapEngine = () => {
  const context = useContext(MapEngineContext);
  if (!context)
    throw new Error("useMapEngine must be used inside a MapEngineProvider");
  return context;
};
