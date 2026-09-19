import type { WikiCommandSet, WikiSection } from "./types";

// ---------- Armor Statues ----------

export const armorStatuesCommands: WikiCommandSet = {
  system: "Armor Statues",
  href: "/wiki/armor-statues",
  commands: [
    {
      command: "/tfmc statues",
      description: "Gives you the Armor Statues book.",
    },
  ],
};

export const armorStatuesSection: WikiSection = {
  nav: {
    href: "/wiki/armor-statues",
    label: "Armor Statues",
    category: "character",
    blurb: "A clickable book for posing and configuring armor stands without commands.",
  },
  commands: armorStatuesCommands,
};
