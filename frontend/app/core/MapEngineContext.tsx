// core/MapEngineContext.tsx
"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import type { OverlayBBox } from "../components/map/types";
import { apiBase } from "../components/map/types";
import {
  buildMapObjectsFromRegionData,
  initialMapObjectVisibility,
} from "./mapObjectBuilder";

type HoverRegionResult = {
  regionId: string | null;
  imagePath: string | null;
  region: Record<string, unknown> | null;
  overlay?: OverlayBBox;
};

type MapEngineContextType = {
  mapObjects: ReturnType<typeof buildMapObjectsFromRegionData>;
  loadData: (regionData: Record<string, unknown>) => void;
  resetDrillVisibility: (regionData: Record<string, unknown>) => void;
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
  const [mapObjects, setMapObjects] = useState<
    ReturnType<typeof buildMapObjectsFromRegionData>
  >([]);
  const mapObjectsRef = useRef(mapObjects);
  mapObjectsRef.current = mapObjects;

  const loadData = useCallback((regionData: Record<string, unknown>) => {
    const next = buildMapObjectsFromRegionData(regionData);
    setMapObjects((prev) => {
      if (prev.length === 0 && next.length === 0) return prev;
      return next;
    });
  }, []);

  const resetDrillVisibility = useCallback(
    (regionData: Record<string, unknown>) => {
      setMapObjects((prev) =>
        prev.map((obj) => ({
          ...obj,
          visible: initialMapObjectVisibility(obj, regionData),
        }))
      );
    },
    []
  );

  const resetMapObjects = useCallback(() => {
    setMapObjects((prev) => (prev.length === 0 ? prev : []));
  }, []);

  const getHoverRegion = useCallback((
    mapType: string,
    mapId: string,
    regionId: string,
    regionData: Record<string, unknown>
  ): HoverRegionResult => {
    const base = apiBase();
    let currentRegionId: string | null = regionId;
    const objects = mapObjectsRef.current;

    while (currentRegionId) {
      const region = regionData[currentRegionId] as Record<string, unknown>;
      if (!region) return { regionId: null, imagePath: null, region: null };

      const main = objects.find((obj) => obj.id === currentRegionId);
      if (main?.visible) {
        return {
          regionId: currentRegionId,
          imagePath: `${base}/${mapId}/regions/${mapType}/${main.path}_hover`,
          region,
          overlay: main.overlay,
        };
      }

      const nestedId = `${currentRegionId}_nested`;
      const nested = objects.find((obj) => obj.id === nestedId);
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
  }, []);

  const drillDownRegion = useCallback(
    (regionId: string, regionData: Record<string, unknown>) => {
      setMapObjects((prev) => {
        const region = regionData[regionId] as Record<string, unknown>;
        const subjects = region?.subjects as string[] | undefined;
        if (!region || !subjects?.length) return prev;

        const updated = prev.map((obj) => ({ ...obj }));
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

        return updated;
      });
    },
    []
  );

  const value = useMemo(
    () => ({
      mapObjects,
      loadData,
      resetDrillVisibility,
      resetMapObjects,
      getHoverRegion,
      drillDownRegion,
    }),
    [
      mapObjects,
      loadData,
      resetDrillVisibility,
      resetMapObjects,
      getHoverRegion,
      drillDownRegion,
    ]
  );

  return (
    <MapEngineContext.Provider value={value}>
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
