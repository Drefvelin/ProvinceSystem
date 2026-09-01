"use client";

import { memo, useEffect, useRef } from "react";

import {
  expandChronicleBorderMask,
  type ChronicleBorderMask,
} from "../../lib/map/chronicleBorderMask";

/**
 * Nation borders for one stored day, drawn as pixels at the grid's own
 * resolution.
 *
 * This canvas deliberately does *not* go through the fill frame's
 * `renderSize` downscale: the fill is painted at 1600, shrunk to 600-1200 and
 * then magnified by the viewport, which is exactly the double resample that
 * turned a 3-px border into a soft band. Borders keep their 1600x1600 backing
 * store, the viewport stretches it once, and `image-rendering: pixelated`
 * keeps the stretch a hard-edged magnification instead of a bilinear smear —
 * at the viewport's maximum zoom one border pixel covers ~2.4 CSS px, the
 * same ratio the live map's server-rendered overlays are shown at.
 *
 * Sits below the label layer (z-15) and above the fill canvas (z-12) so a
 * border is never painted over by the territory it encloses, and never covers
 * a realm name.
 */
function ChronicleBorderCanvas({ mask }: { mask: ChronicleBorderMask | null }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  // One RGBA scratch for whichever day is on screen — the masks themselves
  // stay packed at 1 bit per pixel; only the displayed day is ever expanded.
  const imageDataRef = useRef<ImageData | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !mask) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    if (canvas.width !== mask.width || canvas.height !== mask.height) {
      canvas.width = mask.width;
      canvas.height = mask.height;
      imageDataRef.current = null;
    }
    let imageData = imageDataRef.current;
    if (!imageData) {
      imageData = ctx.createImageData(mask.width, mask.height);
      imageDataRef.current = imageData;
    }
    // Scrubbing between days that share a fingerprint shares the mask object,
    // so this effect (keyed on `mask`) never re-expands an unchanged day.
    expandChronicleBorderMask(mask, imageData.data);
    ctx.putImageData(imageData, 0, 0);
  }, [mask]);

  if (!mask) return null;

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 z-[13] h-full w-full"
      style={{ imageRendering: "pixelated" }}
      aria-hidden
    />
  );
}

export default memo(ChronicleBorderCanvas);
