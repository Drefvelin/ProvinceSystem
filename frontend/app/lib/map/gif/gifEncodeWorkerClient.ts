"use client";

/**
 * Browser-side driver for `gifEncode.worker.ts`.
 *
 * `encodeGif` stays a synchronous, dependency-free function so `encodeGif.test.ts`
 * keeps calling it directly under node — everything that knows a `Worker`
 * exists lives here instead. `chronicleGifExport.ts` streams each rendered
 * frame to the worker the moment it is painted: `postFrame` transfers the
 * frame's backing `ArrayBuffer` rather than copying it, so a frame's pixels
 * leave the main thread as soon as the worker has them instead of sitting in
 * a `sourceFrames` array for the whole render pass — the second half of the
 * "frames retained without a ceiling" finding, alongside the byte-ceiling
 * refusal `chronicleGifExport.ts` checks before rendering starts.
 *
 * Turbopack (this project's bundler, see `next.config.ts`) resolves
 * `new Worker(new URL("./gifEncode.worker.ts", import.meta.url))` the same
 * way webpack does — see the "Magic Comments" section of Next's Turbopack
 * docs and its `new-worker` test fixtures — so this takes the real-Worker
 * path rather than a main-thread chunked-await fallback.
 */

import type { GifSourceFrame } from "./encodeGif";
import type { GifWorkerRequest, GifWorkerResponse } from "./gifEncode.worker";

export type GifEncodeSession = {
  /**
   * Transfers the frame's pixel buffer to the worker. `frame.data` is
   * detached the instant this returns — the caller must not read or reuse it
   * afterward, which is exactly the point: the main thread's copy is gone.
   */
  postFrame(frame: GifSourceFrame): void;
  /**
   * Signals that no more frames are coming and resolves with the finished
   * GIF. Idempotent — a second call does not re-post the "finish" message,
   * it just returns the same promise the first call did.
   */
  finish(): Promise<Uint8Array>;
  /**
   * Terminates the worker immediately and abandons whatever it was holding —
   * every frame transferred to it so far included. For any exit out of the
   * caller's render loop other than a successful `finish()`: a thrown error,
   * a tainted canvas, an abort caught before `finish()` was even called.
   * Without this, an exception between spawning the session and awaiting
   * `finish()` leaves a live worker (and every frame it already owns) parked
   * for the rest of the tab's life, and a retried export spawns another.
   * Idempotent and safe to call after the session has already settled on its
   * own (done/error/abort) — a no-op then, same as a second `postFrame`.
   */
  terminate(): void;
};

export type StartGifEncodeWorkerOptions = {
  width: number;
  height: number;
  loop: boolean;
  onProgress?: (framesDone: number, frameTotal: number) => void;
  signal?: AbortSignal;
};

function abortError(signal: AbortSignal | undefined): Error {
  const reason = signal?.reason;
  if (reason instanceof Error) return reason;
  return new DOMException("GIF encoding was cancelled", "AbortError");
}

/**
 * Spawns `gifEncode.worker.ts` and returns a small session over it. The
 * worker is terminated exactly once — on `done`, on `error`, or on abort —
 * whichever comes first; every path funnels through `settle`.
 */
export function startGifEncodeWorker(
  options: StartGifEncodeWorkerOptions
): GifEncodeSession {
  const { width, height, loop, onProgress, signal } = options;

  const worker = new Worker(new URL("./gifEncode.worker.ts", import.meta.url), {
    type: "module",
  });

  let settled = false;
  let resolveDone!: (bytes: Uint8Array) => void;
  let rejectDone!: (err: unknown) => void;
  const done = new Promise<Uint8Array>((resolve, reject) => {
    resolveDone = resolve;
    rejectDone = reject;
  });
  // `finish()` may never be called (the render loop can throw first, e.g. on
  // abort) — without this, that leaves a permanently-unobserved rejection the
  // moment `settle` below fires, which Node and browsers both report as an
  // unhandled rejection even though a real consumer never existed yet.
  done.catch(() => {});

  const cleanup = (): void => {
    worker.removeEventListener("message", onMessage);
    worker.removeEventListener("error", onError);
    signal?.removeEventListener("abort", onAbort);
  };

  const settle = (fn: () => void): void => {
    if (settled) return;
    settled = true;
    cleanup();
    worker.terminate();
    fn();
  };

  const onAbort = (): void => settle(() => rejectDone(abortError(signal)));

  const onMessage = (event: MessageEvent<GifWorkerResponse>): void => {
    const message = event.data;
    if (message.type === "progress") {
      onProgress?.(message.framesDone, message.frameTotal);
      return;
    }
    if (message.type === "done") {
      settle(() => resolveDone(new Uint8Array(message.bytes)));
    } else {
      settle(() => rejectDone(new Error(message.message)));
    }
  };

  const onError = (event: ErrorEvent): void =>
    settle(() => rejectDone(new Error(event.message || "The GIF worker failed.")));

  worker.addEventListener("message", onMessage);
  worker.addEventListener("error", onError);
  if (signal) {
    if (signal.aborted) onAbort();
    else signal.addEventListener("abort", onAbort, { once: true });
  }

  let finishRequested = false;

  return {
    postFrame(frame) {
      if (settled) return;
      const buffer = frame.data.buffer as ArrayBuffer;
      const request: GifWorkerRequest = {
        type: "frame",
        buffer,
        delayMs: frame.delayMs,
      };
      worker.postMessage(request, [buffer]);
    },
    finish() {
      if (!finishRequested) {
        finishRequested = true;
        if (!settled) {
          const request: GifWorkerRequest = { type: "finish", width, height, loop };
          worker.postMessage(request);
        }
      }
      return done;
    },
    terminate() {
      settle(() =>
        rejectDone(new DOMException("GIF encode session terminated", "AbortError"))
      );
    },
  };
}
