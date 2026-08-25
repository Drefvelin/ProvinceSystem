// hooks/useGuildCache.ts
import { useEffect, useRef } from "react";

import type { MapId } from "../components/map/types";
import { fetchMapJson } from "@/lib/map/api";

export function useGuildCache(
  mapId: MapId,
  sessionToken?: string | null
) {
  const guildNameCacheRef = useRef<Record<string, string>>({});

  useEffect(() => {
    let cancelled = false;

    void fetchMapJson<Record<string, { name?: string }>>(
      `/${mapId}/data/trade`,
      { sessionToken }
    )
      .then((guilds) => {
        if (cancelled) return;

        const map: Record<string, string> = {};
        for (const [id, g] of Object.entries(guilds)) {
          map[id] = g.name ?? id;
        }
        guildNameCacheRef.current = map;
      })
      .catch(() => {
        if (!cancelled) {
          guildNameCacheRef.current = {};
        }
      });

    return () => {
      cancelled = true;
    };
  }, [mapId, sessionToken]);

  return guildNameCacheRef;
}
