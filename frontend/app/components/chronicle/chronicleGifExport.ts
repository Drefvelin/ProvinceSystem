"use client";

import { encodeGif, type GifSourceFrame } from "@/app/lib/map/gif/encodeGif";
import {
  expandChronicleBorderMask,
  type ChronicleBorderMask,
} from "../../lib/map/chronicleBorderMask";
import {
  CHRONICLE_WATERMARK_TEXT,
  chronicleGifLabelLayout,
  chronicleGifMarkerLayout,
  chronicleGifTransform,
  chronicleWatermarkLayout,
  type ChronicleGifTransform,
} from "../../lib/map/chronicleGifFrame";
import { LABEL_INK, type ProvinceCentroids } from "../../lib/mapLabels";
import { resolveMarkerImageSrc, type MapMarker } from "../../lib/mapMarkers";
import {
  buildWarCampaignPathPair,
  warLineStrokeStyle,
} from "../../lib/warCampaignLine";
import type { WarExport } from "../map/types";
import type { ChronicleFrameLayers } from "./chronicleLayers";

/**
 * The canvas half of the GIF export: it flattens the studio's layer *stack* —
 * an `<img>`, a fill canvas, a border canvas, three SVG/DOM overlays, each
 * positioned by CSS and the viewport transform — into one square raster per
 * day, then hands the pile to the encoder.
 *
 * Two things drive every decision in here.
 *
 * The GIF is always the whole map square, never the pan/zoom viewport. What
 * the user framed on screen is a reading aid; a shared timelapse that starts
 * half-scrolled is a bug report. So nothing in this module reads
 * `useMapViewport` — the only transform is `chronicleGifTransform`.
 *
 * And it must not wedge the tab. Fourteen days at 1080² is 65 MB of pixels
 * moved through `getImageData` before the encoder has even started, and the
 * whole thing runs on the main thread; without a yield between days the
 * progress text never repaints and the studio looks hung for the entire run.
 * Every loop below yields.
 *
 * There is no error boundary anywhere under `app/`, so a throw here would blank
 * the page rather than fail the button. Everything that touches day-file data
 * is guarded, and the caller is expected to keep the whole call in a try/catch
 * that lands in state.
 */

type AnyCanvas = OffscreenCanvas | HTMLCanvasElement;
type AnyCanvasContext =
  | OffscreenCanvasRenderingContext2D
  | CanvasRenderingContext2D;

export type ChronicleGifExportFrame = {
  day: string;
  /** The day's painted ownership, or null when the fill layer is off. */
  image: ImageBitmap | null;
  layers: ChronicleFrameLayers;
};

export type ChronicleGifProgress =
  | { phase: "render"; completed: number; total: number; day: string }
  | { phase: "encode"; completed: number; total: number };

export type ChronicleGifExportOptions = {
  frames: ChronicleGifExportFrame[];
  /** Square edge of the exported GIF, from `CHRONICLE_GIF_SIZES`. */
  size: number;
  mapW: number;
  mapH: number;
  /**
   * The base map `<img>` already decoded in the page. Re-fetching it would cost
   * a second copy of a multi-megabyte authenticated asset for no gain; null
   * simply leaves the parchment out rather than failing the export.
   */
  baseImage: HTMLImageElement | null;
  /** The studio's `CHRONICLE_FILL_OPACITY`, so the GIF matches the preview. */
  fillOpacity: number;
  delayMs: number;
  loop: boolean;
  centroids: ProvinceCentroids | null;
  onProgress?: (progress: ChronicleGifProgress) => void;
  signal?: AbortSignal;
};

/**
 * Palette literals from `app/internal/globals.css`. A canvas takes no CSS
 * variables and no `color-mix()`, so the two the export needs are restated
 * here; they are stable brand colours, not theme state.
 */
const CREAM = "#e8e4d9";
const INK_SCRIM = "rgba(15, 28, 22, 0.62)";
const MARKER_HALO = "rgba(15, 28, 22, 0.85)";
/** `LABEL_HALO` from `mapLabels`, as a translucent backing for dark serif ink. */
const LABEL_HALO_RGBA = "rgba(232, 228, 217, 0.7)";

const LOGO_SRC = "/logo.png";

export class ChronicleGifCancelled extends Error {
  constructor() {
    super("GIF export cancelled");
    this.name = "ChronicleGifCancelled";
  }
}

export function isChronicleGifCancelled(err: unknown): boolean {
  return err instanceof ChronicleGifCancelled;
}

