import { describe, expect, it } from "vitest";

import type { WarExport } from "../components/map/types";
import {
  buildSvgPathD,
  buildWarCampaignPathD,
  catmullRomSpline,
  resolveWarWaypoints,
  warLineStrokeStyle,
} from "./warCampaignLine";

const sampleWar = (overrides: Partial<WarExport> = {}): WarExport => ({
  id: "war-1",
  campaign_line_points: [
    { province_id: 10, map_x: 100, map_y: 100 },
    { province_id: 20, map_x: 200, map_y: 150 },
    { province_id: 30, map_x: 300, map_y: 120 },
    { province_id: 40, map_x: 400, map_y: 200 },
  ],
  ...overrides,
});

describe("resolveWarWaypoints", () => {
  it("resolves waypoints from campaign_line_points", () => {
    const waypoints = resolveWarWaypoints(sampleWar());
    expect(waypoints).toEqual([
      { x: 100, y: 100 },
      { x: 200, y: 150 },
      { x: 300, y: 120 },
      { x: 400, y: 200 },
    ]);
  });

  it("falls back to centroids when line points are missing", () => {
    const waypoints = resolveWarWaypoints(
      sampleWar({
        campaign_line_points: undefined,
        campaign_provinces: [10, 20, 30],
      }),
      {
        "10": { x: 50, y: 60, pixel_count: 100 },
        "20": { x: 150, y: 160, pixel_count: 100 },
        "30": { x: 250, y: 260, pixel_count: 100 },
      }
    );
    expect(waypoints).toEqual([
      { x: 50, y: 60 },
      { x: 150, y: 160 },
      { x: 250, y: 260 },
    ]);
  });

  it("prepends attacker capital when not already first", () => {
    const waypoints = resolveWarWaypoints(
      sampleWar({
        campaign_line_points: [
          { province_id: 20, map_x: 200, map_y: 150 },
          { province_id: 30, map_x: 300, map_y: 120 },
        ],
        attacker_capital: {
          province_id: 10,
          map_x: 80,
          map_y: 90,
        },
      })
    );
    expect(waypoints[0]).toEqual({ x: 80, y: 90 });
    expect(waypoints).toHaveLength(3);
  });

  it("returns empty when fewer than two points resolve", () => {
    expect(resolveWarWaypoints(sampleWar({ campaign_line_points: [] }))).toEqual(
      []
    );
    expect(
      resolveWarWaypoints(
        sampleWar({
          campaign_line_points: [{ province_id: 1, map_x: 10, map_y: 10 }],
        })
      )
    ).toEqual([]);
  });
});

describe("catmullRomSpline", () => {
  const waypoints = [
    { x: 0, y: 0 },
    { x: 100, y: 0 },
    { x: 100, y: 100 },
    { x: 0, y: 100 },
  ];

  it("resamples more densely than input waypoints", () => {
    const spline = catmullRomSpline(waypoints);
    expect(spline.length).toBeGreaterThan(waypoints.length);
  });

  it("keeps endpoints near original waypoints", () => {
    const spline = catmullRomSpline(waypoints);
    const first = spline[0];
    const last = spline[spline.length - 1];
    expect(Math.hypot(first.x - waypoints[0].x, first.y - waypoints[0].y)).toBeLessThan(
      1
    );
    expect(
      Math.hypot(last.x - waypoints[waypoints.length - 1].x, last.y - waypoints[waypoints.length - 1].y)
    ).toBeLessThan(1);
  });

  it("returns two points unchanged for a straight segment", () => {
    const segment = [
      { x: 0, y: 0 },
      { x: 200, y: 0 },
    ];
    expect(catmullRomSpline(segment)).toEqual(segment);
  });
});

describe("buildSvgPathD", () => {
  it("builds move/line path commands", () => {
    expect(
      buildSvgPathD([
        { x: 1, y: 2 },
        { x: 3, y: 4 },
      ])
    ).toBe("M 1 2 L 3 4");
  });
});

describe("buildWarCampaignPathD", () => {
  it("returns empty path when war has insufficient waypoints", () => {
    expect(buildWarCampaignPathD(sampleWar({ campaign_line_points: [] }))).toBe(
      ""
    );
  });

  it("returns non-empty path for valid war", () => {
    const path = buildWarCampaignPathD(sampleWar());
    expect(path.startsWith("M ")).toBe(true);
    expect(path.includes("L ")).toBe(true);
  });
});

describe("warLineStrokeStyle", () => {
  it("is stable for the same war id", () => {
    const first = warLineStrokeStyle("war-42", 3);
    const second = warLineStrokeStyle("war-42", 3);
    expect(second).toEqual(first);
  });

  it("uses default colors for a single war", () => {
    const style = warLineStrokeStyle("war-1", 1);
    expect(style.borderColor).toBe("#2a1810");
    expect(style.dashColor).toBe("#8b3a3a");
    expect(style.opacity).toBe(0.85);
  });
});
