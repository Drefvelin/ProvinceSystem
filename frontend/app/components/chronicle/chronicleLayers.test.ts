import { describe, expect, it } from "vitest";

import type { MapMarkersResponse, RegionRecord } from "../map/types";
import {
  CHRONICLE_TOGGLES_OFF,
  buildChronicleLayers,
  chronicleLabelMapObjects,
  chronicleFortMarkers,
  chronicleSettlementMarkers,
  chronicleToggleSignature,
  chronicleRegionData,
  chronicleWars,
  needsMarkers,
  needsNationFile,
} from "./chronicleLayers";

const nationFile: RegionRecord = {
  suzerain: { name: "Suzerain", rgb: "10,20,30", provinces: [1, 2], subjects: ["vassal"] },
  vassal: { name: "Vassal", rgb: "40,50,60", provinces: [3], overlord: "suzerain" },
  colourless: { name: "No colour", provinces: [4] },
  landless: { name: "No land", rgb: "1,2,3", provinces: [] },
};

const markers: MapMarkersResponse = {
  map_id: "main",
  exported_at: null,
  settlements: [
    { id: "s1", name: "Placed", map_x: 100, map_y: 200 },
    { id: "s2", name: "Unplaced" },
  ],
  installations: [
    { id: "i1", name: "Harbour", kind: "port", map_x: 10, map_y: 20 },
    { id: "i2", name: "Bastion", kind: "fort", map_x: 30, map_y: 40 },
  ],
  forts: [],
  wars: [{ id: "w1", name: "The War" }],
};

describe("chronicleRegionData", () => {
  it("keeps only realms with a colour and land, like the live map does", () => {
    expect(Object.keys(chronicleRegionData(nationFile)).sort()).toEqual([
      "suzerain",
      "vassal",
    ]);
    expect(chronicleRegionData(null)).toEqual({});
  });
});

describe("chronicleLabelMapObjects", () => {
  it("hides a vassal's own label under its suzerain's", () => {
    const regionData = chronicleRegionData(nationFile);
    expect(chronicleLabelMapObjects(regionData, nationFile)).toEqual([
      { id: "suzerain", visible: true },
      { id: "vassal", visible: false },
    ]);
  });
});

describe("toggle data needs", () => {
  it("maps each toggle onto the day file it costs", () => {
    expect(needsNationFile(CHRONICLE_TOGGLES_OFF)).toBe(false);
    expect(needsMarkers(CHRONICLE_TOGGLES_OFF)).toBe(false);
    expect(
      needsNationFile({ ...CHRONICLE_TOGGLES_OFF, nationNames: true })
    ).toBe(true);
    expect(needsMarkers({ ...CHRONICLE_TOGGLES_OFF, forts: true })).toBe(true);
  });
});

describe("chronicleToggleSignature", () => {
  it("distinguishes layer sets that cost different amounts to build", () => {
    expect(chronicleToggleSignature(CHRONICLE_TOGGLES_OFF)).toBe("none");
    expect(
      chronicleToggleSignature({ ...CHRONICLE_TOGGLES_OFF, nationFill: true })
    ).toBe("nationFill");
    expect(
      chronicleToggleSignature({
        ...CHRONICLE_TOGGLES_OFF,
        nationFill: true,
        nationNames: true,
      })
    ).toBe("nationFill+nationNames");
  });

  it("does not depend on the order the toggles were switched on", () => {
    expect(
      chronicleToggleSignature({
        ...CHRONICLE_TOGGLES_OFF,
        wars: true,
        nationFill: true,
      })
    ).toBe(
      chronicleToggleSignature({
        ...CHRONICLE_TOGGLES_OFF,
        nationFill: true,
        wars: true,
      })
    );
  });
});

