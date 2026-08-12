# Batch 30.06 — RPC apply, mask swap, wardrobe command

**Plan + build:** Pull signed skins; apply when character is selected; mask auto-swap; in-game quick swap.

**Repos:** `Workspace/rpcharacters` (+ small PS plugin wardrobe routes)  
**Depends on:** [02-data-model-api](./02-data-model-api.md) · [04-ranks-platform-catalog](./04-ranks-platform-catalog.md)

## Pull / cache

- Plugin GET `/characters/plugin/wardrobe/{uuid}/{character_id}` (signed value/signature).
- Cache per session; account texture snapshotted before first wardrobe apply.
- Enforce max slots / wipe extras on PS GET (same as web).

## Apply

- Join + character switch (+ revive / creation / permakill replacement when active changes).
- Active signed → Paper profile textures; empty active → restore account snapshot (or leave alone).
- Mask helmet (`ArmorEquipEvent`) → masked if signed, else active/account.

## `/rpcharacterwardrobe`

- Lists filled unlocked swappable slots; pick to PATCH active + apply.
- Masked never selectable.

## Verify

- [x] Switch to character with base skin → skin applied  
- [x] Switch to character with empty wardrobe → account skin unchanged  
- [x] Wear mask with masked uploaded → masked skin; remove → active  
- [x] Wardrobe command cannot select masked  
- [x] Rank wipe removes extras and fixes active (PS enforce on pull)  

## Status

**Done.** Next: [07-creation-stages](./07-creation-stages.md).
