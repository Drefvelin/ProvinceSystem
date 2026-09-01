/**
 * Dedicated Worker entry point for `encodeGif`.
 *
 * This file is the one caller `encodeGif`'s, `gifLzw`'s and `gifPalette`'s
 * module docs point at: it is loaded with
 * `new Worker(new URL("./gifEncode.worker.ts", import.meta.url), { type: "module" })`
 * from `gifEncodeWorkerClient.ts`, and everything from that import down runs
 * on this thread, off the one painting the studio.
 *
 * Protocol, driven entirely by `gifEncodeWorkerClient.ts`:
 *  - `{ type: "frame" }` arrives once per rendered day, its `buffer` a
 *    transferred `ArrayBuffer` (not copied) so the studio's frame pixels move
 *    to this thread instead of living on both at once.
 *  - `{ type: "finish" }` arrives once, after the last frame, and starts the
 *    actual encode. `encodeGif`'s own `onProgress` is relayed back as
 *    `{ type: "progress" }` messages for the studio's progress bar.
 *  - The result comes back as `{ type: "done", bytes }`, `bytes` transferred
 *    the same way frames arrived, or `{ type: "error" }` if `encodeGif` threw
 *    — a worker has no `try/catch` at the call site, so an escaping throw
 *    would surface only as a silent, unresolved export.
 *
 * The project's `tsconfig.json` pulls in the `dom` lib only. Adding
 * `webworker` for this one file is not an option — the two libs declare
 * incompatible globals (`self` chief among them) and TypeScript refuses to
 * combine them. `self` is narrowed by hand instead, to just the two members
 * this file actually calls; the real worker runtime still has the rest.
 */

import { encodeGif, type GifSourceFrame } from "./encodeGif";

export type GifWorkerRequest =
  | { type: "frame"; buffer: ArrayBuffer; delayMs: number }
  | { type: "finish"; width: number; height: number; loop: boolean };

export type GifWorkerResponse =
  | { type: "progress"; framesDone: number; frameTotal: number }
  | { type: "done"; bytes: ArrayBuffer }
  | { type: "error"; message: string };

type WorkerSelf = {
  onmessage: ((event: MessageEvent<GifWorkerRequest>) => void) | null;
  postMessage: (message: GifWorkerResponse, transfer?: Transferable[]) => void;
};

const workerSelf = self as unknown as WorkerSelf;

/** Frames received so far, in arrival order — the same order the studio rendered them in. */
const frames: GifSourceFrame[] = [];

workerSelf.onmessage = (event) => {
  const message = event.data;

  if (message.type === "frame") {
    frames.push({
      data: new Uint8ClampedArray(message.buffer),
      delayMs: message.delayMs,
    });
    return;
  }

  // message.type === "finish"
  try {
    const bytes = encodeGif({
      width: message.width,
      height: message.height,
      frames,
      loop: message.loop,
      onProgress: (framesDone, frameTotal) => {
        workerSelf.postMessage({ type: "progress", framesDone, frameTotal });
      },
    });
    // `encodeGif` returns a `Uint8Array` sized to exactly its content
    // (`ByteWriter.toUint8Array` allocates fresh), so its `buffer` needs no
    // slicing before it is handed over.
    const out = bytes.buffer as ArrayBuffer;
    workerSelf.postMessage({ type: "done", bytes: out }, [out]);
  } catch (err) {
    workerSelf.postMessage({
      type: "error",
      message: err instanceof Error ? err.message : "GIF encode failed",
    });
  }
};
