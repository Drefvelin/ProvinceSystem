# Batch 21.01 — Editable kit sync + NBT preview (RPCharacters → API)

**Plan + build:** Expose `kit.yml` `editable` parts and a resolved item preview so the website never hardcodes knife stages or lore templates.

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem`  
**Depends on:** Step 20 `kit.yml` / `KitLoader` / `KitEditableSpec`

## Locked

| Piece | Value |
|-------|--------|
| Asset | Ship `plugins/RPCharacters/assets/knife_skin.png` (default preview texture; do not scrape `tfmc_pack`) |
| Editable fields | `skin-png`, `base-set` only |
| Preview source | TLibs `getItemFromPath` on the kit item path (e.g. `m.tools.IRON_HUNTING_KNIFE`) → ItemStack → display name + lore lines + material + custom model data (or equivalent) |
| Push | On reload (+ command if useful), with roster or a dedicated PUT (prefer extend catalog/roster family; document chosen endpoint) |

## Plan

1. **Asset** — Add default `knife_skin.png` under RPC resources/`assets/`; copy out on first run like other configs if needed.
2. **Payload** — For each kit item with `editable`:
   - `kit_key` / item path / `base_set` / `skin_png` id
   - `preview`: `{ display_name, lore: string[], material, custom_model_data?, … }` from live ItemStack
3. **API store** — ProvinceSystem accepts and stores snapshot (new table or column on catalog/meta); session GET for the character UI.
4. **Fail closed** — If MI/TLibs missing, log and omit preview rather than invent lore.

## Verify

- [ ] Reload RPC → API has knife editable + preview name/lore matching in-game MI item  
- [ ] `base-set` is `knives`; no category field  
- [ ] Base PNG present under RPC assets  

## Out of scope

Web editor UI; lore persistence; skin submit/apply.
