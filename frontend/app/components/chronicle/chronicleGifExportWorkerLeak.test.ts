/**
 * @vitest-environment jsdom
 *
 * Regression coverage for the worker-leak review finding: `exportChronicleGif`
 * spawns its `encodeSession` before the render loop, but nothing terminated
 * that worker (and every frame already transferred to it) if the loop threw
 * before reaching a successful `finish()` — a tainted-canvas `getImageData`
 * throw, an aborted signal, or any layer-painter throw all left a live
 * worker parked for the rest of the tab's life, with a retried export
 * spawning another one alongside it.
 *
 * This drives the real `exportChronicleGif` through a fake `Worker` (the
 * same `FakeWorker` shape `gifEncodeWorkerClient.test.ts` uses) and a fake
 * canvas 2D context whose `getImageData` always throws — the same failure
 * mode the module's own tainted-canvas comment describes — to force an exit
 * out of the render loop after the worker has already been spawned.
 */

import { afterEach, describe, expect, it, vi } from "vitest";

import { EMPTY_CHRONICLE_LAYERS } from "./chronicleLayers";
import { exportChronicleGif } from "./chronicleGifExport";
import type { GifWorkerRequest } from "../../lib/map/gif/gifEncode.worker";

class FakeWorker {
  static instances: FakeWorker[] = [];
  readonly posted: GifWorkerRequest[] = [];
  terminated = false;
  private readonly listeners: Record<string, Array<(event: unknown) => void>> = {
    message: [],
    error: [],
  };

  constructor() {
    FakeWorker.instances.push(this);
  }

  postMessage(message: GifWorkerRequest): void {
    this.posted.push(message);
  }

  addEventListener(type: string, listener: (event: unknown) => void): void {
    this.listeners[type]?.push(listener);
  }

  removeEventListener(type: string, listener: (event: unknown) => void): void {
    const list = this.listeners[type];
    if (!list) return;
    const i = list.indexOf(listener);
    if (i >= 0) list.splice(i, 1);
  }

  terminate(): void {
    this.terminated = true;
  }
}

/** Every ctx method call this render pass reaches (or doesn't — the frame
 * has no image, markers, labels or wars) is a harmless no-op except
 * `getImageData`, which always throws — the trigger this test needs. */
function makeFakeCtx(): CanvasRenderingContext2D {
  const store: Record<string, unknown> = {};
  return new Proxy(
    {},
    {
      get(_target, prop) {
        if (prop === "getImageData") {
          return () => {
            throw new Error("simulated tainted canvas");
          };
        }
        if (prop === "measureText") {
          return () => ({ width: 10 });
        }
        if (prop in store) return store[prop as string];
        return () => undefined;
      },
      set(_target, prop, value) {
        store[prop as string] = value;
        return true;
      },
    }
  ) as unknown as CanvasRenderingContext2D;
}

/** Fails synchronously — `loadImages` treats a failed icon load as "draw
 * without that icon", never as a fatal error, so this keeps the export's
 * one `await loadImages(...)` from hanging on jsdom's un-implemented image
 * loading instead of actually testing anything. */
class FakeImage {
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  set src(_value: string) {
    queueMicrotask(() => this.onerror?.());
  }
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  FakeWorker.instances = [];
});

describe("exportChronicleGif worker lifecycle on failure", () => {
  it("terminates the encode worker when the render loop throws before finish()", async () => {
    vi.stubGlobal("Worker", FakeWorker as unknown as typeof Worker);
    vi.stubGlobal("Image", FakeImage as unknown as typeof Image);
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockImplementation(
      () => makeFakeCtx()
    );

    await expect(
      exportChronicleGif({
        frames: [{ day: "2000-01-01", image: null, layers: EMPTY_CHRONICLE_LAYERS }],
        size: 64,
        mapW: 100,
        mapH: 100,
        baseImage: null,
        fillOpacity: 1,
        delayMs: 100,
        loop: true,
        centroids: null,
        stampDay: false,
      })
    ).rejects.toThrow(/blocked reading this frame's pixels/i);

    expect(FakeWorker.instances).toHaveLength(1);
    expect(FakeWorker.instances[0]!.terminated).toBe(true);
  });

  it("terminates the encode worker when the signal aborts mid-render", async () => {
    vi.stubGlobal("Worker", FakeWorker as unknown as typeof Worker);
    vi.stubGlobal("Image", FakeImage as unknown as typeof Image);
    // Never actually reached — the signal is pre-aborted, so the render loop's
    // first `throwIfAborted` fires before any canvas work happens.
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockImplementation(
      () => makeFakeCtx()
    );

    const controller = new AbortController();
    controller.abort();

    await expect(
      exportChronicleGif({
        frames: [
          { day: "2000-01-01", image: null, layers: EMPTY_CHRONICLE_LAYERS },
          { day: "2000-01-02", image: null, layers: EMPTY_CHRONICLE_LAYERS },
        ],
        size: 64,
        mapW: 100,
        mapH: 100,
        baseImage: null,
        fillOpacity: 1,
        delayMs: 100,
        loop: true,
        centroids: null,
        stampDay: false,
        signal: controller.signal,
      })
    ).rejects.toThrow(/cancelled/i);

    expect(FakeWorker.instances).toHaveLength(1);
    expect(FakeWorker.instances[0]!.terminated).toBe(true);
  });
});
