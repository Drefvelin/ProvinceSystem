# Step 31.08 — Staff delete + texture reuse

**Repos:** DrinkBuilder · PS · FE

## Goal

Staff delete drinks safely; players reuse textures; refcount prevents orphan deletes.

## Plan

1. API: list player's applied textures; submit with `existing_texture_id` (CMD required).
2. FE: reuse picker (Gilded+) — applied-only labels.
3. `/drinkbuilder drink delete <id>`: remove Brewery recipe; decrement texture refcount; if 0 delete IA files + free CMD; revoke PS row.
4. Refuse deleting a texture still referenced (only via drink delete).
5. Tab-complete human ids (like ArmourShop).

## Verify

- Two drinks share texture → delete one → texture remains.  
- Delete second → texture + CMD freed.  
- Website reuse lists only owned applied textures.

## Done when

Delete/reuse paths verified on staging.

## Status

**Done** (implementation):

### ProvinceSystem
- `GET /drinks/textures` → applied only (`cmd IS NOT NULL`)
- Reuse submit rejects unapplied textures
- `GET /drinks/plugin/drinks/deletable`
- `GET /drinks/plugin/drinks/{id}`
- `POST /drinks/plugin/drinks/{id}/revoke` → `{texture_freed, ia_item_id, cmd}`

### DrinkBuilder
- `/drinkbuilder drink delete <id>` + tab-complete
- `RecipesYmlMerger.remove` · `IaDrinksRemover` · `CmdAllocator.free`

### Frontend
- Reuse picker: applied-only, `ia_item_id` + CMD labels, empty-state copy
