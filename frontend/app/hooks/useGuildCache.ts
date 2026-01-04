// hooks/useGuildCache.ts
import { useEffect, useRef } from "react";

export function useGuildCache(mapId: "main" | "dev") {
  const guildNameCacheRef = useRef<Record<string, string>>({});

  useEffect(() => {
    let cancelled = false;

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/${mapId}/data/trade`)
      .then(res => res.json())
      .then((guilds) => {
        if (cancelled) return;

        const map: Record<string, string> = {};
        for (const [id, g] of Object.entries(guilds)) {
          map[id] = (g as any).name ?? id;
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
  }, [mapId]);

  return guildNameCacheRef;
}
