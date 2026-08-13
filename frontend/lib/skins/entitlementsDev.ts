/** Dev fixture entitlements when catalog has not synced (local / ui-dev). */

import type { CatalogEntitlements } from "./catalog";

/** Matches ArmourShop permission-groups.yml defaults. */
export const DEV_CATALOG_ENTITLEMENTS: CatalogEntitlements = {
  defaults: {
    name_colour_stops: 0,
    max_3d_pair_bytes: 30720,
  },
  groups: [
    {
      id: "noble",
      tier: 1,
      permission: "rpchar.group.noble",
      display_name: "Noble",
      name_colour_stops: 1,
      max_3d_pair_bytes: 30720,
    },
    {
      id: "gilded",
      tier: 2,
      permission: "rpchar.group.gilded",
      display_name: "Gilded",
      name_colour_stops: 2,
      max_3d_pair_bytes: 30720,
    },
    {
      id: "ascended",
      tier: 3,
      permission: "rpchar.group.ascended",
      display_name: "Ascended",
      name_colour_stops: 20,
      max_3d_pair_bytes: 30720,
    },
    {
      id: "legacy",
      tier: 4,
      permission: "rpchar.group.legacy",
      display_name: "Legacy",
      name_colour_stops: 20,
      max_3d_pair_bytes: 30720,
    },
  ],
};
