# Batch 30.04 — Ranks perk, stage platform, catalog sync

**Plan + build:** Slot unlocks from permission groups; creation stages can be web-only or game-only; web gets display names for lock copy.

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` (catalog consumers)  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Permission groups

Perk `wardrobe-skin-slots` (swappable skins; masked always separate):

| Group | Value |
|-------|-------|
| defaults / noble | `1` |
| gilded | `2` |
| ascended / legacy | `3` |

Wired via `PermissionGroupService.getWardrobeSkinSlots`, catalog `slot_limits`, roster `wardrobe_skin_slots` meta.

**Downgrade:** `enforce_wardrobe_slot_limits` on wardrobe GET/upload deletes locked `extra_*` + PNGs and fixes active.

## Stage `platform`

`both` (default) · `web` · `game`. In-game skips `web`; website `playableStages` skips `game`. Catalog emits `platform` on each stage.

Wardrobe stage *content* remains [07](./07-creation-stages.md).

## Verify

- [x] Perk + catalog + roster meta path for wardrobe_skin_slots  
- [x] Wardrobe unlocks from meta; wipe locked extras on get/upload  
- [x] Stage platform parse/emit + game skip + web skip  
- [ ] Full create-flow tick with wardrobe stages (after 30.07)  

## Status

**Done.** Next: [05-web-wardrobe-ui](./05-web-wardrobe-ui.md).
