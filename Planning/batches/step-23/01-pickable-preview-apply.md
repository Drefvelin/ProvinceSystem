# Batch 23.01 — Pickable skins, preview files, namespace apply

**Plan + build:** Correct pickable list, serve website PNGs to character session, omit missing files, pass `ia_namespace` through customise → plugin → RPC merge.

**Repos:** `ProvinceSystem/backend` · `Workspace/rpcharacters`  
**Depends on:** Step 21 lore-item API

## Locked

| Piece | Value |
|-------|--------|
| Pickable | `(staff=0 AND player_uuid=session AND applied AND base_set)` OR `(staff=1 AND category=i_tools AND applied AND base_set)` |
| Missing file | Do not list |
| Texture GET | Character Bearer; owner player skin or staff pickable; 404 if missing |
| Namespaces | Player `tfmc_submissions`; staff `tfmc_armorshop` |

## Plan

1. Rewrite `_list_pickable_skins(player_uuid, base_set)` with filters + file existence check.
2. `GET /characters/lore-items/skins/{id}/texture` (auth + ACL).
3. Enrich pickable rows with `ia_namespace`, `kind`.
4. Persist/echo `ia_namespace` on customise when picking; fix `_ia_path`; plugin pending includes namespace.
5. RPC ingest + `KitCustomiseApplyService` use payload namespace (default submissions).
6. Smoke pickable filter + staff namespace on pending.

## Verify

- [x] Other players' skins not listed
- [x] Staff `i_tools` knives listed when applied + PNG present
- [x] Missing PNG omitted
- [x] Staff pick pending has `ia_namespace=tfmc_armorshop`

## Status

**Implemented** (23.01). Next: [02-customise-name-lore-hash](./02-customise-name-lore-hash.md).

## Out of scope

Name colours / lore codes (02); FE UI (03).
