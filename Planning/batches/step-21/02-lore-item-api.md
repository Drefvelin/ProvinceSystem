# Batch 21.02 — Lore-item API (ProvinceSystem)

**Plan + build:** Character-session API for listing editable kit parts, serving preview, and submitting a customise request (name + lore + existing skin **or** new skin upload bridge).

**Repos:** `ProvinceSystem`  
**Depends on:** [01-editable-sync-and-preview](./01-editable-sync-and-preview.md)

## Locked

| Piece | Value |
|-------|--------|
| Auth | Existing character Bearer session |
| Who | Player who owns the character; character must be **claimable** (not yet `kit_status=granted`). Create-window only (see [07](./07-create-window-customise.md)). **Supersedes** earlier “must already have kit granted” note. |
| New skin | Create a normal **player** `handheld` submission with **locked** `base_set: knives` (no staff, no category) |
| Existing skin | Reference an applyable skin id that targets `knives` / hunting knife |
| Name | Display name (also becomes skin name when uploading); charset rules from `text_validation` |
| Lore | Ordered lines; prose validation; length caps from config |
| Preview GET | Merge base NBT preview + draft name/lore overlay for the editor |

## Plan

1. **Routes** (names flexible; document in batch when implementing), e.g.:
   - `GET /characters/lore-items` — editable parts + base preview + current customise state
   - `POST /characters/lore-items/{key}/customise` — name, lore[], optional `existing_skin_id` **or** multipart/new submission id
2. **Storage** — Per player/character customise draft or pending state (skin submission id, lore lines, name) until applied.
3. **Bridge** — Reuse skins submit helpers for PNG size rules (`handheld` 16×16) and Discord pending queue.
4. **List knives skins** — Expose pickable skins for `base_set: knives` (from AS catalog sync / shop YAML mirror already on API if present; otherwise document minimal list source).

## Verify

- [ ] Session required; wrong scope 401  
- [ ] Customise with name+lore only validates and stores  
- [ ] New PNG creates pending player skin (`knives`, not staff)  
- [ ] Invalid charset / oversized PNG rejected  

## Product note (post-ship)

21.02 landed with `kit_status=granted` eligibility. Target product: customise during **web create** while claimable — change in [07](./07-create-window-customise.md).

## Out of scope

Frontend; AS pack write; RPC lore apply on the live ItemStack.
