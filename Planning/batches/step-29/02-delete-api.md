# Batch 29.02 — Player delete customise API

**Plan + build:** Session-auth endpoint to wipe one kit item’s customise row (not the skin).

**Repos:** `ProvinceSystem/backend`  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Locked

| Piece | Choice |
|-------|--------|
| Scope | One `(player_uuid, character_id, kit_key)` row; optional `kit_id` query for consistency with other lore routes |
| Auth | Player session (same as customise); character must be owned / claimable rules same as edit |
| Effect | `DELETE` row from `lore_item_customisations` (or equivalent clear). Name/lore/skin binding for that kit item gone → default on next claim |
| Not deleted | `submissions` / pack / LP / shop skin |
| Staff | Existing `resetkit` + plugin wipe unchanged (whole kit) |

## Done

1. `delete_lore_item_customise` in `lore_items.py`  
2. `DELETE /characters/lore-items/{kit_key}/customise`  
3. Smoke: wipe + idempotent + granted 403  

## Verify

- [x] Delete returns OK; row gone  
- [ ] Skin submission still exists if it was uploaded (manual / later FE path)  
- [ ] Claim after delete grants default line for that item  

## Status

**Implemented** (29.02). Next: [03-kit-list-ux](./03-kit-list-ux.md).