describe("buildChronicleLayers", () => {
  const labels = [{ nationId: "suzerain" }] as never[];
  const labelObjects = [{ id: "suzerain", visible: true }];

  it("renders nothing while every toggle is off", () => {
    const layers = buildChronicleLayers({
      toggles: CHRONICLE_TOGGLES_OFF,
      markers,
      labels,
      labelObjects,
    });
    expect(layers).toEqual({ labels: [], markers: [], wars: [] });
  });

  it("splits forts out of the settlement layer", () => {
    const settlementLayer = buildChronicleLayers({
      toggles: { ...CHRONICLE_TOGGLES_OFF, settlements: true },
      markers,
      labels,
      labelObjects,
    });
    expect(settlementLayer.markers.map((marker) => marker.id)).toEqual([
      "s1",
      "installation:i1",
    ]);

    const fortLayer = buildChronicleLayers({
      toggles: { ...CHRONICLE_TOGGLES_OFF, forts: true },
      markers,
      labels,
      labelObjects,
    });
    expect(fortLayer.markers.map((marker) => marker.id)).toEqual([
      "installation:i2",
    ]);
  });

  it("only carries wars when the war toggle is on", () => {
    expect(
      buildChronicleLayers({
        toggles: { ...CHRONICLE_TOGGLES_OFF, wars: true },
        markers,
        labels,
        labelObjects,
      }).wars
    ).toHaveLength(1);
    expect(
      buildChronicleLayers({
        toggles: { ...CHRONICLE_TOGGLES_OFF, settlements: true },
        markers,
        labels,
        labelObjects,
      }).wars
    ).toEqual([]);
  });

  it("passes labels through only when names are on", () => {
    expect(
      buildChronicleLayers({
        toggles: { ...CHRONICLE_TOGGLES_OFF, nationNames: true },
        markers: null,
        labels,
        labelObjects,
      }).labels
    ).toBe(labels);
  });
});

describe("chronicleRegionData against a hostile day file", () => {
  it("does not let a __proto__ realm hijack the map it is collected into", () => {
    // `JSON.parse` makes `__proto__` a real own property, so `Object.entries`
    // yields it and `out[id] = region` on a plain object would call
    // `Object.prototype.__proto__`'s setter: the realm silently vanishes from
    // the label layer while `buildNationColorLut` still paints its provinces,
    // and the map then answers truthily for keys it never had.
    const hostile = JSON.parse(
      '{"__proto__":{"rgb":"1,2,3","provinces":[9]},"Real":{"rgb":"4,5,6","provinces":[1]}}'
    ) as RegionRecord;

    const out = chronicleRegionData(hostile);

    expect(Object.keys(out).sort()).toEqual(["Real", "__proto__"]);
    expect(Object.getPrototypeOf(out)).toBeNull();
    // The hijack's tell: an unrelated key resolving through the injected object.
    expect((out as Record<string, unknown>).rgb).toBeUndefined();
    expect((out as Record<string, unknown>).missingRealm).toBeUndefined();
    // Scoped to this object either way, but assert the realm nothing did.
    expect(({} as Record<string, unknown>).rgb).toBeUndefined();
  });

  it("keeps the fill and the labels agreeing on which realms exist", () => {
    // `buildNationColorLut` reads the same file with `Object.values`, so any
    // realm this drops is one that gets painted with no label over it.
    const hostile = JSON.parse(
      '{"__proto__":{"rgb":"1,2,3","provinces":[9]},"Real":{"rgb":"4,5,6","provinces":[1]}}'
    ) as RegionRecord;

    expect(Object.keys(chronicleRegionData(hostile))).toHaveLength(
      Object.values(hostile).length
    );
  });
});

describe("marker layers against malformed day payloads", () => {
  // `?? []` only fires for null and undefined. A server that answers
  // `"settlements": {}` used to reach `.filter` inside a `useMemo` and take the
  // whole page down mid-render — there is no error boundary to catch it.
  const malformed = {
    map_id: "main",
    exported_at: null,
    settlements: {},
    installations: "nope",
    forts: [],
    wars: { id: "w1" },
  } as unknown as MapMarkersResponse;

  it("treats a non-array settlements payload as an empty day", () => {
    expect(chronicleSettlementMarkers(malformed, [])).toEqual([]);
  });

  it("treats a non-array installations payload as an empty day", () => {
    expect(chronicleFortMarkers(malformed)).toEqual([]);
  });

  it("treats a non-array wars payload as an empty day", () => {
    expect(chronicleWars(malformed)).toEqual([]);
    expect(chronicleWars(null)).toEqual([]);
    expect(
      chronicleWars({ map_id: "main" } as unknown as MapMarkersResponse)
    ).toEqual([]);
  });

  it("builds a whole layer set from a malformed day without throwing", () => {
    const layers = buildChronicleLayers({
      toggles: {
        ...CHRONICLE_TOGGLES_OFF,
        settlements: true,
        forts: true,
        wars: true,
      },
      markers: malformed,
      labels: [],
      labelObjects: [],
    });

    expect(layers).toEqual({ labels: [], markers: [], wars: [] });
  });
});