/** Same fallback ladder as `chronicleRenderTarget.ts`. */
function createCanvas(width: number, height: number): AnyCanvas {
  if (typeof OffscreenCanvas !== "undefined") {
    return new OffscreenCanvas(width, height);
  }
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  return canvas;
}

function context2d(canvas: AnyCanvas): AnyCanvasContext {
  // Every frame ends in a `getImageData`, which is the one access pattern that
  // makes a GPU-backed canvas pay a full readback each time.
  const ctx = canvas.getContext("2d", {
    willReadFrequently: true,
  } as CanvasRenderingContext2DSettings) as AnyCanvasContext | null;
  if (!ctx) throw new Error("2D canvas context unavailable");
  return ctx;
}

/** Lets the browser repaint and lets the user click Pause. */
function yieldToEventLoop(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

function throwIfAborted(signal: AbortSignal | undefined): void {
  if (signal?.aborted) throw new ChronicleGifCancelled();
}

/**
 * Marker icons are a handful of PNGs shared by hundreds of pins across every
 * day, so they are loaded once per export and kept. A failed load resolves to
 * null instead of rejecting: a missing icon is one pin without art, not a dead
 * export.
 */
function loadImages(sources: string[]): Promise<Map<string, HTMLImageElement>> {
  const unique = Array.from(new Set(sources));
  return Promise.all(
    unique.map(
      (src) =>
        new Promise<[string, HTMLImageElement | null]>((resolve) => {
          const img = new Image();
          img.onload = () => resolve([src, img]);
          img.onerror = () => resolve([src, null]);
          img.src = src;
        })
    )
  ).then((entries) => {
    const map = new Map<string, HTMLImageElement>();
    for (const [src, img] of entries) if (img) map.set(src, img);
    return map;
  });
}

/**
 * Borders arrive as a 1-bit mask at the province grid's own 1600² resolution.
 * They are expanded onto a scratch canvas at that resolution and scaled down
 * with smoothing *off*, which is the same nearest-neighbour magnification
 * `ChronicleBorderCanvas` gets from `image-rendering: pixelated` — bilinear
 * downsampling turns the 3-px seam into a grey haze that the GIF's palette
 * then posterises into blotches.
 *
 * Consecutive days with an unchanged nation file share one mask object, so
 * caching on identity means a quiet stretch expands nothing at all.
 */
class BorderScratch {
  private canvas: AnyCanvas | null = null;
  private ctx: AnyCanvasContext | null = null;
  private imageData: ImageData | null = null;
  private drawn: ChronicleBorderMask | null = null;

  draw(
    target: AnyCanvasContext,
    mask: ChronicleBorderMask,
    transform: ChronicleGifTransform
  ): void {
    if (
      !this.canvas ||
      this.canvas.width !== mask.width ||
      this.canvas.height !== mask.height
    ) {
      this.canvas = createCanvas(mask.width, mask.height);
      this.ctx = context2d(this.canvas);
      this.imageData = null;
      this.drawn = null;
    }
    const ctx = this.ctx!;
    if (!this.imageData) {
      this.imageData = ctx.createImageData(mask.width, mask.height);
      this.drawn = null;
    }
    if (this.drawn !== mask) {
      expandChronicleBorderMask(mask, this.imageData.data);
      ctx.putImageData(this.imageData, 0, 0);
      this.drawn = mask;
    }

    const smoothing = target.imageSmoothingEnabled;
    target.imageSmoothingEnabled = false;
    target.drawImage(
      this.canvas as CanvasImageSource,
      transform.offsetX,
      transform.offsetY,
      transform.drawWidth,
      transform.drawHeight
    );
    target.imageSmoothingEnabled = smoothing;
  }
}

/**
 * Resolves the site's font stacks for canvas use. Next's font loader mints a
 * hashed family name into a CSS variable, and `ctx.font` will not read a
 * `var()` — it silently falls back to a 10 px sans, which is how a whole
 * export ends up in the wrong typeface with no error.
 */
function fontStacks(): { serif: string; sans: string } {
  let fraunces = "";
  let sourceSans = "";
  try {
    const style = getComputedStyle(document.body);
    fraunces = style.getPropertyValue("--font-fraunces").trim();
    sourceSans = style.getPropertyValue("--font-source-sans").trim();
  } catch {
    // A detached or restricted document: the generic stacks below still read.
  }
  return {
    serif: [fraunces, "Fraunces", "Georgia", "serif"].filter(Boolean).join(", "),
    sans: [sourceSans, "system-ui", "sans-serif"].filter(Boolean).join(", "),
  };
}

function drawWarLines(
  ctx: AnyCanvasContext,
  wars: WarExport[],
  centroids: ProvinceCentroids | null,
  transform: ChronicleGifTransform
): void {
  if (!wars.length) return;
  ctx.save();
  // Working in map coordinates keeps the stroke widths and dash arrays the SVG
  // layer uses meaningful: they are map-space numbers there too, scaled by the
  // `viewBox`, and restating them in export pixels would drift from that layer
  // the moment either changes.
  ctx.translate(transform.offsetX, transform.offsetY);
  ctx.scale(transform.scale, transform.scale);
  ctx.lineCap = "butt";
  ctx.lineJoin = "round";

  for (const war of wars) {
    let pair;
    try {
      pair = buildWarCampaignPathPair(war, centroids);
    } catch {
      // One malformed war must not cost the other thirteen days their export.
      continue;
    }
    for (const [d, phase] of [
      [pair.remainingD, "remaining"],
      [pair.progressedD, "progressed"],
    ] as const) {
      if (!d) continue;
      const style = warLineStrokeStyle(phase);
      ctx.globalAlpha = style.opacity;
      ctx.strokeStyle = style.dashColor;
      ctx.lineWidth = style.dashWidth;
      ctx.setLineDash(
        style.dashArray
          .split(/[\s,]+/)
          .map(Number)
          .filter((n) => Number.isFinite(n) && n > 0)
      );
      try {
        ctx.stroke(new Path2D(d));
      } catch {
        // `Path2D` rejects a malformed `d` by throwing; skip that stroke.
      }
    }
  }

  ctx.setLineDash([]);
  ctx.globalAlpha = 1;
  ctx.restore();
}

function drawMarkers(
  ctx: AnyCanvasContext,
  markers: MapMarker[],
  icons: Map<string, HTMLImageElement>,
  transform: ChronicleGifTransform,
  sansStack: string
): void {
  if (!markers.length) return;

  // Icons first, then every chip, so a pin never lands on top of a name that a
  // neighbouring pin owns. `MapMarkerLayer` gets the same ordering for free
  // from the DOM's paint order plus its z-index.
  const chips: { marker: MapMarker; layout: NonNullable<ReturnType<typeof chronicleGifMarkerLayout>> }[] =
    [];

  ctx.save();
  ctx.imageSmoothingEnabled = false;
  for (const marker of markers) {
    const layout = chronicleGifMarkerLayout(transform, marker);
    if (!layout) continue;
    const icon = icons.get(resolveMarkerImageSrc(marker.kind, marker.markerSize));
    if (icon) {
      ctx.drawImage(icon, layout.iconX, layout.iconY, layout.iconSize, layout.iconSize);
    }
    if (!marker.showLabelOnlyOnHover && marker.label) {
      chips.push({ marker, layout });
    }
  }
  ctx.restore();

  if (!chips.length) return;
  ctx.save();
  ctx.textAlign = "center";
  ctx.textBaseline = "alphabetic";
  ctx.lineJoin = "round";
  ctx.miterLimit = 2;
  for (const { marker, layout } of chips) {
    ctx.font = `600 ${layout.fontSize}px ${sansStack}`;
    // The on-screen chip is a rounded box with a border and a `color-mix`
    // background, none of which survives a 256-colour palette cleanly. A dark
    // halo does the same job — separating cream text from snow and desert —
    // in colours the quantiser already has to keep for the ink.
    ctx.strokeStyle = MARKER_HALO;
    ctx.lineWidth = layout.haloWidth;
    ctx.strokeText(marker.label, layout.labelCenterX, layout.labelBaselineY);
    ctx.fillStyle = CREAM;
    ctx.fillText(marker.label, layout.labelCenterX, layout.labelBaselineY);
  }
  ctx.restore();
}

function drawNationLabels(
  ctx: AnyCanvasContext,
  layers: ChronicleFrameLayers,
  transform: ChronicleGifTransform,
  serifStack: string
): void {
  if (!layers.labels.length) return;
  ctx.save();
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.lineJoin = "round";
  ctx.miterLimit = 2;

  for (const label of layers.labels) {
    const layout = chronicleGifLabelLayout(transform, label);
    if (!layout) continue;
    ctx.save();
    ctx.translate(layout.centerX, layout.centerY);
    ctx.rotate(layout.angleRad);
    ctx.font = `500 ${layout.fontSize}px ${serifStack}`;
    // The SVG layer sets the name in bare ink and relies on the parchment
    // underneath. Painted ownership at 0.88 can be as dark as the ink, so the
    // export adds the pale halo the label module already defines rather than
    // letting a realm name vanish into its own colour.
    ctx.strokeStyle = LABEL_HALO_RGBA;
    ctx.lineWidth = layout.haloWidth;
    ctx.strokeText(layout.text, 0, 0);
    ctx.fillStyle = LABEL_INK;
    ctx.fillText(layout.text, 0, 0);
    ctx.restore();
  }
  ctx.restore();
}

function drawWatermark(
  ctx: AnyCanvasContext,
  size: number,
  logo: HTMLImageElement | null,
  sansStack: string
): void {
  // Measured before the layout is computed: the scrim has to know how wide the
  // text turned out, and only the context can say.
  const probe = chronicleWatermarkLayout(size, 0);
  ctx.save();
  ctx.font = `600 ${probe.fontSize}px ${sansStack}`;
  const textWidth = ctx.measureText(CHRONICLE_WATERMARK_TEXT).width;
  const layout = chronicleWatermarkLayout(size, textWidth);

  const { scrim } = layout;
  if (scrim.width > 0 && scrim.height > 0) {
    ctx.fillStyle = INK_SCRIM;
    ctx.beginPath();
    // Ocean and snow are the two extremes the mark has to survive; a soft dark
    // plate under it settles both without hiding the map behind a hard box.
    if (typeof ctx.roundRect === "function") {
      ctx.roundRect(scrim.x, scrim.y, scrim.width, scrim.height, scrim.radius);
    } else {
      ctx.rect(scrim.x, scrim.y, scrim.width, scrim.height);
    }
    ctx.fill();
  }

  if (logo) {
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(
      logo,
      layout.logoX,
      layout.logoY,
      layout.logoSize,
      layout.logoSize
    );
  }

  ctx.font = `600 ${layout.fontSize}px ${sansStack}`;
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
  ctx.lineJoin = "round";
  ctx.miterLimit = 2;
  ctx.strokeStyle = MARKER_HALO;
  ctx.lineWidth = layout.haloWidth;
  ctx.strokeText(CHRONICLE_WATERMARK_TEXT, layout.textX, layout.textBaselineY);
  ctx.fillStyle = CREAM;
  ctx.fillText(CHRONICLE_WATERMARK_TEXT, layout.textX, layout.textBaselineY);
  ctx.restore();
}

/**
 * Whether the base map is drawable into a canvas we can read back.
 *
 * A cross-origin image with no CORS grant taints the canvas silently — the
 * `drawImage` succeeds and only the later `getImageData` throws — and once
 * tainted a canvas can never be read again, so this has to be settled on a
 * throwaway probe before any real frame is drawn. The studio asks for the base
 * map with `crossOrigin="anonymous"` precisely so this probe passes; the probe
 * is what makes the deployment where it does not still produce a GIF.
 */
function baseMapIsReadable(
  baseImage: HTMLImageElement,
  transform: ChronicleGifTransform
): boolean {
  try {
    const probe = createCanvas(1, 1);
    const ctx = context2d(probe);
    ctx.drawImage(
      baseImage,
      transform.offsetX,
      transform.offsetY,
      transform.drawWidth,
      transform.drawHeight
    );
    ctx.getImageData(0, 0, 1, 1);
    return true;
  } catch {
    return false;
  }
}

export type ChronicleGifExportResult = {
  bytes: Uint8Array;
  /**
   * True when the parchment had to be left out. A timelapse of ownership and
   * borders on a flat ground is still worth having, so this is something the
   * panel mentions rather than something the export fails on.
   */
  baseMapOmitted: boolean;
};

/**
 * Renders every day and encodes them into one GIF.
 *
 * Throws `ChronicleGifCancelled` when the signal fires. A base map that cannot
 * be read back is *not* a failure: it is detected up front and dropped from
 * the composite, and the caller is told through `baseMapOmitted`.
 */
export async function exportChronicleGif(
  options: ChronicleGifExportOptions
): Promise<ChronicleGifExportResult> {
  const {
    frames,
    size,
    mapW,
    mapH,
    baseImage,
    fillOpacity,
    delayMs,
    loop,
    centroids,
    onProgress,
    signal,
  } = options;

  if (!frames.length) throw new Error("There are no built frames to export.");

  const transform = chronicleGifTransform(mapW, mapH, size);
  const edge = transform.size;
  const canvas = createCanvas(edge, edge);
  const ctx = context2d(canvas);
  ctx.imageSmoothingQuality = "high";

  const baseUsable =
    baseImage != null && baseImage.complete && baseImage.naturalWidth > 0;
  const baseReady = baseUsable && baseMapIsReadable(baseImage, transform);

  const { serif, sans } = fontStacks();

  const iconSources = new Set<string>([LOGO_SRC]);
  for (const frame of frames) {
    for (const marker of frame.layers.markers) {
      iconSources.add(resolveMarkerImageSrc(marker.kind, marker.markerSize));
    }
  }
  const images = await loadImages(Array.from(iconSources));
  const logo = images.get(LOGO_SRC) ?? null;
  // Custom faces are still swapping in on a cold load; measuring or drawing
  // before they settle bakes the fallback metrics into the file.
  try {
    await document.fonts?.ready;
  } catch {
    // No font manager (or it rejected) — the generic stacks are already usable.
  }

  const borders = new BorderScratch();
  const sourceFrames: GifSourceFrame[] = [];

  for (let i = 0; i < frames.length; i++) {
    throwIfAborted(signal);
    const frame = frames[i]!;
    onProgress?.({
      phase: "render",
      completed: i,
      total: frames.length,
      day: frame.day,
    });

    ctx.clearRect(0, 0, edge, edge);
    // The letterbox bars and any hole in the parchment read as the map's own
    // deep-forest ground rather than as transparency the GIF cannot express.
    ctx.fillStyle = "#0f1c16";
    ctx.fillRect(0, 0, edge, edge);

    if (baseReady) {
      ctx.drawImage(
        baseImage,
        transform.offsetX,
        transform.offsetY,
        transform.drawWidth,
        transform.drawHeight
      );
    }

    if (frame.image) {
      ctx.save();
      ctx.globalAlpha = fillOpacity;
      ctx.drawImage(
        frame.image,
        transform.offsetX,
        transform.offsetY,
        transform.drawWidth,
        transform.drawHeight
      );
      ctx.restore();
    }

    if (frame.layers.borders) {
      borders.draw(ctx, frame.layers.borders, transform);
    }
    drawWarLines(ctx, frame.layers.wars, centroids, transform);
    drawMarkers(ctx, frame.layers.markers, images, transform, sans);
    drawNationLabels(ctx, frame.layers, transform, serif);
    drawWatermark(ctx, edge, logo, sans);

    let pixels: ImageData;
    try {
      pixels = ctx.getImageData(0, 0, edge, edge);
    } catch {
      // The probe already cleared the one image that arrives from another
      // origin, so reaching here means something else tainted the canvas —
      // there is nothing to drop and retry, and a half-written GIF is worse
      // than a message.
      throw new Error(
        "The browser blocked reading this frame's pixels, so the GIF cannot be built."
      );
    }
    sourceFrames.push({ data: pixels.data, delayMs });

    // Between days, not after the last one: the encode phase yields on its own.
    if (i < frames.length - 1) await yieldToEventLoop();
  }

  throwIfAborted(signal);
  onProgress?.({ phase: "encode", completed: 0, total: frames.length });
  // One more yield so "Encoding…" is on screen before the encoder takes the
  // thread; it does not yield internally.
  await yieldToEventLoop();

  const bytes = encodeGif({
    width: edge,
    height: edge,
    frames: sourceFrames,
    loop,
    onProgress: (completed: number, total: number) =>
      onProgress?.({ phase: "encode", completed, total }),
  });

  return { bytes, baseMapOmitted: baseUsable && !baseReady };
}

/**
 * Hands the finished bytes to the browser as a download. Kept here beside the
 * encoder call so the studio never has to think about object URLs — and so the
 * revoke cannot be forgotten, which leaks the whole GIF for the tab's lifetime.
 */
export function downloadGif(bytes: Uint8Array, filename: string): void {
  const blob = new Blob([bytes as unknown as BlobPart], { type: "image/gif" });
  const url = URL.createObjectURL(blob);
  try {
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.rel = "noopener";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  } finally {
    // Deferred: revoking synchronously races the navigation the click started
    // and lands as a silently cancelled download in Chromium.
    setTimeout(() => URL.revokeObjectURL(url), 60_000);
  }
}
