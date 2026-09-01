import { afterEach, describe, expect, it, vi } from "vitest";

import { startGifEncodeWorker } from "./gifEncodeWorkerClient";
import type { GifWorkerRequest, GifWorkerResponse } from "./gifEncode.worker";

/**
 * `gifEncode.worker.ts` itself needs a real Worker/`self` global to run —
 * exactly the thing a plain node test does not have — so this covers the
 * other half: the message protocol `gifEncodeWorkerClient.ts` drives against
 * whatever `new Worker(...)` returns. A hand-written fake stands in for the
 * real `Worker` and exposes the exact surface the client touches
 * (`postMessage`, `addEventListener`/`removeEventListener`, `terminate`), so
 * these tests exercise the same code path the browser does.
 */
class FakeWorker {
  static instances: FakeWorker[] = [];
  readonly url: string;
  readonly options: unknown;
  readonly posted: Array<{ message: GifWorkerRequest; transfer?: Transferable[] }> = [];
  terminated = false;
  private readonly listeners: {
    message: Array<(event: { data: GifWorkerResponse }) => void>;
    error: Array<(event: { message: string }) => void>;
  } = { message: [], error: [] };

  constructor(url: string | URL, options?: unknown) {
    this.url = String(url);
    this.options = options;
    FakeWorker.instances.push(this);
  }

  postMessage(message: GifWorkerRequest, transfer?: Transferable[]): void {
    this.posted.push({ message, transfer });
  }

  addEventListener(type: "message" | "error", listener: any): void {
    this.listeners[type].push(listener);
  }

  removeEventListener(type: "message" | "error", listener: any): void {
    const list = this.listeners[type] as any[];
    const i = list.indexOf(listener);
    if (i >= 0) list.splice(i, 1);
  }

  terminate(): void {
    this.terminated = true;
  }

  emitMessage(data: GifWorkerResponse): void {
    for (const listener of [...this.listeners.message]) listener({ data });
  }

  emitError(message: string): void {
    for (const listener of [...this.listeners.error]) listener({ message });
  }
}

function installFakeWorker(): void {
  FakeWorker.instances = [];
  vi.stubGlobal("Worker", FakeWorker as unknown as typeof Worker);
}

afterEach(() => {
  vi.unstubAllGlobals();
});

function frame(byte: number, delayMs = 100) {
  const data = new Uint8ClampedArray([byte, byte, byte, 255]);
  return { data, delayMs };
}

