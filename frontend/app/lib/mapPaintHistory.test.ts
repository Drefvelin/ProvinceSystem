import { describe, expect, it } from "vitest";

import type { PaintShape, PaintStampShape } from "./mapPaint";
import {
  PAINT_HISTORY_LIMIT,
  canRedoPaint,
  canUndoPaint,
  commitPaintHistory,
  createPaintHistory,
  redoPaintHistory,
  undoPaintHistory,
} from "./mapPaintHistory";

function stamp(id: string): PaintStampShape {
  return {
    id,
    type: "stamp",
    color: "attack",
    createdAt: 1,
    icon: "raid",
    at: { x: 0, y: 0 },
  };
}

const a: PaintShape[] = [stamp("a")];
const ab: PaintShape[] = [stamp("a"), stamp("b")];

describe("createPaintHistory", () => {
  it("starts with nothing to undo or redo", () => {
    const history = createPaintHistory(a);
    expect(history.present).toBe(a);
    expect(canUndoPaint(history)).toBe(false);
    expect(canRedoPaint(history)).toBe(false);
  });
});

describe("commitPaintHistory", () => {
  it("pushes the previous present onto the past", () => {
    const history = commitPaintHistory(createPaintHistory(a), ab);
    expect(history.present).toBe(ab);
    expect(history.past).toEqual([a]);
    expect(canUndoPaint(history)).toBe(true);
  });

  it("is a no-op when the list is unchanged", () => {
    const before = createPaintHistory(a);
    expect(commitPaintHistory(before, a)).toBe(before);
  });

  it("caps the past at PAINT_HISTORY_LIMIT", () => {
    let history = createPaintHistory([]);
    for (let i = 0; i < PAINT_HISTORY_LIMIT + 10; i += 1) {
      history = commitPaintHistory(history, [stamp(`s${i}`)]);
    }
    expect(history.past).toHaveLength(PAINT_HISTORY_LIMIT);
  });

  it("clears the future so redo cannot skip past a new edit", () => {
    const undone = undoPaintHistory(commitPaintHistory(createPaintHistory(a), ab));
    expect(canRedoPaint(undone)).toBe(true);

    const rewritten = commitPaintHistory(undone, [stamp("c")]);
    expect(canRedoPaint(rewritten)).toBe(false);
  });
});

describe("undoPaintHistory / redoPaintHistory", () => {
  it("round-trips back to the same list", () => {
    const committed = commitPaintHistory(createPaintHistory(a), ab);
    const undone = undoPaintHistory(committed);
    expect(undone.present).toBe(a);

    const redone = redoPaintHistory(undone);
    expect(redone.present).toBe(ab);
    expect(canRedoPaint(redone)).toBe(false);
  });

  it("no-ops at the ends of the stack", () => {
    const empty = createPaintHistory(a);
    expect(undoPaintHistory(empty)).toBe(empty);
    expect(redoPaintHistory(empty)).toBe(empty);
  });
});
