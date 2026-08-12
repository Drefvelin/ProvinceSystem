# Batch 25.01 — Deny whole customise (BE)

**Plan + build:** Skin deny marks kit customise `denied`; keep name/lore; require new skin to leave denied.

**Repos:** `ProvinceSystem/backend` (`lore_items.py`, deny hook)  
**Depends on:** Existing lore customise + skin deny path

## Locked

| Piece | Choice |
|-------|--------|
| State | `STATE_DENIED = "denied"` |
| Keep | `display_name`, lore, `name_colours`, `submission_id` |
| Clear | `ready_at`, `existing_skin_id`, `skin_slug` |
| Claim / plugin pull | Denied is neither pending nor ready |
| Resubmit | Texture upload or `existing_skin_id` required |

## Verify

- [x] Deny → customise `denied`, name/lore kept, claim not ready
- [x] Resubmit without skin → 400
- [x] `deny_reason` on draft

## Status

**Implemented** (25.01). Next: [02-editor-ux](./02-editor-ux.md).
