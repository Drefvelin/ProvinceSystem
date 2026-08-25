"use client";

import { useEffect, useRef, useState } from "react";

import type { MapId } from "@/app/components/map/types";
import {
  buildProvinceIndexFromGrid,
  deserializeProvinceIdGrid,
  type ProvinceIndex,
} from "@/app/lib/map/editor/buildProvinceIndex";
import {
  fetchEditorProvinceIndex,
  fetchEditorProvinces,
  MapAccessError,
} from "@/lib/map/api";

async function gunzipProvinceIndexGrid(buffer: ArrayBuffer): Promise<ArrayBuffer> {
  if (typeof DecompressionStream === "undefined") {
    throw new Error("gzip decompression not supported");
  }
  const stream = new Blob([buffer])
    .stream()
    .pipeThrough(new DecompressionStream("gzip"));
  return await new Response(stream).arrayBuffer();
}

function loadErrorMessage(err: unknown): string {
  if (err instanceof MapAccessError) {
    return err.detail || err.message;
  }
  if (err instanceof Error) {
    return err.message;
  }
  return "Failed to load province index";
}

export type EditorProvinceIndexCallbacks = {
  onCatalogLoaded?: () => void;
  onIndexLoaded?: () => void;
};

export function useEditorProvinceIndex(
  mapId: MapId,
  sessionToken: string | null,
  enabled = true,
  callbacks?: EditorProvinceIndexCallbacks
): {
  index: ProvinceIndex | null;
  loading: boolean;
  error: string | null;
} {
  const [index, setIndex] = useState<ProvinceIndex | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const callbacksRef = useRef(callbacks);

  callbacksRef.current = callbacks;

  useEffect(() => {
    if (!enabled || !sessionToken) {
      setIndex(null);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      setIndex(null);

      try {
        const provincesPromise = fetchEditorProvinces(mapId, sessionToken);
        const gridPromise = fetchEditorProvinceIndex(mapId, sessionToken);

        const { provinces } = await provincesPromise;
        if (cancelled) return;
        callbacksRef.current?.onCatalogLoaded?.();

        const gridBytes = await gridPromise;
        if (cancelled) return;

        const payload = await gunzipProvinceIndexGrid(gridBytes);
        const { width, height, ids } = deserializeProvinceIdGrid(payload);
        const built = buildProvinceIndexFromGrid(provinces, width, height, ids);

        if (!cancelled) {
          setIndex(built);
          setLoading(false);
          callbacksRef.current?.onIndexLoaded?.();
        }
      } catch (err) {
        if (!cancelled) {
          setIndex(null);
          setLoading(false);
          setError(loadErrorMessage(err));
        }
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [mapId, sessionToken, enabled]);

  return { index, loading, error };
}
