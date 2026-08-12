# Batch 30.08 — Docs + staging verify

**Plan + build:** Close Step 30 statuses when code is done; STAGING checklist; handoff.

**Depends on:** 30.02–30.07 implemented

## Staging checklist (operator, unchecked)

Live ticks remain in [STAGING.md](../../../STAGING.md) Step 30:

- Free MineSkin API key configured on PS backend
- Web: upload 64×64 base → spinner → slot ready with 3D preview
- Non-64×64 rejected
- Locked extras show Gilded+ / Ascended+ (coloured when possible)
- Masked upload; not selectable in `/rpcharacterwardrobe`
- Character switch / join applies active skin; empty base leaves account skin
- Mask on/off swaps masked ↔ active
- Gilded unlocks 2 swappable; Ascended 3
- Rank drop wipes extras
- Game create: wardrobe tip only; web create: wardrobe card (optional upload)

## Hub close-out

- [x] Mark 30.01–30.08 done in [00-index](./00-index.md)
- [x] Update [14](../../14-character-creator.md) / [03-roadmap](../../03-roadmap.md) / checklist / batches README
- [x] Rewrite [AgentHandoff](../../../../Documentation/Agent/AgentHandoff.md)
- [x] STAGING Step 30 code status (operator ticks stay open)

## Out of scope

Item `/skins` review pipeline. LibsDisguises integration. Paying for MineSkin. Death/world re-apply unless forced by bugs.

## Status

**Done.** Operator ticks remain in [STAGING.md](../../../STAGING.md) Step 30.
