import { describe, expect, it } from "vitest";

import {
  CHRONICLE_DAY_PATTERN,
  chronicleDayHref,
  chronicleStudioHref,
  isValidChronicleDay,
  liveMapHref,
} from "./chronicleDayRoute";

describe("isValidChronicleDay", () => {
  it("accepts a well-formed day", () => {
    expect(isValidChronicleDay("2026-08-25")).toBe(true);
    expect(isValidChronicleDay("0001-01-01")).toBe(true);
  });

  it("rejects anything that is not exactly YYYY-MM-DD", () => {
    for (const bad of [
      "",
      "2026-8-25",
      "2026-08-5",
      "26-08-25",
      "2026-08-25T00:00:00Z",
      "2026-08-250",
      " 2026-08-25",
      "2026-08-25 ",
      "2026/08/25",
      "latest",
    ]) {
      expect(isValidChronicleDay(bad), bad).toBe(false);
    }
  });

  it("rejects traversal and injection shapes", () => {
    for (const bad of [
      "..",
      "../../etc/passwd",
      "2026-08-25/../../secret",
      "%2e%2e%2f",
      "2026-08-25?x=1",
      "__proto__",
    ]) {
      expect(isValidChronicleDay(bad), bad).toBe(false);
    }
  });

  it("rejects non-strings", () => {
    for (const bad of [null, undefined, 20260825, ["2026-08-25"], {}]) {
      expect(isValidChronicleDay(bad)).toBe(false);
    }
  });

  it("is anchored at both ends", () => {
    // A newline is the classic way an unanchored `$` still matches.
    expect(CHRONICLE_DAY_PATTERN.test("2026-08-25\nrm -rf")).toBe(false);
    expect(CHRONICLE_DAY_PATTERN.test("x2026-08-25")).toBe(false);
  });

  it("is not a calendar check, only a shape check", () => {
    // Whether the day exists is the chronicle index's job, not this regex's.
    expect(isValidChronicleDay("2026-02-31")).toBe(true);
    expect(isValidChronicleDay("2026-13-99")).toBe(true);
  });

  it("has no lastIndex state to leak between calls", () => {
    // A `/g` regex would alternate true/false here.
    expect(isValidChronicleDay("2026-08-25")).toBe(true);
    expect(isValidChronicleDay("2026-08-25")).toBe(true);
  });
});

describe("chronicle route hrefs", () => {
  it("maps the dev map id onto its public segment", () => {
    expect(liveMapHref("main")).toBe("/map/main");
    expect(liveMapHref("dev")).toBe("/map/r3b1rth");
    expect(chronicleStudioHref("main")).toBe("/map/main/chronicle");
    expect(chronicleStudioHref("dev")).toBe("/map/r3b1rth/chronicle");
  });

  it("builds a day href under the studio route", () => {
    expect(chronicleDayHref("main", "2026-08-25")).toBe(
      "/map/main/chronicle/2026-08-25"
    );
    expect(chronicleDayHref("dev", "2026-08-25")).toBe(
      "/map/r3b1rth/chronicle/2026-08-25"
    );
  });

  it("encodes the day segment rather than interpolating it raw", () => {
    // Never reachable through a validated day, but the helper must not be the
    // weak link if some future caller passes something unvalidated.
    expect(chronicleDayHref("main", "../secret")).toBe(
      "/map/main/chronicle/..%2Fsecret"
    );
  });
});
