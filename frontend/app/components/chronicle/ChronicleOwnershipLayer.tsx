"use client";

import { useEffect, useMemo, useRef } from "react";

import { mapObjectsVisibilityKey } from "@/app/hooks/useMapHover";
import { visibleOwnership } from "@/app/lib/map/chronicleOwnership";
import {
  buildNationColorLut,
  paintChronicleFrameToImageData,
  type NationOwnership,
  type ProvinceIdGrid,
} from "@/app/lib/map/chroniclePaint";
import type { MapObject, RegionRecord } from "@/app/components/map/types";
import {
  DRILL_STACK_OVERLAY_OPACITY,
  HOVER_OVERLAY_OPACITY,
} from "@/app/components/map/MapCanvas";

/**
 * The chronicle's replacement for the two server-rendered nation layers.
 *
 * On the live map the coloured nation shapes and the hovered-nation highlight
 * are PNGs under `/{map}/regions/{mode}/...`, regenerated from *today's* data
 * with no per-day variant. A stored day therefore has to paint them itself, or
 * opening a date in 2025 would show 2026's borders.
 *
 * Both canvases are painted from the quarter-scale province id grid: 1600x1600
 * against a 6400x6400 map, so a border can land up to 4 map pixels from where
 * the full-resolution PNG puts it. That is a deliberate 16x memory trade, not
 * an oversight — the full-res grid would make each of these canvases a 164 MB
 * `ImageData` (328 MB for the pair, ~500 MB once the pick canvas joins them),
 * against ~10 MB each here. At the zoom levels the viewer supports the
 * difference is under a pixel on screen.
 */

type ChronicleOwnershipLayerProps = {
  /** Quarter-scale province id grid, or null while it is still loading. */
  grid: ProvinceIdGrid | null;
  /** The day's `nation.json`, already loaded by `useMapModeData`. */
  regionData: RegionRecord | null;
  /** Drill state, exactly as `MapCanvas` would have used it to pick PNGs. */
  mapObjects: MapObject[];
  /** Region the pick canvas resolved under the cursor, or null. */
  hoveredRegionId?: string | null;
  mapW: number;
  mapH: number;
};

/**
 * The backend's `_hover` PNGs are a lightness/saturation bump in the nation's
 * own hue (`display_colour.hover_rgb`). This is the same idea done cheaply:
 * mix the nation's colour toward white. Chronicle frames already paint the raw
 * stored `rgb` rather than the backend's parchment-washed display colour, so
 * matching that pipeline exactly here would not make the layers agree anyway —
 * what matters is that the hovered nation reads as clearly brighter.
 */
const HIGHLIGHT_MIX_TOWARD_WHITE = 0.45;

function highlightRgb(rgb: string | undefined): string | null {
  if (!rgb) return null;
  const parts = rgb.split(",");
  if (parts.length !== 3) return null;

  const mixed: number[] = [];
  for (const part of parts) {
    const value = Number(part.trim());
    if (!Number.isFinite(value)) return null;
    const clamped = Math.min(255, Math.max(0, value));
    mixed.push(
      Math.round(clamped + (255 - clamped) * HIGHLIGHT_MIX_TOWARD_WHITE)
    );
  }
  return mixed.join(",");
}

function paintOwnershipCanvas(
  canvas: HTMLCanvasElement | null,
  grid: ProvinceIdGrid | null,
  ownership: NationOwnership | null
): void {
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  if (!grid || !ownership) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    return;
  }

  // Resizing re-allocates the backing store; only touch it on a real change.
  if (canvas.width !== grid.width || canvas.height !== grid.height) {
    canvas.width = grid.width;
    canvas.height = grid.height;
  }

  // `paintChronicleFrameToImageData` writes every pixel, so a fresh buffer
  // needs no clearing and a reused canvas needs no clearRect.
  const imageData = ctx.createImageData(grid.width, grid.height);
  paintChronicleFrameToImageData(imageData, grid, buildNationColorLut(ownership));
  ctx.putImageData(imageData, 0, 0);
}

const canvasClass = "pointer-events-none absolute inset-0 h-full w-full";

export default function ChronicleOwnershipLayer({
  grid,
  regionData,
  mapObjects,
  hoveredRegionId = null,
  mapW,
  mapH,
}: ChronicleOwnershipLayerProps) {
  const baseCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const hoverCanvasRef = useRef<HTMLCanvasElement | null>(null);

  // The drawn state's identity. `mapObjects` gets a fresh array (and fresh
  // entry objects) on every drill reset even when nothing became visible or
  // invisible, so depending on the array itself would repaint 2.5M pixels for
  // no visible change.
  const visibilityKey = useMemo(
    () => mapObjectsVisibilityKey(mapObjects),
    [mapObjects]
  );

  /**
   * The drawn ownership for the current drill state. Computed once and used by
   * both canvases so the highlight cannot disagree with the shape underneath
   * it: `getHoverRegion` resolves a pick to whichever *visible* entry owns it,
   * and that entry is a rolled-up overlord at the top level but own-land-only
   * once drilled in. Deriving the highlight from any other source would light
   * up a drilled overlord's vassals, which the live `_hover` PNG does not.
   */
  const visible = useMemo(
    () => (regionData ? visibleOwnership(regionData, mapObjects) : null),
    // `mapObjects` is read through `visibilityKey`, which is what actually
    // changes the result.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [regionData, visibilityKey]
  );

  useEffect(() => {
    paintOwnershipCanvas(baseCanvasRef.current, grid, visible);
  }, [grid, visible]);

  useEffect(() => {
    const drawn = hoveredRegionId ? visible?.[hoveredRegionId] : null;
    const rgb = highlightRgb(drawn?.rgb);

    if (!grid || !drawn || !rgb) {
      paintOwnershipCanvas(hoverCanvasRef.current, null, null);
      return;
    }

    const highlight: NationOwnership = Object.create(null);
    highlight[hoveredRegionId!] = { rgb, provinces: drawn.provinces };
    paintOwnershipCanvas(hoverCanvasRef.current, grid, highlight);
  }, [grid, visible, hoveredRegionId]);

  // Matches `HoverOverlayImage`: a map with no measured size has nothing to
  // stretch to, so hide rather than show a stray 1600x1600 square. Hidden, not
  // unmounted — unmounting would drop the canvas nodes the paint effects above
  // hold refs to, and nothing would repaint them once the size arrived.
  const sized = mapW > 0 && mapH > 0;

  return (
    <>
      <canvas
        ref={baseCanvasRef}
        className={canvasClass}
        style={{ opacity: sized ? DRILL_STACK_OVERLAY_OPACITY : 0 }}
        aria-hidden
      />
      <canvas
        ref={hoverCanvasRef}
        className={`${canvasClass} z-10`}
        style={{ opacity: sized ? HOVER_OVERLAY_OPACITY : 0 }}
        aria-hidden
      />
    </>
  );
}
