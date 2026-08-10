/** ArmourShop catalog snapshot for staff upload dropdowns. */

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

export type SkinsCatalog = {
  categories: CatalogCategory[];
  scrolls: CatalogScroll[];
  updated_at: string | null;
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
