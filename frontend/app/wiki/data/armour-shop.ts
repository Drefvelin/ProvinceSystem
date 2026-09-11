import type { WikiCommandSet, WikiSection } from "./types";

// ---------- Armour Shop ----------

export type ArmourCategory = {
  name: string;
  sets: number;
  scrollsRequired: number;
  permissionGated: boolean;
  note?: string;
};

/** `categories.yml` + `Categories/a_*.yml`: the armour-set skin categories. */
export const armourCategories: ArmourCategory[] = [
  { name: "Reset to Default", sets: 7, scrollsRequired: 0, permissionGated: false, note: "Free: reverts to the vanilla/base look." },
  { name: "Medieval", sets: 32, scrollsRequired: 24, permissionGated: false },
  { name: "Forest", sets: 3, scrollsRequired: 3, permissionGated: false },
  { name: "Hraftar", sets: 3, scrollsRequired: 3, permissionGated: false },
  { name: "Pirate", sets: 4, scrollsRequired: 4, permissionGated: false },
  { name: "Samurai", sets: 5, scrollsRequired: 5, permissionGated: false },
  { name: "Imperial", sets: 3, scrollsRequired: 3, permissionGated: false },
  { name: "Original Rothil Zerratoris", sets: 15, scrollsRequired: 15, permissionGated: false },
  {
    name: "Rothil Zerratoris",
    sets: 15,
    scrollsRequired: 0,
    permissionGated: true,
    note: "Free for players who have this collection unlocked.",
  },
  { name: "Miscellaneous Sets", sets: 5, scrollsRequired: 5, permissionGated: false },
  { name: "Infantry Sets", sets: 11, scrollsRequired: 11, permissionGated: false },
  { name: "Mage Sets", sets: 2, scrollsRequired: 2, permissionGated: false },
  {
    name: "Wild Mage Sets",
    sets: 4,
    scrollsRequired: 4,
    permissionGated: false,
    note: "Uses one scroll for each set.",
  },
  { name: "Tricontinental Faction Sets", sets: 4, scrollsRequired: 4, permissionGated: false },
  { name: "Decarian Faction Sets", sets: 1, scrollsRequired: 1, permissionGated: false },
  { name: "Urcerrithian Faction Sets", sets: 1, scrollsRequired: 1, permissionGated: false },
  { name: "Calavorian Faction Sets", sets: 15, scrollsRequired: 15, permissionGated: false },
  { name: "Legacy Sets", sets: 12, scrollsRequired: 12, permissionGated: false },
  { name: "Player Armor", sets: 0, scrollsRequired: 0, permissionGated: true, note: "Reserved for approved player submissions." },
];

export type ItemSkinCategory = {
  name: string;
  skins: number;
  scrollsRequired: number;
  note?: string;
};

/** `categories.yml` + `Categories/i_*.yml`: the weapon/item skin categories. */
export const itemSkinCategories: ItemSkinCategory[] = [
  { name: "Helmets", skins: 23, scrollsRequired: 23 },
  { name: "Shields", skins: 23, scrollsRequired: 23 },
  { name: "Mage Staffs", skins: 11, scrollsRequired: 11 },
  { name: "Mage Wands", skins: 10, scrollsRequired: 10 },
  { name: "Longswords", skins: 9, scrollsRequired: 9 },
  { name: "Polearms", skins: 9, scrollsRequired: 9 },
  { name: "Swords", skins: 8, scrollsRequired: 8 },
  { name: "Daggers", skins: 7, scrollsRequired: 7, note: "One skin requires its collection unlock." },
  { name: "Warhammers", skins: 6, scrollsRequired: 6 },
  { name: "Longbows", skins: 5, scrollsRequired: 5 },
  { name: "Tools", skins: 5, scrollsRequired: 5 },
  { name: "Battleaxes", skins: 4, scrollsRequired: 4 },
  { name: "Consumables", skins: 4, scrollsRequired: 4 },
  { name: "Greataxes", skins: 3, scrollsRequired: 3 },
  { name: "Greathammers", skins: 3, scrollsRequired: 3 },
  { name: "Spears", skins: 3, scrollsRequired: 3 },
  { name: "Shortbows", skins: 3, scrollsRequired: 3 },
  { name: "Crossbows", skins: 3, scrollsRequired: 3 },
  { name: "Battle Standards", skins: 3, scrollsRequired: 3 },
  { name: "Shortswords", skins: 1, scrollsRequired: 1 },
  { name: "Mage Blades", skins: 1, scrollsRequired: 1 },
  { name: "Guns", skins: 0, scrollsRequired: 0, note: "No skins listed." },
  { name: "Player Items", skins: 11, scrollsRequired: 0, note: "Approved player submissions, free when unlocked." },
];

export type ScrollTier = { scroll: string; skinsRequiringIt: number };

/** Scroll cost distribution across all 297 skin definitions. */
export const scrollTiers: ScrollTier[] = [
  { scroll: "Common Item Skin Scroll", skinsRequiringIt: 83 },
  { scroll: "Rare Item Skin Scroll", skinsRequiringIt: 76 },
  { scroll: "Legendary Item Skin Scroll", skinsRequiringIt: 50 },
  { scroll: "Epic Item Skin Scroll", skinsRequiringIt: 47 },
];

export type DonatorTier = {
  group: string;
  tokenCooldown: string;
  skinKindsUnlocked: string;
  armour3d: boolean;
};

/**
 * `permission-groups.yml`: governs minting your own skin token to upload a
 * custom skin through the website, not browsing the shop's built-in skins.
 */
export const donatorTiers: DonatorTier[] = [
  { group: "Commoner", tokenCooldown: "Cannot mint tokens", skinKindsUnlocked: "None", armour3d: false },
  {
    group: "Noble",
    tokenCooldown: "28 days",
    skinKindsUnlocked: "Handheld, large handheld, bow, large bow, crossbow, book",
    armour3d: false,
  },
  {
    group: "Gilded",
    tokenCooldown: "21 days",
    skinKindsUnlocked: "Previous tier plus armour sets",
    armour3d: false,
  },
  {
    group: "Ascended",
    tokenCooldown: "14 days",
    skinKindsUnlocked: "Previous tiers plus 3D items, shields, 3D helmets and guns",
    armour3d: true,
  },
  {
    group: "Legacy",
    tokenCooldown: "7 days",
    skinKindsUnlocked: "Everything from every lower tier",
    armour3d: true,
  },
];

export const armourShopCommands: WikiCommandSet = {
  system: "Armour Shop",
  href: "/wiki/armour-shop",
  commands: [
    {
      command: "/armourshop",
      description: "Opens the skin shop: pick Armour skins or Item skins, then a category, then a skin to apply.",
    },
  ],
  excludedStaffCommands: [
    "/armourshop reload",
    "/armourshop token create …",
    "/armourshop token delete <code>",
    "/armourshop listtokens",
    "/armourshop pack pull",
    "/armourshop pack sync",
    "/armourshop catalog sync",
    "/armourshop submission delete <id>",
    "/armourshop skin delete <id>",
  ],
};

export const armourShopSection: WikiSection = {
  nav: {
    href: "/wiki/armour-shop",
    label: "Armour Shop",
    category: "social",
    blurb: "Spend a Skin Scroll to restyle the armour or weapon you're holding: pure cosmetics, stats untouched.",
  },
  commands: armourShopCommands,
};
