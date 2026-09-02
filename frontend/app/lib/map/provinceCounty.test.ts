import { describe, expect, it } from "vitest";

import { buildProvinceCountyNames } from "./provinceCounty";

describe("buildProvinceCountyNames", () => {
  it("maps a province to its county display name", () => {
    const names = buildProvinceCountyNames({
      COUNTY_1: { name: "Elvaris", provinces: [1, 2] },
      COUNTY_2: { name: "Valoris", provinces: [3] },
    });
    expect(names.get(1)).toBe("Elvaris");
    expect(names.get(2)).toBe("Elvaris");
    expect(names.get(3)).toBe("Valoris");
  });

  it("attributes nested child provinces to the child, not the parent", () => {
    const names = buildProvinceCountyNames({
      COUNTY_PARENT: { name: "Parent", titles: ["COUNTY_CHILD"] },
      COUNTY_CHILD: { name: "Child", provinces: [10] },
    });
    expect(names.get(10)).toBe("Child");
    expect(names.has(10)).toBe(true);
  });

  it("omits unassigned provinces", () => {
    const names = buildProvinceCountyNames({
      COUNTY_1: { name: "Elvaris", provinces: [1] },
    });
    expect(names.has(99)).toBe(false);
  });

  it("falls back to the county id when name is missing", () => {
    const names = buildProvinceCountyNames({
      COUNTY_1: { provinces: [4] },
    });
    expect(names.get(4)).toBe("COUNTY_1");
  });

  it("ignores malformed entries and non-integer ids", () => {
    const names = buildProvinceCountyNames({
      COUNTY_OK: { name: "Ok", provinces: [5, 1.5, "6" as unknown as number] },
      COUNTY_BAD: null as unknown as { provinces: number[] },
    });
    expect(names.get(5)).toBe("Ok");
    expect(names.has(1)).toBe(false);
    expect(names.size).toBe(1);
  });
});
