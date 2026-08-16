import { useEffect, useState } from "react";

import type { MapId, SettlementMarker } from "../components/map/types";
import { filterPlacedSettlements } from "../lib/settlementMarkers";
import { fetchMapMarkers } from "@/lib/map/api";

type MapMarkersState = {
  settlements: SettlementMarker[];
  loading: boolean;
  error: string | null;
};

export function useMapMarkers(
  mapId: MapId,
  sessionToken?: string | null,
  enabled = true
): MapMarkersState {
  const [state, setState] = useState<MapMarkersState>({
    settlements: [],
    loading: enabled,
    error: null,
  });

  useEffect(() => {
    if (!enabled) {
      setState({ settlements: [], loading: false, error: null });
      return;
    }

    let cancelled = false;

    const load = async () => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const data = await fetchMapMarkers(mapId, sessionToken);
        if (cancelled) return;
        setState({
          settlements: filterPlacedSettlements(data.settlements ?? []),
          loading: false,
          error: null,
        });
      } catch (err) {
        if (cancelled) return;
        const message =
          err instanceof Error ? err.message : "Failed to load map markers";
        console.error("[useMapMarkers]", message, err);
        setState({ settlements: [], loading: false, error: message });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [mapId, sessionToken, enabled]);

  return state;
}
