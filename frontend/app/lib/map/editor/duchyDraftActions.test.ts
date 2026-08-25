import { describe, expect, it } from "vitest";

import {
  removeDuchyFromDraft,
  toggleCountyInDuchy,
} from "./duchyDraftActions";

describe("duchyDraftActions", () => {
  it("toggleCountyInDuchy adds county", () => {
    const entry = { name: "DUCHY_1", rgb: "128,128,128", titles: [] };
    const next = toggleCountyInDuchy(entry, "COUNTY_1", {
      countyRgb: "58,132,60",
      usedRgbs: ["10,20,30"],
    });
    expect(next.titles).toEqual(["COUNTY_1"]);
    expect(next.rgb).not.toBe("128,128,128");
  });

  it("toggleCountyInDuchy removes county", () => {
    const entry = {
      name: "DUCHY_1",
      rgb: "180,80,80",
      titles: ["COUNTY_1", "COUNTY_2"],
    };
    const next = toggleCountyInDuchy(entry, "COUNTY_1");
    expect(next.titles).toEqual(["COUNTY_2"]);
  });

  it("removeDuchyFromDraft deletes duchy key", () => {
    const draft = {
      DUCHY_1: { name: "A", rgb: "1,2,3", titles: ["COUNTY_1"] },
      DUCHY_2: { name: "B", rgb: "4,5,6", titles: ["COUNTY_2"] },
    };
    const next = removeDuchyFromDraft(draft, "DUCHY_1");
    expect(next).toEqual({
      DUCHY_2: { name: "B", rgb: "4,5,6", titles: ["COUNTY_2"] },
    });
  });
});
