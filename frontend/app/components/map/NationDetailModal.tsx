"use client";

import { useEffect } from "react";
import NationDetailContent from "./NationDetailContent";
import type { MapId, MapMode, RegionInfo, RegionRecord } from "./types";

type NationDetailModalProps = {
  open: boolean;
  mapId: MapId;
  mapType: MapMode;
  regionInfo: RegionInfo | null;
  regionData: RegionRecord | null;
  sessionToken?: string | null;
  onClose: () => void;
};

export default function NationDetailModal({
  open,
  mapId,
  mapType,
  regionInfo,
  regionData,
  sessionToken,
  onClose,
}: NationDetailModalProps) {
  useEffect(() => {
    if (!open) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onClose]);

  if (!open || !regionInfo) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-[color-mix(in_srgb,var(--tfmc-forest)_72%,black)]/80 p-0 backdrop-blur-[2px] md:items-center md:p-4"
      role="presentation"
      onClick={onClose}
    >
      <div
        className="flex max-h-[90vh] w-full max-w-lg flex-col gap-4 overflow-y-auto rounded-t-xl border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] border-b-0 bg-[color-mix(in_srgb,var(--tfmc-moss)_35%,var(--tfmc-forest-deep))] p-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] shadow-xl md:rounded-lg md:border-b"
        role="dialog"
        aria-modal="true"
        aria-label={regionInfo.title}
        onClick={(event) => event.stopPropagation()}
      >
        <div
          aria-hidden
          className="mx-auto mb-1 h-1 w-10 rounded-full bg-[color-mix(in_srgb,var(--tfmc-cream)_25%,transparent)] md:hidden"
        />

        <div className="flex items-start justify-between gap-3">
          <p className="text-sm font-medium uppercase tracking-wide text-[var(--tfmc-mist)]">
            Nation details
          </p>
          <button
            type="button"
            className="inline-flex min-h-11 items-center px-3 text-sm text-[var(--tfmc-stone)] transition-colors hover:text-[var(--tfmc-cream)]"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        <NationDetailContent
          mapId={mapId}
          mapType={mapType}
          regionInfo={regionInfo}
          regionData={regionData}
          sessionToken={sessionToken}
        />
      </div>
    </div>
  );
}
