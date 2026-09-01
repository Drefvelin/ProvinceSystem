/**
 * @vitest-environment jsdom
 *
 * Smoke coverage for the ledger panel. Before this file existed no `.tsx` in
 * the repo was imported by any test at all (`vitest.config.ts` only matched
 * `app/**\/*.test.ts` and ran node-env), so a component could stop compiling
 * — a dropped `export`, a renamed import — with the whole suite still green.
 *
 * It also pins the band cap end-to-end: `stackBreakdown` capping its return
 * value is only useful if the panel renders one `<path>`/legend entry per
 * returned key and nothing else.
 */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import LedgerChartsPanel from "./LedgerChartsPanel";
import type { LedgerChartsResult } from "./useLedgerSeries";
import type { LedgerFactionSeries, LedgerSeries } from "../../lib/map/ledgerData";
import { LEDGER_MAX_BREAKDOWN_BANDS } from "../../lib/map/ledgerSeries";

afterEach(cleanup);

const DAYS = ["2026-08-01", "2026-08-02"];

function factionSeries(bandCount: number): LedgerFactionSeries {
  const wealth: Record<string, Array<number | null>> = {};
  for (let i = 0; i < bandCount; i++) wealth[`band-${i}`] = [i + 1, i + 1];
  return {
    key: "f1|2026-08-01T00:00:00Z",
    id: "f1",
    founded_at: "2026-08-01T00:00:00Z",
    name: "Aurelia",
    rgb: "#ffffff",
    series: {
      wealth: [10, 20],
      prestige: [1, 2],
      net_income: [3, 4],
      inflation_delta: [0, 0],
      bank: [0, 0],
    },
    rank: [null, null],
    tier: [null, null],
    breakdowns: { wealth, prestige: { honour: [1, 2] } },
  };
}

function readyResult(bandCount: number): LedgerChartsResult {
  const series: LedgerSeries = {
    days: DAYS,
    server_day: [1, 2],
    captured_at: [null, null],
    complete: [true, true],
    global: { pouch_wealth: [5, 6], player_bank_wealth: [7, 8] },
    factions: [factionSeries(bandCount)],
    truncated: false,
  };
  return {
    status: "ready",
    options: [
      {
        name: "Aurelia",
        keys: ["f1|2026-08-01T00:00:00Z"],
        foundedAt: ["2026-08-01T00:00:00Z"],
        label: "Aurelia",
      },
    ],
    selections: { wealth: "Aurelia", prestige: "Aurelia", income: "Aurelia" },
    onSelect: () => {},
    series,
    seriesLoading: false,
    seriesError: null,
  };
}

describe("LedgerChartsPanel", () => {
  it("mounts the ready state and renders all three cards", () => {
    render(<LedgerChartsPanel result={readyResult(3)} cursorDay={DAYS[0]!} />);
    expect(screen.getByText("Wealth")).toBeDefined();
    expect(screen.getByText("Prestige")).toBeDefined();
    expect(screen.getByText("Income")).toBeDefined();
  });

  it("mounts every non-ready state without throwing", () => {
    for (const result of [
      { status: "loading" },
      { status: "empty" },
      { status: "no-options" },
      { status: "error", message: "boom" },
    ] as LedgerChartsResult[]) {
      const { unmount } = render(<LedgerChartsPanel result={result} cursorDay={null} />);
      unmount();
    }
  });

  it("does not mount one band per server key when the breakdown is huge", () => {
    // The hang: breakdown keys are attacker-controlled, and each one became a
    // `<path>` plus a legend `<span>` on every card.
    const { container } = render(
      <LedgerChartsPanel result={readyResult(4_000)} cursorDay={DAYS[0]!} />
    );
    // First card, first `<svg>`: the stacked wealth chart itself (the second
    // svg in the card is the separate globals strip, which is two fixed lines).
    const stack = container.firstElementChild!.querySelector("svg")!;
    const bands = stack.querySelectorAll("path");
    expect(bands.length).toBeLessThanOrEqual(LEDGER_MAX_BREAKDOWN_BANDS + 1);
    // The legend is capped with it — same key list drives both. `band-0`
    // has the smallest peak, so it is one of the folded-away bands.
    expect(screen.queryByText("band-0")).toBeNull();
  });
});
