# Batch 8.02 — `base_set` UI

**Plan + build:** `/skins` upload form: enabled kinds only; filtered tier/type dropdowns; status shows values.

**Repos:** `ProvinceSystem/frontend` (+ Discord embed label if trivial)

**Depends on:** [01-base-set-api](./01-base-set-api.md)

## Plan

1. Kind picker: `armor_set`, `handheld`, `large_handheld`, `bow`, `large_bow`, `crossbow` — **no `item`**.
2. Filtered dropdowns (required):
   - `armor_set` → 6 tiers: `iron`, `steel`, `abyssalite`, `mythril`, `mage`, `infantry`
   - `handheld` → swords, battleaxes, daggers, warhammers, shortswords, hatchets, hoes, knives
   - `large_handheld` → spears, polearms, greathammers, staffs (+ grip preset)
   - `bow` → `shortbows` only (or single fixed value)
   - `large_bow` → `longbows`
   - `crossbow` → `crossbows`
3. Send `base_set` in multipart via `lib/skins/api.ts`.
4. Status page shows kind + tier/type; Discord review embed includes `base_set`.

## Build

| File | Action |
|------|--------|
| `KindPicker.tsx` / `UploadForm.tsx` | enabled kinds + filtered pickers |
| `lib/skins/api.ts` / sizes | kinds + `base_set` |
| Status / review UI | display |
| tfmc_bot skins embed | show `base_set` when present |

## Verify

- [x] Cannot submit without picker for the chosen kind  
- [x] Handheld list has no spears; large list has no swords  
- [x] `item` not offered  
- [x] Status + Discord show chosen value  

**Implemented:** filtered `base_set` select; kinds include bow/large_bow/crossbow; Discord embed `base_set` field.

## Out of scope

ArmourShop apply; changing BaseSet YAML on the MC server.
