import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  clearDevGateBypass,
  isDevGateBypassActive,
  isDevGateBypassCode,
  setDevGateBypass,
  SITE_DEV_GATE_BYPASS_CODE,
} from "@/lib/site/devGateBypass";

function mockSessionStorage() {
  const store = new Map<string, string>();
  vi.stubGlobal("sessionStorage", {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => {
      store.set(key, value);
    },
    removeItem: (key: string) => {
      store.delete(key);
    },
    clear: () => {
      store.clear();
    },
  });
}

describe("devGateBypass", () => {
  beforeEach(() => {
    mockSessionStorage();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("matches the temporary bypass code exactly", () => {
    expect(isDevGateBypassCode(SITE_DEV_GATE_BYPASS_CODE)).toBe(true);
    expect(isDevGateBypassCode(` ${SITE_DEV_GATE_BYPASS_CODE} `)).toBe(true);
    expect(isDevGateBypassCode("TEMP-CODE-4423")).toBe(false);
    expect(isDevGateBypassCode("character-code")).toBe(false);
  });

  it("stores bypass in sessionStorage without a login session", () => {
    expect(isDevGateBypassActive()).toBe(false);
    setDevGateBypass();
    expect(isDevGateBypassActive()).toBe(true);
    clearDevGateBypass();
    expect(isDevGateBypassActive()).toBe(false);
  });
});
