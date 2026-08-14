import { useEffect, useState } from "react";

import type {
  ProvinceCentroids,
  ProvinceNeighbors,
} from "../lib/mapLabels";
import { apiBase, type MapId } from "../components/map/types";

type MapGeometryState = {
  neighbors: ProvinceNeighbors | null;
  centroids: ProvinceCentroids | null;
  ready: boolean;
};

export function useMapGeometry(mapId: MapId): MapGeometryState {
  const [state, setState] = useState<MapGeometryState>({
    neighbors: null,
    centroids: null,
    ready: mapId !== "main",
  });

  useEffect(() => {
    if (mapId !== "main") {
      setState({ neighbors: null, centroids: null, ready: true });
      return;
    }

    let cancelled = false;

    const load = async () => {
      setState({ neighbors: null, centroids: null, ready: false });
      const base = apiBase();

      try {
        const [neighborsRes, centroidsRes] = await Promise.all([
          fetch(`${base}/${mapId}/data/province_neighbors`),
          fetch(`${base}/${mapId}/data/province_centroids`),
        ]);

        if (!neighborsRes.ok || !centroidsRes.ok) {
          throw new Error("Failed to fetch map geometry");
        }

        const [neighbors, centroids] = await Promise.all([
          neighborsRes.json() as Promise<ProvinceNeighbors>,
          centroidsRes.json() as Promise<ProvinceCentroids>,
        ]);

        if (cancelled) return;

        setState({ neighbors, centroids, ready: true });
      } catch (err) {
        if (cancelled) return;
        console.error("Error fetching map geometry:", err);
        setState({ neighbors: null, centroids: null, ready: true });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [mapId]);

  return state;
}
