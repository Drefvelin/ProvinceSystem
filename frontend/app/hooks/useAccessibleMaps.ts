"use client";

import { useCallback, useEffect, useState } from "react";

import {
  fetchAccessibleMaps,
  type AccessibleMapEntry,
} from "@/lib/map/api";
import { getSession, isSessionValid } from "@/lib/characters/session";

type AccessibleMapsState = {
  maps: AccessibleMapEntry[];
  loading: boolean;
  error: string | null;
};

export function useAccessibleMaps(): AccessibleMapsState {
  const [state, setState] = useState<AccessibleMapsState>({
    maps: [],
    loading: true,
    error: null,
  });

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const session = getSession();
      const token = isSessionValid(session) ? session?.session_token : null;
      const data = await fetchAccessibleMaps(token);
      setState({ maps: data.maps, loading: false, error: null });
    } catch {
      setState({ maps: [], loading: false, error: "Failed to load maps" });
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const onStorage = (event: StorageEvent) => {
      if (event.key === "tfmc_character_session") {
        void load();
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [load]);

  return state;
}
