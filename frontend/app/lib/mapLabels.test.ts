import { describe, expect, it } from "vitest";

import {
  MIN_PIXEL_AREA,
  MIN_PROVINCES,
  componentPixelArea,
  computeNationLabels,
  computeVisibleNationLabels,
  connectedComponents,
  directHoldingProvinces,
  fontSizeForLabel,
  graphDiameterEndpoints,
  isDrilledSuzerainView,
  isNationLabelVisible,
  labelAngleDeg,
  labelsForProvinces,
  pixelDiameterEndpoints,
  provincesForNationLabel,
  shouldShowLabelsAtZoom,
  type LabelMapObject,
  type ProvinceCentroids,
  type ProvinceNeighbors,
} from "./mapLabels";

const chainNeighbors: ProvinceNeighbors = {
  "1": [2],
  "2": [1, 3],
  "3": [2],
};

const chainCentroids: ProvinceCentroids = {
  "1": { x: 0, y: 0, pixel_count: 6000 },
  "2": { x: 100, y: 0, pixel_count: 6000 },
  "3": { x: 200, y: 0, pixel_count: 6000 },
};

describe("connectedComponents", () => {
  it("splits disconnected province sets", () => {
    const neighbors: ProvinceNeighbors = {
      "1": [2, 3],
      "2": [1, 3],
      "3": [1, 2],
      "10": [11, 12],
      "11": [10, 12],
      "12": [10, 11],
    };

    const components = connectedComponents([1, 2, 3, 10, 11, 12], neighbors);
    expect(components).toHaveLength(2);
    expect(components.map((c) => [...c].sort())).toEqual([
      [1, 2, 3],
      [10, 11, 12],
    ]);
  });
});

describe("graphDiameterEndpoints", () => {
  it("returns chain ends for a linear graph", () => {
    expect(graphDiameterEndpoints([1, 2, 3], chainNeighbors)).toEqual([1, 3]);
  });

  it("returns the same province for a singleton component", () => {
    expect(graphDiameterEndpoints([5], {})).toEqual([5, 5]);
  });
});

describe("pixelDiameterEndpoints", () => {
  it("picks geometric extremes on an L-shaped blob, not graph-hop shortcuts", () => {
    const neighbors: ProvinceNeighbors = {
      "1": [2],
      "2": [1, 3, 4],
      "3": [2],
      "4": [2],
    };
    const centroids: ProvinceCentroids = {
      "1": { x: 0, y: 0, pixel_count: 6000 },
      "2": { x: 100, y: 0, pixel_count: 6000 },
      "3": { x: 100, y: 100, pixel_count: 6000 },
      "4": { x: 200, y: 0, pixel_count: 6000 },
    };

    expect(graphDiameterEndpoints([1, 2, 3, 4], neighbors)).toEqual([1, 3]);
    expect(pixelDiameterEndpoints([1, 2, 3, 4], centroids)).toEqual([1, 4]);
  });
});

describe("fontSizeForLabel", () => {
  it("scales fontSize from segment length and character count", () => {
    expect(fontSizeForLabel(600, "Nimbus")).toBe(100);
    expect(fontSizeForLabel(200, "Test")).toBe(50);
  });

  it("uses one unit for empty names", () => {
    expect(fontSizeForLabel(80, "   ")).toBe(80);
  });
});

describe("componentPixelArea", () => {
  it("sums pixel_count across provinces", () => {
    expect(componentPixelArea([1, 2], chainCentroids)).toBe(12000);
  });
});

describe("shouldShowLabelsAtZoom", () => {
  it("shows labels at overview zoom", () => {
    expect(shouldShowLabelsAtZoom(1)).toBe(true);
  });

  it("shows labels at max zoom boundary", () => {
    expect(shouldShowLabelsAtZoom(1.5)).toBe(true);
  });

  it("hides labels when zoomed in past threshold", () => {
    expect(shouldShowLabelsAtZoom(1.51)).toBe(false);
  });
});

describe("labelAngleDeg", () => {
  it("returns ~0 for horizontal segments", () => {
    expect(labelAngleDeg(0, 0, 100, 0)).toBeCloseTo(0, 5);
  });

  it("returns ~90 for upward vertical segments", () => {
    expect(labelAngleDeg(0, 100, 0, 0)).toBeCloseTo(90, 5);
  });
});

