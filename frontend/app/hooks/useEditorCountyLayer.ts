"use client";

import { useEffect, useState } from "react";

import type { MapId } from "@/app/components/map/types";
import type { TitleDraft } from "@/app/hooks/useEditorDraft";
import { fetchMapJson } from "@/lib/map/api";

export function useEditorCountyLayer(
  mapId: MapId,
  sessionToken: string | null,
  enabled = true
): {
  countyDraft: TitleDraft;
  loading: boolean;
  error: string | null;
  isEmpty: boolean;
} {
  const [countyDraft, setCountyDraft] = useState<TitleDraft>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || !sessionToken) {
      setCountyDraft({});
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchMapJson<TitleDraft>(`/${mapId}/data/county`, {
          sessionToken,
        });
        if (!cancelled) {
          setCountyDraft(data);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setCountyDraft({});
          setLoading(false);
          setError(
            err instanceof Error ? err.message : "Failed to load county data"
          );
        }
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [mapId, sessionToken, enabled]);

  const isEmpty = Object.keys(countyDraft).length === 0;

  return { countyDraft, loading, error, isEmpty };
}
