import { describe, expect, it } from "vitest";

import { parseItemDescriptions } from "./build-item-descriptions.mjs";

describe("MMOItems lore description parsing", () => {
  it("keeps inline-commented item IDs isolated and decodes doubled apostrophes", () => {
    const source = `
CLUSTERBOMB: # display name follows in another file
    lore:
    - 'Clusterbomb''s blast radius'
    - '&aSecond line'

MINOR_FOCUS_POTION: # this must start a new identity
    lore:
    - 'Focus potion''s restorative effect'

NO_LORE: # a block without lore must not inherit the previous block
    material: PAPER

OTHER_ITEM: # another valid top-level block
    lore:
    - 'Other item only'
`;
    const used = new Set([
      "mmoitem:ITEMS:CLUSTERBOMB",
      "mmoitem:ITEMS:MINOR_FOCUS_POTION",
      "mmoitem:ITEMS:NO_LORE",
      "mmoitem:ITEMS:OTHER_ITEM",
    ]);

    expect(parseItemDescriptions(source, "items", used)).toEqual({
      "mmoitem:ITEMS:CLUSTERBOMB": ["Clusterbomb's blast radius", "Second line"],
      "mmoitem:ITEMS:MINOR_FOCUS_POTION": ["Focus potion's restorative effect"],
      "mmoitem:ITEMS:OTHER_ITEM": ["Other item only"],
    });
  });
});
