import { useEffect, useState } from "react";

import type { MapId, MapMode } from "../components/map/types";
import type { TitleEntity, TitleLayers } from "../lib/titleProvinces";
import { fetchMapJson } from "@/lib/map/api";
import { isChronicleStaticMode } from "../lib/map/chronicleDayModes";

const tierCache = new Map<string, Record<string, TitleEntity>>();

/**
 * The day is part of the key even though every tier `fetchTier` fetches is live.
 *
 * `/{mapId}/data/{tier}` is **live** data and this cache is module-level, so it
 * survives client-side navigation from the live map onto a stored day. That is
 * safe today, and the reason is a product fact rather than an accident: the
 * only tiers `EXTRA_FETCHES` ever asks for are `county`, `duchy` and `kingdom`,
 * and all three are *static* — de jure structure that does not change day to
 * day, so their live answer is also their historical one. See
 * `CHRONICLE_STATIC_MODES` in `app/lib/map/chronicleDayModes`.
 *
 * `empire` is the one title tier that *is* game state, and it never reaches
 * this function: it is the active tier, resolved from the day's own captured
 * `empire.json` through `CHRONICLE_MODE_SOURCE` and handed in as `regionData`.
 * So an empire map on a stored day draws that day's empires over live
 * county/duchy/kingdom boundaries, which is correct.
 *
 * The day stays in the key anyway. If a tier that *does* vary is ever added to
 * `EXTRA_FETCHES`, a shared cache entry would serve one day's fetch to another
 * under a date banner; keying on the day costs one template literal and makes
 * that class of bug impossible.
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

  // Deliberately live even under a day: `assertStaticTier` is the guard that
  // this stays true, and it throws rather than silently fetching today's data
  // for a tier someone has since made day-varying.
  assertStaticTier(tier, day);
  const data = await fetchMapJson<Record<string, TitleEntity>>(
    `/${mapId}/data/${tier}`,
    { sessionToken }
  );
  tierCache.set(key, data);
  return data;
}

/**
 * The live-leak tripwire. Every tier this hook fetches directly must be one the
 * chronicle classifies as static; anything else would render today's boundaries
 * under a past date. Throwing lands in the effect's `.catch`, which logs and
 * clears the layers — a missing tier layer, not fabricated history.
 */
function assertStaticTier(tier: string, day: string | null): void {
  if (day === null) return;
  if (isChronicleStaticMode(tier)) return;
  throw new Error(
    `useTitleLayerData refuses to fetch live "${tier}" under chronicle day ${day}`
  );
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