describe("startGifEncodeWorker", () => {
  it("posts each frame with a transfer list, then a finish message with the encode parameters", () => {
    installFakeWorker();
    const session = startGifEncodeWorker({ width: 2, height: 3, loop: true });
    const worker = FakeWorker.instances[0]!;

    const f0 = frame(10);
    const f1 = frame(20);
    session.postFrame(f0);
    session.postFrame(f1);
    void session.finish();

    expect(worker.posted).toHaveLength(3);
    expect(worker.posted[0]!.message).toEqual({
      type: "frame",
      buffer: f0.data.buffer,
      delayMs: 100,
    });
    expect(worker.posted[0]!.transfer).toEqual([f0.data.buffer]);
    expect(worker.posted[1]!.message).toEqual({
      type: "frame",
      buffer: f1.data.buffer,
      delayMs: 100,
    });
    expect(worker.posted[2]!.message).toEqual({
      type: "finish",
      width: 2,
      height: 3,
      loop: true,
    });
  });

  it("resolves finish() with the done message's bytes and terminates the worker", async () => {
    installFakeWorker();
    const progress: Array<[number, number]> = [];
    const session = startGifEncodeWorker({
      width: 1,
      height: 1,
      loop: false,
      onProgress: (done, total) => progress.push([done, total]),
    });
    const worker = FakeWorker.instances[0]!;

    const finishPromise = session.finish();
    worker.emitMessage({ type: "progress", framesDone: 1, frameTotal: 2 });
    worker.emitMessage({ type: "progress", framesDone: 2, frameTotal: 2 });
    const bytes = new Uint8Array([1, 2, 3]).buffer;
    worker.emitMessage({ type: "done", bytes });

    await expect(finishPromise).resolves.toEqual(new Uint8Array([1, 2, 3]));
    expect(progress).toEqual([
      [1, 2],
      [2, 2],
    ]);
    expect(worker.terminated).toBe(true);
  });

  it("rejects finish() and terminates the worker on an error message", async () => {
    installFakeWorker();
    const session = startGifEncodeWorker({ width: 1, height: 1, loop: true });
    const worker = FakeWorker.instances[0]!;

    const finishPromise = session.finish();
    worker.emitMessage({ type: "error", message: "boom" });

    await expect(finishPromise).rejects.toThrow(/boom/);
    expect(worker.terminated).toBe(true);
  });

  it("rejects finish() and terminates the worker on a worker error event", async () => {
    installFakeWorker();
    const session = startGifEncodeWorker({ width: 1, height: 1, loop: true });
    const worker = FakeWorker.instances[0]!;

    const finishPromise = session.finish();
    worker.emitError("script threw");

    await expect(finishPromise).rejects.toThrow(/script threw/);
    expect(worker.terminated).toBe(true);
  });

  it("terminates the worker and rejects finish() when the signal aborts mid-stream", async () => {
    installFakeWorker();
    const controller = new AbortController();
    const session = startGifEncodeWorker({
      width: 1,
      height: 1,
      loop: true,
      signal: controller.signal,
    });
    const worker = FakeWorker.instances[0]!;

    session.postFrame(frame(5));
    controller.abort();

    expect(worker.terminated).toBe(true);

    // A frame posted after abort is a no-op — the session is already settled.
    const postedBefore = worker.posted.length;
    session.postFrame(frame(6));
    expect(worker.posted).toHaveLength(postedBefore);

    await expect(session.finish()).rejects.toThrow(/cancelled|aborted/i);
    // finish() must not resurrect a terminated worker with a stray message.
    expect(worker.posted).toHaveLength(postedBefore);
  });

  it("rejects immediately when the signal is already aborted before the worker is asked to finish", async () => {
    installFakeWorker();
    const controller = new AbortController();
    controller.abort();
    const session = startGifEncodeWorker({
      width: 1,
      height: 1,
      loop: true,
      signal: controller.signal,
    });
    const worker = FakeWorker.instances[0]!;

    expect(worker.terminated).toBe(true);
    await expect(session.finish()).rejects.toThrow(/cancelled|aborted/i);
  });

  it("terminate() kills the worker and rejects an in-flight finish(), even with no signal", async () => {
    installFakeWorker();
    const session = startGifEncodeWorker({ width: 1, height: 1, loop: true });
    const worker = FakeWorker.instances[0]!;

    session.postFrame(frame(1));
    const finishPromise = session.finish();
    expect(worker.terminated).toBe(false);

    session.terminate();

    expect(worker.terminated).toBe(true);
    await expect(finishPromise).rejects.toThrow(/terminated/i);
  });

  it("terminate() is a no-op once the session already settled on its own", async () => {
    installFakeWorker();
    const session = startGifEncodeWorker({ width: 1, height: 1, loop: true });
    const worker = FakeWorker.instances[0]!;

    const finishPromise = session.finish();
    worker.emitMessage({ type: "done", bytes: new Uint8Array([9]).buffer });
    await expect(finishPromise).resolves.toEqual(new Uint8Array([9]));

    const terminateCallsBefore = worker.terminated;
    expect(terminateCallsBefore).toBe(true);

    // Calling terminate() after a real done must not flip the resolved
    // promise into a rejection, or double-terminate in a way that throws.
    expect(() => session.terminate()).not.toThrow();
    await expect(finishPromise).resolves.toEqual(new Uint8Array([9]));
  });

  it("finish() called twice posts the finish message only once and returns the same promise", () => {
    installFakeWorker();
    const session = startGifEncodeWorker({ width: 2, height: 2, loop: false });
    const worker = FakeWorker.instances[0]!;

    const first = session.finish();
    const second = session.finish();

    expect(first).toBe(second);
    const finishMessages = worker.posted.filter((p) => p.message.type === "finish");
    expect(finishMessages).toHaveLength(1);
  });
});
