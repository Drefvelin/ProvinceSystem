# Batch 30.05 — Web wardrobe UI

**Plan + build:** Character detail wardrobe like kits: standing frames, locks, modal upload.

**Repos:** `ProvinceSystem/frontend`  
**Depends on:** [02-data-model-api](./02-data-model-api.md) · [03-mineskin-sign](./03-mineskin-sign.md) · [04-ranks-platform-catalog](./04-ranks-platform-catalog.md)

## Character page

- CTA **Wardrobe** next to Kits on character sheet (alive).
- Route `/character/[id]/wardrobe`.
- Standing frames (steve mannequin); locked extras red hue + formatted Gilded+/Ascended+ from catalog.
- Modal: 64×64 PNG validate → preview → Save spinner (MineSkin on server) → optional Equip on save.
- Masked separate; never Equip as active.

## Verify

- [x] API client + page + modal + mannequin  
- [x] `&#RRGGBB` rank display parsing for lock copy  
- [x] Client 64×64 reject before POST  
- [x] Masked upload path; no Equip on masked  

## Status

**Done.** Next: [06-rpc-apply](./06-rpc-apply.md).
