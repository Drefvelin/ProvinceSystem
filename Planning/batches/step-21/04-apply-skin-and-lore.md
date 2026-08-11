# Batch 21.04 — Apply skin + lore onto hunting knife

**Plan + build:** After Discord approve (or when applying an existing skin), put texture/name on `IRON_HUNTING_KNIFE` via ArmourShop player lane, and apply RPC-stored lore so the in-hand item matches the web preview.

**Repos:** `Workspace/armourshop` · `Workspace/rpcharacters` · `ProvinceSystem`  
**Depends on:** [02](./02-lore-item-api.md) + [03](./03-web-item-editor.md); existing Flow 2 player apply

## Locked

| Piece | Value |
|-------|--------|
| Pack / shop | Player path: `tfmc_submissions` + **`ps_items`** (not `tfmc_armorshop`) |
| Base set | `knives` → `tools.iron_hunting_knife` |
| Lore owner | RPCharacters (persist per character; apply on **kit claim** when customise `ready`, and re-apply on join if needed) |
| Name | From skin submission / customise (AS colour/name pipeline as today) |
| Idempotent | Re-apply safe; do not duplicate kit items |

## Plan

1. **AS** — Ensure knives/`handheld` apply works for lore-knife submissions (same as other player handhelds targeting hunting knife). Tag or correlate submission ↔ character if needed for RPC.
2. **RPC** — Store custom lore (+ optional skin id / display name mirror) on character; on **kit claim** (and join rebuild if already granted), rebuild item: MI base → apply skin if present → append/set custom lore. Do not auto-grant kit on join.
3. **API ack** — When skin reaches `applied`, mark lore-item customise complete; roster/list can show status.
4. **Deny** — Clear pending customise; keep last applied state.
5. **Claim gate** — See [06](./06-kit-claim-command.md) + [07](./07-create-window-customise.md): no claim while `pending_skin`.

## Verify

- [ ] Approve custom PNG → skin on hunting knife in-game + shop/`ps_items` as expected  
- [ ] Custom lore visible on item; MI stats still present per merge rules  
- [ ] Existing knives-set skin pick applies without new upload  
- [ ] Deny leaves previous knife state intact  

## Product note (post-ship)

Apply path landed against auto-grant / post-grant customise. Wire primary apply to **claim** in 06/07.

## Out of scope

Staff category apply; changing kit grant contents.
