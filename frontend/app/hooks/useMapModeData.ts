// hooks/useMapModeData.ts
import { useEffect, useState } from "react";

import type { MapId } from "../components/map/types";
import {
  MapAccessError,
  fetchMapJson,
  staffMapAccessReason,
} from "@/lib/map/api";
import type { MapAccessGateReason } from "../components/map/MapAccessGate";

export function useMapModeData({
  mapId,
  mapType,
  loadData,
  sessionToken,
}: {
  mapId: MapId;
  mapType: string;
  loadData: (data: Record<string, any>) => void;
  sessionToken?: string | null;
}) {
  const [regionData, setRegionData] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [accessError, setAccessError] = useState<MapAccessGateReason | null>(
    null
  );

  useEffect(() => {
    // Map modes with no region data
    if (
      mapType === "terrain" ||
      mapType === "fertility" ||
      mapType === "prosperity"
    ) {
      setRegionData(null);
      setLoading(false);
      setAccessError(null);
      loadData({});
      return;
    }

    let cancelled = false;

    // Drop previous mode's regions so title rollups cannot read stale ids.
    setRegionData(null);
    setLoading(true);
    setAccessError(null);
    loadData({});

    const fetchRegionData = async () => {
      try {
        const rawData = await fetchMapJson<Record<string, any>>(
          `/${mapId}/data/${mapType}`,
          { sessionToken }
        );
        if (cancelled) return;

        // Filter region data
        const filteredData: Record<string, any> = Object.fromEntries(
          Object.entries(rawData).filter(([_, region]) => {
            // Always require RGB
            if (typeof region.rgb !== "string") return false;

            // Only apply geometry filter for nation map
            if (mapType === "nation") {
              return (
                Array.isArray(region.provinces) &&
                region.provinces.length > 0
              );
            }

            // All other map types keep everything
            return true;
          })
        );

        setRegionData(filteredData);
        loadData(filteredData);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof MapAccessError && err.status === 403) {
          setAccessError(staffMapAccessReason(err));
        } else {
          console.error("Error fetching region data:", err);
        }
        setRegionData(null);
        loadData({});
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void fetchRegionData();

    return () => {
      cancelled = true;
    };
  }, [mapId, mapType, sessionToken, loadData]);

  return { regionData, loading, accessError };
}
