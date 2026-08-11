/** UI-dev fixture for the read-only character sheet. */

import type { CharacterListItem } from "./api";
import { UI_DEV_LORE_CHARACTER_ID } from "./loreItemsDev";

export function uiDevSheetCharacter(
  characterId: string = UI_DEV_LORE_CHARACTER_ID
): CharacterListItem {
  return {
    id: characterId || UI_DEV_LORE_CHARACTER_ID,
    name: "UI Dev Character",
    status: "ALIVE",
    race: "human",
    class: "warrior",
    race_name: "Human",
    class_name: "Warrior",
    age: "24",
    birthday: "1203-04-15",
    gender: "female",
    description:
      "A quiet scout from the borderlands. Keeps to the trees and trusts few.",
    attributes: {
      strength: 2,
      dexterity: 3,
      constitution: 2,
      intelligence: 1,
      wisdom: 2,
      charisma: 1,
    },
    traits: [
      { id: "keen_eye", name: "Keen Eye", key: "positive" },
      { id: "light_step", name: "Light Step", key: "positive" },
      { id: "scar", name: "Old Scar", key: "neutral" },
      { id: "soft_spoken", name: "Soft Spoken", key: "negative" },
    ],
    clues: [
      "Saw a red banner at dusk near the mill road.",
      "Heard wolves circling the eastern woods.",
    ],
    kit_status: "eligible",
    kit_statuses: { starter: "eligible" },
    source: "roster",
  };
}