describe("computeNationLabels", () => {
  it("places one label along a three-province chain", () => {
    const labels = computeNationLabels(
      { TestNation: { name: "Test", provinces: [1, 2, 3] } },
      chainNeighbors,
      chainCentroids,
      { minPixelArea: 10000 }
    );

    expect(labels).toHaveLength(1);
    expect(labels[0]).toMatchObject({
      nationId: "TestNation",
      componentIndex: 0,
      text: "Test",
      x1: 0,
      y1: 0,
      x2: 200,
      y2: 0,
      cx: 100,
      cy: 0,
      segmentPx: 200,
      textLength: 200,
      fontSize: 50,
    });
    expect(labels[0].angleDeg).toBeCloseTo(0, 5);
  });

  it("emits two labels for two large disconnected components", () => {
    const neighbors: ProvinceNeighbors = {
      "1": [2, 3],
      "2": [1, 3],
      "3": [1, 2],
      "10": [11, 12],
      "11": [10, 12],
      "12": [10, 11],
    };
    const centroids: ProvinceCentroids = {
      "1": { x: 0, y: 0, pixel_count: 6000 },
      "2": { x: 10, y: 0, pixel_count: 6000 },
      "3": { x: 20, y: 0, pixel_count: 6000 },
      "10": { x: 100, y: 100, pixel_count: 6000 },
      "11": { x: 110, y: 100, pixel_count: 6000 },
      "12": { x: 120, y: 100, pixel_count: 6000 },
    };

    const labels = computeNationLabels(
      { ExclaveNation: { name: "Exclave", provinces: [1, 2, 3, 10, 11, 12] } },
      neighbors,
      centroids,
      { minPixelArea: 10000 }
    );

    expect(labels).toHaveLength(2);
    expect(labels[0].componentIndex).toBe(0);
    expect(labels[1].componentIndex).toBe(1);
    expect(labels.every((l) => l.text === "Exclave")).toBe(true);
  });

  it("skips components below MIN_PROVINCES", () => {
    const labels = computeNationLabels(
      { Tiny: { name: "Tiny", provinces: [1, 2] } },
      { "1": [2], "2": [1] },
      {
        "1": { x: 0, y: 0, pixel_count: 8000 },
        "2": { x: 10, y: 0, pixel_count: 8000 },
      }
    );

    expect(labels).toHaveLength(0);
    expect(MIN_PROVINCES).toBe(3);
  });

  it("skips components below minPixelArea threshold", () => {
    const labels = computeNationLabels(
      { Small: { name: "Small", provinces: [1, 2, 3] } },
      chainNeighbors,
      {
        "1": { x: 0, y: 0, pixel_count: 1000 },
        "2": { x: 10, y: 0, pixel_count: 1000 },
        "3": { x: 20, y: 0, pixel_count: 1000 },
      },
      { minPixelArea: MIN_PIXEL_AREA }
    );

    expect(labels).toHaveLength(0);
  });

  it("skips nations without a name", () => {
    const labels = computeNationLabels(
      { NoName: { provinces: [1, 2, 3] } },
      chainNeighbors,
      chainCentroids,
      { minPixelArea: 10000 }
    );

    expect(labels).toHaveLength(0);
  });

  it("ignores provinces missing centroids", () => {
    const labels = computeNationLabels(
      { Partial: { name: "Partial", provinces: [1, 2, 3, 99] } },
      chainNeighbors,
      chainCentroids,
      { minPixelArea: 10000 }
    );

    expect(labels).toHaveLength(1);
    expect(graphDiameterEndpoints([1, 2, 3], chainNeighbors)).toEqual([1, 3]);
  });

  it("assigns larger fontSize to wider blobs", () => {
    const neighbors: ProvinceNeighbors = {
      "1": [2],
      "2": [1, 3],
      "3": [2],
      "10": [11],
      "11": [10, 12],
      "12": [11],
    };
    const centroids: ProvinceCentroids = {
      "1": { x: 0, y: 0, pixel_count: 6000 },
      "2": { x: 50, y: 0, pixel_count: 6000 },
      "3": { x: 100, y: 0, pixel_count: 6000 },
      "10": { x: 0, y: 0, pixel_count: 6000 },
      "11": { x: 300, y: 0, pixel_count: 6000 },
      "12": { x: 600, y: 0, pixel_count: 6000 },
    };

    const labels = labelsForProvinces(
      "Sized",
      "Sized",
      [1, 2, 3, 10, 11, 12],
      neighbors,
      centroids,
      "full",
      { minPixelArea: 10000 }
    );

    expect(labels).toHaveLength(2);
    const smallBlob = labels.find((label) => label.componentIndex === 0);
    const largeBlob = labels.find((label) => label.componentIndex === 1);
    expect(smallBlob?.segmentPx).toBe(100);
    expect(largeBlob?.segmentPx).toBe(600);
    expect(largeBlob!.fontSize).toBeGreaterThan(smallBlob!.fontSize);
  });
});

const empireNeighbors: ProvinceNeighbors = {
  "1": [2],
  "2": [1, 3],
  "3": [2, 4],
  "4": [3, 5],
  "5": [4, 6],
  "6": [5],
  "10": [11],
  "11": [10, 12],
  "12": [11],
};

const empireCentroids: ProvinceCentroids = {
  "1": { x: 0, y: 0, pixel_count: 6000 },
  "2": { x: 100, y: 0, pixel_count: 6000 },
  "3": { x: 200, y: 0, pixel_count: 6000 },
  "4": { x: 300, y: 0, pixel_count: 6000 },
  "5": { x: 400, y: 0, pixel_count: 6000 },
  "6": { x: 500, y: 0, pixel_count: 6000 },
  "10": { x: 0, y: 100, pixel_count: 6000 },
  "11": { x: 100, y: 100, pixel_count: 6000 },
  "12": { x: 200, y: 100, pixel_count: 6000 },
};

