# Batch 8.06 — Docs + E2E verify (armor / melee)

**Plan + build:** Parent checklist ticks; STAGING Flow 2 for **armor_set / handheld / large_handheld** (kinds with Step 7 writers).

**Repos:** Planning docs + STAGING

**Depends on:** [05-reload-and-ack](./05-reload-and-ack.md)

## Plan

1. Confirm [00-index](./00-index.md) / [08](../../08-implementation-checklist.md) S4b / [10](../../10-armourshop-itemsadder.md) match what shipped for melee/armor.
2. STAGING checklist (no `#` inside bash fences): mint → upload with kind + `base_set` → Discord approve → ArmourShop pull → reload → apply in shop onto matching BaseSet gear.
3. Tick S4b boxes that apply to 01–06; leave bow writers / bow E2E for [07](./07-bow-crossbow-writers.md).

## Build

| File | Action |
|------|--------|
| `STAGING.md` / local-dev | Flow 2 apply steps (melee/armor) |
| `08-implementation-checklist.md` | partial S4b ticks |
| step-8 `00-index` | checkpoint note if needed |

## Verify

- [x] Docs describe filtered `base_set` map + disabled `item`  
- [x] STAGING Step 8 Flow 2 apply section added  
- [x] S4b 8.01–8.05 ticked; 8.06 live E2E + 8.07 left open  
- [ ] Staging: issuer applies armor or handheld/large skin to matching gear  

**Implemented:** docs + checklists; operator STAGING boxes remain for live green.

## Out of scope

Bow / large_bow / crossbow live apply (07); guns; shields; helmets; B4 `item_3d`.
