import { useEffect, useState } from "react";

import type { MapId, MapMode } from "../components/map/types";
import type { TitleEntity, TitleLayers } from "../lib/titleProvinces";
import { fetchMapJson } from "@/lib/map/api";

const tierCache = new Map<string, Record<string, TitleEntity>>();

/**
 * The day is part of the key even though nothing varies it today.
 *
 * `/{mapId}/data/{tier}` is **live** data, and this cache is module-level: it
 * survives client-side navigation from the live map onto a stored day. Today
 * that is unreachable — `ACTIVE_TIER` has no `nation` key, and `trade`
 * resolves from the day's own `regionData` with no extra fetch, so `extra` is
 * empty for both chronicle modes and `fetchTier` is never called under a day.
 * The moment a title tier is added to `CHRONICLE_MODE_SOURCE` it would become
 * a silent live-data leak under a date banner. Keying on the day now costs one
 * template literal and makes that impossible.
 */
function cacheKey(mapId: MapId, tier: string, day: string | null): string {
  return `${mapId}:${day ?? "live"}:${tier}`;
}

async function fetchTier(
  mapId: MapId,
  tier: string,
  sessionToken?: string | null,
  day: string | null = null
): Promise<Record<string, TitleEntity>> {
  const key = cacheKey(mapId, tier, day);
  const cached = tierCache.get(key);
  if (cached) return cached;

  const data = await fetchMapJson<Record<string, TitleEntity>>(
    `/${mapId}/data/${tier}`,
    { sessionToken }
  );
  tierCache.set(key, data);
  return data;
}

const EXTRA_FETCHES: Partial<Record<MapMode, string[]>> = {
  duchy: ["county"],
  kingdom: ["duchy", "county"],
  empire: ["kingdom", "duchy", "county"],
};

const ACTIVE_TIER: Partial<Record<MapMode, keyof TitleLayers>> = {
  county: "county",
  duchy: "duchy",
  kingdom: "kingdom",
  empire: "empire",
  trade: "trade",
};

export function useTitleLayerData(
  mapId: MapId,
  mapType: MapMode,
  regionData: Record<string, TitleEntity> | null,
  sessionToken?: string | null,
  /** A chronicle day, or `null` for the live map. See `cacheKey`. */
  day: string | null = null
): { layers: TitleLayers | null; loading: boolean } {
  const [layers, setLayers] = useState<TitleLayers | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const activeTier = ACTIVE_TIER[mapType];
    if (!activeTier || !regionData) {
      setLayers(null);
      setLoading(false);
      return;
    }

    const extra = EXTRA_FETCHES[mapType] ?? [];
    if (extra.length === 0) {
      const next: TitleLayers = { county: {} };
      if (activeTier === "county") next.county = regionData;
      else if (activeTier === "trade") next.trade = regionData;
      setLayers(next);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);

    Promise.all(
      extra.map((tier) => fetchTier(mapId, tier, sessionToken, day))
    )
      .then((fetched) => {
        if (cancelled) return;

        const next: TitleLayers = { county: {} };
        extra.forEach((tier, index) => {
          const data = fetched[index];
          if (tier === "county") next.county = data;
          else if (tier === "duchy") next.duchy = data;
          else if (tier === "kingdom") next.kingdom = data;
        });

        if (activeTier === "duchy") next.duchy = regionData;
        else if (activeTier === "kingdom") next.kingdom = regionData;
        else if (activeTier === "empire") next.empire = regionData;

        setLayers(next);
      })
      .catch((err) => {
        if (cancelled) return;
        console.error("useTitleLayerData:", err);
        setLayers(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [mapId, mapType, regionData, sessionToken, day]);

  return { layers, loading };
}
