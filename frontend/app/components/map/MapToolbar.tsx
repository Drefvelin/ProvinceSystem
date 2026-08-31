"use client";

import { useEffect, useRef, useState } from "react";
import type { MapId, MapMode } from "./types";

const panelClass =
  "rounded-lg border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-moss)_35%,var(--tfmc-forest-deep))] shadow-lg";

const BASE_MODE_OPTIONS: { value: MapMode; label: string }[] = [
  { value: "nation", label: "Nation Map" },
  { value: "county", label: "County Map" },
  { value: "duchy", label: "Duchy Map" },
  { value: "kingdom", label: "Kingdom Map" },
  { value: "empire", label: "Empire Map" },
];

const EXTRA_MODE_OPTIONS: { value: MapMode; label: string }[] = [
  { value: "terrain", label: "Terrain" },
  { value: "fertility", label: "Fertility" },
  { value: "trade", label: "Trade" },
  { value: "prosperity", label: "Prosperity" },
  { value: "infestation", label: "Infestation" },
];

type MapToolbarProps = {
  mapId: MapId;
  mapType: MapMode;
  onMapTypeChange: (mode: MapMode) => void;
  variant?: "sidebar" | "mobile" | "bar";
  /**
   * When present, only these modes are offered. Used by chronicle mode, which
   * passes the keys of `CHRONICLE_MODE_SOURCE`: eight of the ten modes have no
   * per-day capture, and an unreachable option is better than an option that
   * would render today's data under a past date.
   *
   * Omitted on the live map, which is the only other caller, and the omission
   * is what keeps the live toolbar byte-for-byte what it was.
   */
  availableModes?: Set<MapMode>;
};

export default function MapToolbar({
  mapId,
  mapType,
  onMapTypeChange,
  variant = "sidebar",
  availableModes,
}: MapToolbarProps) {
  const isMobile = variant === "mobile";
  const isBar = variant === "bar";
  const isSidebar = variant === "sidebar";

  const allOptions = [
    ...BASE_MODE_OPTIONS,
    ...(mapId === "main" || mapId === "dev" ? EXTRA_MODE_OPTIONS : []),
  ];
  // `undefined` means "no restriction" and must not narrow anything: the live
  // map passes nothing and gets the identical list it has always got.
  const options = availableModes
    ? allOptions.filter((opt) => availableModes.has(opt.value))
    : allOptions;

  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: PointerEvent) {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  if (isSidebar) {
    const selected = options.find((o) => o.value === mapType);
    return (
      <div ref={rootRef} className={`${panelClass} relative p-2`}>
        <div className="flex w-full items-center justify-between gap-2 px-1 py-0.5">
          <span className="truncate text-xs font-semibold uppercase tracking-wide text-[var(--tfmc-stone)]">
            Map mode <span className="text-[var(--tfmc-cream)]">— {selected?.label ?? mapType}</span>
          </span>
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            aria-label="Toggle map mode options"
            className="flex shrink-0 items-center justify-center rounded-md p-1"
          >
            <svg
              viewBox="0 0 20 20"
              fill="none"
              className={`h-4 w-4 text-[var(--tfmc-stone)] transition-transform ${open ? "rotate-180" : ""}`}
            >
              <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
        {open ? (
          <div className={`${panelClass} absolute left-0 right-0 top-full z-20 mt-1 max-h-64 overflow-auto p-1`}>
            {options.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  onMapTypeChange(opt.value);
                  setOpen(false);
                }}
                className={`block w-full rounded-md px-2 py-1.5 text-left text-sm ${
                  opt.value === mapType
                    ? "bg-[color-mix(in_srgb,var(--tfmc-cream)_92%,transparent)] text-[var(--tfmc-forest-deep)]"
                    : "text-[var(--tfmc-cream)] hover:bg-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)]"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div
      className={`${panelClass} ${
        isMobile ? "sticky top-[calc(var(--tfmc-header-h)+0.5rem)] z-20 p-3" : "p-3 sm:p-4"
      }`}
    >
      <h2
        className={`mb-2 font-semibold uppercase tracking-wide text-[var(--tfmc-stone)] text-xs sm:text-sm`}
      >
        Map mode
      </h2>
      <select
        value={mapType}
        onChange={(e) => onMapTypeChange(e.target.value as MapMode)}
        className={`w-full min-h-11 rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_15%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-cream)_92%,transparent)] px-3 text-base text-[var(--tfmc-forest-deep)] focus:outline-none focus:ring-2 focus:ring-[var(--tfmc-accent)] sm:py-2 sm:text-sm ${
          isMobile || isBar ? "" : ""
        }`}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
