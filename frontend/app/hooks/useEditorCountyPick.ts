"use client";

import { useEffect, useMemo, useState } from "react";

import type { MapId } from "@/app/components/map/types";
import type { TitleDraft } from "@/app/hooks/useEditorDraft";
import {
  buildCountyPickIndex,
  type CountyPickIndex,
} from "@/app/lib/map/editor/buildCountyPickIndex";
import { fetchMapBlobUrl, revokeMapBlobUrl } from "@/lib/map/api";

/** @deprecated Use useEditorChildPick instead */
export function useEditorCountyPick(
  mapId: MapId,
  sessionToken: string | null,
  countyDraft: TitleDraft,
  enabled = true
): {
  countyPick: CountyPickIndex | null;
  loading: boolean;
  error: string | null;
} {
  const [imageData, setImageData] = useState<ImageData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || !sessionToken) {
      setImageData(null);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;
    let blobUrl: string | null = null;

    const load = async () => {
      setLoading(true);
      setError(null);
      setImageData(null);

      try {
        blobUrl = await fetchMapBlobUrl(`/${mapId}/mapdata/county`, sessionToken);

        if (cancelled) {
          revokeMapBlobUrl(blobUrl);
          return;
        }

        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = blobUrl;

        await new Promise<void>((resolve, reject) => {
          img.onload = () => resolve();
          img.onerror = () => reject(new Error("Failed to load county pick map"));
        });

        if (cancelled) return;

        const offscreen = document.createElement("canvas");
        offscreen.width = img.naturalWidth;
        offscreen.height = img.naturalHeight;
        const ctx = offscreen.getContext("2d");
        if (!ctx) {
          throw new Error("Canvas not available");
        }
        ctx.drawImage(img, 0, 0);
        const data = ctx.getImageData(0, 0, offscreen.width, offscreen.height);

        if (!cancelled) {
          setImageData(data);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setImageData(null);
          setLoading(false);
          setError(
            err instanceof Error ? err.message : "Failed to load county pick map"
          );
        }
      }
    };

    void load();

    return () => {
      cancelled = true;
      revokeMapBlobUrl(blobUrl);
    };
  }, [mapId, sessionToken, enabled]);

  const countyPick = useMemo(() => {
    if (!imageData) return null;
    return buildCountyPickIndex(countyDraft, imageData);
  }, [imageData, countyDraft]);

  return { countyPick, loading, error };
}
