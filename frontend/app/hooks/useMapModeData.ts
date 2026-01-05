// hooks/useMapModeData.ts
import { useEffect, useState } from "react";

export function useMapModeData({
  mapId,
  mapType,
  loadData,
}: {
  mapId: "main" | "dev";
  mapType: string;
  loadData: (data: Record<string, any>) => void;
}) {
  const [regionData, setRegionData] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Map modes with no region data
    if (
      mapType === "terrain" ||
      mapType === "fertility" ||
      mapType === "prosperity"
    ) {
      setRegionData(null);
      setLoading(false);
      loadData({});
      return;
    }

    let cancelled = false;

    const fetchRegionData = async () => {
      setLoading(true);
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/${mapId}/data/${mapType}`
        );
        if (!res.ok) throw new Error("Failed to fetch region data");

        const rawData: Record<string, any> = await res.json();
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
        console.error("Error fetching region data:", err);
        setRegionData(null);
        loadData({});
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchRegionData();

    return () => {
      cancelled = true;
    };
  }, [mapId, mapType]);

  return { regionData, loading };
}