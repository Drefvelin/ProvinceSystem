import type { WikiCommandSet, WikiSection } from "./types";

// ---------- MMOInventory: Extra Equipment Slots ----------

export type EquipmentSlotRow = {
  slot: string;
  inventorySlot: number;
  accepts: string;
};

/** The 4 live accessory slots (`inventory/tfmc_inventory.yml`), placed directly in the vanilla 3x9 grid. */
export const equipmentSlots: EquipmentSlotRow[] = [
  { slot: "Ring Slot", inventorySlot: 9, accepts: "MMOItems type RING (10 rings exist)" },
  { slot: "Amulet Slot", inventorySlot: 10, accepts: "MMOItems type AMULET (9 amulets exist)" },
  { slot: "Artifact Slot I", inventorySlot: 11, accepts: "MMOItems type ARTIFACT (11 artifacts exist)" },
  { slot: "Artifact Slot II", inventorySlot: 12, accepts: "MMOItems type ARTIFACT (11 artifacts exist)" },
];

/** No player command exists for the live inventory. It is `type: vanilla`, so slots sit in your normal inventory. */
export const equipmentSlotsCommands: WikiCommandSet = {
  system: "MMOInventory",
  href: "/wiki/equipment-slots",
  commands: [],
  excludedStaffCommands: ["/mmoinventory (/rpginventory, /mmoinv, /rpginv): admin reload and inspect"],
};

export const equipmentSlotsSection: WikiSection = {
  nav: {
    href: "/wiki/equipment-slots",
    label: "Equipment Slots",
    category: "character",
    blurb: "Four extra accessory slots: Ring, Amulet and two Artifacts: living in your normal inventory.",
  },
  commands: equipmentSlotsCommands,
};
