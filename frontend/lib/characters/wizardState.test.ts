import { describe, expect, it } from "vitest";
import type { CreationCatalog } from "./api";
import { newDraft, setTraitsForKey } from "./wizardState";

const catalog: CreationCatalog = {
  traits: [
    { id: "one_handed", key: "injury", cost: 0 },
    { id: "blind", key: "injury", cost: 0 },
    {
      id: "wooden_claw_arm",
      key: "prosthetic",
      cost: 1,
      replaces_injury: "one_handed",
    },
  ],
  stages: [
    {
      id: "permanent_injury_selection_stage",
      type: "selection",
      target: "trait",
      key: "injury",
      min_select: 0,
      max_select: 99,
    },
    {
      id: "prosthetic_selection_stage",
      type: "selection",
      target: "trait",
      key: "prosthetic",
      min_select: 0,
      max_select: 1,
      points: 1,
    },
  ],
};

describe("setTraitsForKey prosthetic-wins sanitize", () => {
  it("drops matching injury when prosthetic is selected first", () => {
    let draft = newDraft(catalog);
    draft = setTraitsForKey(draft, catalog, "prosthetic", ["wooden_claw_arm"]);
    draft = setTraitsForKey(draft, catalog, "injury", ["one_handed", "blind"]);
    expect(draft.traitIds).toEqual(["wooden_claw_arm", "blind"]);
  });

  it("drops matching injury when injury is re-selected after prosthetic", () => {
    let draft = newDraft(catalog);
    draft = setTraitsForKey(draft, catalog, "prosthetic", ["wooden_claw_arm"]);
    draft = setTraitsForKey(draft, catalog, "injury", ["blind"]);
    expect(draft.traitIds).toEqual(["wooden_claw_arm", "blind"]);
    draft = setTraitsForKey(draft, catalog, "injury", ["one_handed", "blind"]);
    expect(draft.traitIds).toEqual(["wooden_claw_arm", "blind"]);
  });
});
