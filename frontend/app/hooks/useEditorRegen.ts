"use client";

import { useCallback, useEffect, useState } from "react";

import type { MapId } from "@/app/components/map/types";
import type { MapAccessGateReason } from "@/app/components/map/MapAccessGate";
import {
  MapAccessError,
  postEditorRegen,
  staffMapAccessReason,
  type EditorTier,
} from "@/lib/map/api";

export type RegenState = "idle" | "running" | "done" | "error";

export function useEditorRegen({
  mapId,
  tier,
  sessionToken,
  dirty,
  onAccessLost,
}: {
  mapId: MapId;
  tier: EditorTier;
  sessionToken: string;
  dirty: boolean;
  onAccessLost: (reason: MapAccessGateReason) => void;
}): {
  regenState: RegenState;
  regenMessage: string | null;
  lastSavedAt: number | null;
  canRegen: boolean;
  regen: () => Promise<void>;
} {
  const [regenState, setRegenState] = useState<RegenState>("idle");
  const [regenMessage, setRegenMessage] = useState<string | null>(null);
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null);

  useEffect(() => {
    setLastSavedAt(null);
    setRegenState("idle");
    setRegenMessage(null);
  }, [mapId, tier]);

  const regen = useCallback(async () => {
    if (dirty || !lastSavedAt) return;

    setRegenState("running");
    setRegenMessage(null);

    try {
      const response = await postEditorRegen(
        mapId,
        `fullregen:${tier}`,
        sessionToken
      );
      setRegenState("done");
      setRegenMessage(
        `${response.message} Open the map viewer to preview when it finishes.`
      );
    } catch (err) {
      if (err instanceof MapAccessError && err.status === 403) {
        onAccessLost(staffMapAccessReason(err));
        setRegenState("idle");
        return;
      }
      const message =
        err instanceof MapAccessError
          ? err.detail
          : err instanceof Error
            ? err.message
            : "Failed to start regeneration";
      setRegenMessage(message);
      setRegenState("error");
    }
  }, [dirty, lastSavedAt, mapId, tier, sessionToken, onAccessLost]);

  const canRegen =
    !dirty && lastSavedAt !== null && regenState !== "running";

  return {
    regenState,
    regenMessage,
    lastSavedAt,
    canRegen,
    regen,
  };
}
