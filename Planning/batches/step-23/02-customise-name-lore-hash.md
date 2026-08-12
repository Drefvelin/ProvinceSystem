# Batch 23.02 — Name colours, lore codes, texture hash, 3D bridge

**Plan + build:** Customise accepts colours and formatted lore; duplicate PNG guard; optional `item_3d` upload from lore editor.

**Repos:** `ProvinceSystem/backend`  
**Depends on:** [01](./01-pickable-preview-apply.md)

## Locked

| Piece | Value |
|-------|--------|
| `name_colours` | On customise; passed to `create_submission` with `add_name=True` |
| Lore | Allow inline colour codes; prepend `§7` if no leading colour/hex |
| Duplicate | SHA-256 texture; same `player_uuid` + `base_set` in pending/approved/applied → 400 + existing id |
| 3D | Model+texture → `kind=item_3d`; else `handheld` |

## Plan

1. Customise route/body: `name_colours`, optional model file / `use_3d`.
2. Lore validators allow codes; normalize `§7` on save; plugin pending gets normalized lines.
3. `texture_hash` column + check on lore (and prefer on skins create for same player/base_set).
4. Bridge `create_submission` kind from 3D flag.
5. Smoke: colours, mid-line `§c`, duplicate 400, `item_3d` row.

## Verify

- [x] Colours stored on new submission
- [x] Lore mid-line codes accepted; plain line gets `§7`
- [x] Duplicate PNG rejected with existing id
- [x] 3D upload creates `item_3d` + `base_set=knives`

## Status

**Implemented** (23.02). Next: [03-editor-ui](./03-editor-ui.md).

## Out of scope

FE editor layout (03).
