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

        const data = await res.json();
        if (cancelled) return;

        setRegionData(data);
        loadData(data);
      } catch (err) {
        if (cancelled) return;
        console.error("Error fetching region data:", err);
        setRegionData(null);
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