const empireRegionData = {
  imperium: {
    name: "Grand Drakhanate",
    provinces: [1, 2, 3, 4, 5, 6],
    subjects: ["vassalA"],
  },
  vassalA: {
    name: "Verdant City",
    provinces: [4, 5, 6],
  },
  independent: {
    name: "Nimbus",
    provinces: [10, 11, 12],
  },
};

const overviewMapObjects: LabelMapObject[] = [
  { id: "imperium", visible: true },
  { id: "imperium_nested", visible: false },
  { id: "vassalA", visible: false },
  { id: "independent", visible: true },
];

const drilledMapObjects: LabelMapObject[] = [
  { id: "imperium", visible: false },
  { id: "imperium_nested", visible: true },
  { id: "vassalA", visible: true },
  { id: "independent", visible: true },
];

describe("label visibility helpers", () => {
  it("detects visible nations from main or nested overlays", () => {
    expect(isNationLabelVisible("imperium", overviewMapObjects)).toBe(true);
    expect(isNationLabelVisible("vassalA", overviewMapObjects)).toBe(false);
    expect(isNationLabelVisible("imperium", drilledMapObjects)).toBe(true);
    expect(isNationLabelVisible("vassalA", drilledMapObjects)).toBe(true);
  });

  it("detects drilled suzerain nested view", () => {
    expect(isDrilledSuzerainView("imperium", overviewMapObjects)).toBe(false);
    expect(isDrilledSuzerainView("imperium", drilledMapObjects)).toBe(true);
    expect(isDrilledSuzerainView("vassalA", drilledMapObjects)).toBe(false);
  });

  it("returns direct holdings without subject provinces", () => {
    expect(directHoldingProvinces("imperium", empireRegionData)).toEqual([
      1, 2, 3,
    ]);
  });

  it("resolves full provinces at overview and direct provinces when drilled", () => {
    expect(
      provincesForNationLabel("imperium", empireRegionData, overviewMapObjects)
    ).toEqual({
      provinces: [1, 2, 3, 4, 5, 6],
      scope: "full",
    });
    expect(
      provincesForNationLabel("imperium", empireRegionData, drilledMapObjects)
    ).toEqual({
      provinces: [1, 2, 3],
      scope: "direct",
    });
    expect(
      provincesForNationLabel("vassalA", empireRegionData, overviewMapObjects)
    ).toBeNull();
  });
});

describe("computeVisibleNationLabels", () => {
  it("labels visible independent nations and skips hidden vassals at overview", () => {
    const labels = computeVisibleNationLabels(
      empireRegionData,
      empireNeighbors,
      empireCentroids,
      overviewMapObjects,
      { minPixelArea: 10000 }
    );

    const nationIds = labels.map((label) => label.nationId);
    expect(nationIds).toContain("imperium");
    expect(nationIds).toContain("independent");
    expect(nationIds).not.toContain("vassalA");

    const empireLabel = labels.find((label) => label.nationId === "imperium");
    expect(empireLabel?.scope).toBe("full");
    expect(empireLabel?.x2).toBe(500);
    expect(empireLabel?.segmentPx).toBe(500);
    expect(empireLabel?.textLength).toBe(500);
    expect(empireLabel?.fontSize).toBe(
      fontSizeForLabel(500, "Grand Drakhanate")
    );

    const nimbusLabel = labels.find((label) => label.nationId === "independent");
    expect(nimbusLabel?.textLength).toBe(nimbusLabel?.segmentPx);
    expect(nimbusLabel!.fontSize).toBe(fontSizeForLabel(200, "Nimbus"));
  });

  it("labels visible subjects and uses direct holdings for drilled suzerain", () => {
    const labels = computeVisibleNationLabels(
      empireRegionData,
      empireNeighbors,
      empireCentroids,
      drilledMapObjects,
      { minPixelArea: 10000 }
    );

    const nationIds = labels.map((label) => label.nationId);
    expect(nationIds).toContain("imperium");
    expect(nationIds).toContain("vassalA");
    expect(nationIds).toContain("independent");

    const empireLabel = labels.find((label) => label.nationId === "imperium");
    expect(empireLabel?.scope).toBe("direct");
    expect(empireLabel?.x2).toBe(200);

    const vassalLabel = labels.find((label) => label.nationId === "vassalA");
    expect(vassalLabel?.scope).toBe("full");
    expect(vassalLabel?.x2).toBe(500);
  });

  it("returns no labels when nothing is visible", () => {
    const hiddenObjects: LabelMapObject[] = [
      { id: "imperium", visible: false },
      { id: "imperium_nested", visible: false },
      { id: "vassalA", visible: false },
      { id: "independent", visible: false },
    ];

    expect(
      computeVisibleNationLabels(
        empireRegionData,
        empireNeighbors,
        empireCentroids,
        hiddenObjects,
        { minPixelArea: 10000 }
      )
    ).toEqual([]);
  });
});
