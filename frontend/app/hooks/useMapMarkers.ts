import { useEffect, useState } from "react";

import type {
  FortMarker,
  InstallationMarker,
  MapId,
  SettlementMarker,
  WarExport,
} from "../components/map/types";
import { filterPlacedInstallations } from "../lib/installationMarkers";
import { filterPlacedSettlements } from "../lib/settlementMarkers";
import { fetchMapMarkers } from "@/lib/map/api";

type MapMarkersState = {
  settlements: SettlementMarker[];
  installations: InstallationMarker[];
  forts: FortMarker[];
  wars: WarExport[];
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
    installations: [],
    forts: [],
    wars: [],
    loading: enabled,
    error: null,
  });

  useEffect(() => {
    if (!enabled) {
      setState({
        settlements: [],
        installations: [],
        forts: [],
        wars: [],
        loading: false,
        error: null,
      });
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
          installations: filterPlacedInstallations(data.installations ?? []),
          forts: data.forts ?? [],
          wars: data.wars ?? [],
          loading: false,
          error: null,
        });
      } catch (err) {
        if (cancelled) return;
        const message =
          err instanceof Error ? err.message : "Failed to load map markers";
        console.error("[useMapMarkers]", message, err);
        setState({
          settlements: [],
          installations: [],
          forts: [],
          wars: [],
          loading: false,
          error: message,
        });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [mapId, sessionToken, enabled]);

  return state;
}
