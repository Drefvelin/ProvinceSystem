/** ArmourShop catalog snapshot for website dropdowns + entitlements. */

export type CatalogCategory = {
  id: string;
  name: string;
  is_item: boolean;
  skin_sets: string[];
};

export type CatalogScroll = {
  id: string;
  label: string;
};

export type CatalogEntitlementDefaults = {
  name_colour_stops: number;
  max_3d_pair_bytes: number;
};

export type CatalogEntitlementGroup = {
  id: string;
  tier: number;
  permission: string;
  display_name: string;
  name_colour_stops: number;
  max_3d_pair_bytes: number;
};

export type CatalogEntitlements = {
  defaults: CatalogEntitlementDefaults;
  groups: CatalogEntitlementGroup[];
};

export type SkinsCatalog = {
  categories: CatalogCategory[];
  scrolls: CatalogScroll[];
  entitlements: CatalogEntitlements;
  updated_at: string | null;
};

export const EMPTY_ENTITLEMENTS: CatalogEntitlements = {
  defaults: { name_colour_stops: 0, max_3d_pair_bytes: 0 },
  groups: [],
};

const PS_CATEGORY_IDS = new Set(["ps_armor", "ps_items"]);

/** Staff dropdown categories: drop ps_*; armor vs item by is_item. */
export function filterStaffCategories(
  categories: CatalogCategory[],
  kind: string
): CatalogCategory[] {
  const wantItem = kind !== "armor_set";
  return categories.filter((c) => {
    if (!c?.id || PS_CATEGORY_IDS.has(c.id)) return false;
    return Boolean(c.is_item) === wantItem;
  });
}

export function parseEntitlements(raw: unknown): CatalogEntitlements {
  if (!raw || typeof raw !== "object") {
    return EMPTY_ENTITLEMENTS;
  }
  const obj = raw as Record<string, unknown>;
  const defaultsIn =
    obj.defaults && typeof obj.defaults === "object"
      ? (obj.defaults as Record<string, unknown>)
      : {};
  const stops = Number(defaultsIn.name_colour_stops);
  const pair = Number(defaultsIn.max_3d_pair_bytes);
  const defaults: CatalogEntitlementDefaults = {
    name_colour_stops: Number.isFinite(stops) && stops >= 0 ? Math.floor(stops) : 0,
    max_3d_pair_bytes: Number.isFinite(pair) && pair >= 0 ? Math.floor(pair) : 0,
  };
  const groupsIn = Array.isArray(obj.groups) ? obj.groups : [];
  const groups: CatalogEntitlementGroup[] = [];
  for (const row of groupsIn) {
    if (!row || typeof row !== "object") continue;
    const g = row as Record<string, unknown>;
    const id = typeof g.id === "string" ? g.id.trim() : "";
    if (!id) continue;
    const tier = Number(g.tier);
    const gStops = Number(g.name_colour_stops);
    const gPair = Number(g.max_3d_pair_bytes);
    groups.push({
      id,
      tier: Number.isFinite(tier) ? Math.floor(tier) : 0,
      permission: typeof g.permission === "string" ? g.permission : "",
      display_name:
        typeof g.display_name === "string" && g.display_name.trim()
          ? g.display_name
          : id,
      name_colour_stops:
        Number.isFinite(gStops) && gStops >= 0
          ? Math.floor(gStops)
          : defaults.name_colour_stops,
      max_3d_pair_bytes:
        Number.isFinite(gPair) && gPair >= 0
          ? Math.floor(gPair)
          : defaults.max_3d_pair_bytes,
    });
  }
  return { defaults, groups };
}
