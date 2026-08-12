# Batch 27.03 — Kit customise kind + size limits

**Plan + build:** Website and PS bridge use catalog templates for upload kind and PNG dimensions; hide 3D when no `3d_template`.

**Repos:** `ProvinceSystem` backend (`lore_items.py`) · `frontend` (`LoreItemEditor`, sizes helpers)  
**Depends on:** [02-rpc-templates](./02-rpc-templates.md)

## Locked

| Piece | Choice |
|-------|--------|
| Flat upload | Kind = `2d_template`; size via existing skins rules (`handheld` → 16×16, etc.) |
| 3D upload | Only if `3d_template` set; kind = that value (e.g. `item_3d`); require model JSON |
| UI | FancyCheckbox **3D model** only when `3d_template` present; label stays user-facing (no template jargon) |
| Bridge | `create_submission` kind from templates (not hard-coded handheld/item_3d) |
| Pick existing | Still filtered by `base_set` |

## Done

- Lore item API exposes `2d_template` / `3d_template` (2d defaults to `handheld`)
- Bridge rejects 3D when no `3d_template`; kinds from templates
- FE size via `expectedSizeForField`; 3D checkbox gated; preview kind from templates
- ui-dev fixture includes knife templates

## Verify

- [x] Knife: reject non-16×16 PNG on 2D upload
- [x] Knife: 3D checkbox present; bridges as `item_3d` when checked
- [x] Editable with only `2d-template`: no 3D checkbox; 3D upload rejected server-side

## Status

**Implemented** (27.03). Next: [04-resetkit](./04-resetkit.md).
