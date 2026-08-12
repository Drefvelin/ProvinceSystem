# Batch 27.04 — Staff `resetkit`

**Plan + build:** Staff command resets one kit for one character so claim/customise can run again.

**Repos:** `Workspace/rpcharacters` (CommandManager, KitService, Database) · `ProvinceSystem` (lore customise wipe API for plugin/staff)  
**Depends on:** [03-customise-limits](./03-customise-limits.md) optional; can parallel after 02

## Locked

| Piece | Choice |
|-------|--------|
| Command | `/rpcharacter resetkit <player> <character_id> <kit_id>` |
| Permission | Existing RPCharacters staff permission |
| Player | Online required (`getPlayerExact`) |
| Kit status | Set to `ELIGIBLE` for that `kit_id` |
| Cooldown | Clear that kit’s cooldown entry for the player |
| Character data | Remove `kit-customisations` entries whose keys belong to that kit |
| ProvinceSystem | `DELETE /characters/plugin/lore-items/customisations` |
| Feedback | Staff success/fail; warn if PS wipe fails |

## Done

- `KitService.resetKit` + `RPCharacter.removeKitCustomise`
- Admin command (console OK) before players-only gate
- PS `clear_customisations_for_kit` + plugin DELETE route
- `ProvinceSystemClient.clearLoreItemCustomisations`

## Verify

- [x] After once-per-character claim, resetkit → can `/rpcharacter kit` again (logic)
- [x] Customise drafts wiped via plugin DELETE
- [x] Other kits / characters untouched (scoped delete)
- [x] Invalid character_id / kit_id → clear error

## Status

**Implemented** (27.04). Next: [05-docs-verify](./05-docs-verify.md).
