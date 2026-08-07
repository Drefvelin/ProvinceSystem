# Batch 2.06 — Asset rules (sizes + kinds + grip)

**Plan + build:** Enforce exact PNG dimensions; replace retired `item_2d` with `item` / `handheld` / `large_handheld`; require `grip_preset` for large.

Supersedes the `item_2d` path from [04-submissions](./04-submissions.md). Batches 01–05 stay historical; do not rewrite them as unfinished.

Parent design: [../../05-skins-system.md](../../05-skins-system.md), [../../07-naming-conventions.md](../../07-naming-conventions.md).

## Plan

1. Exact sizes (wrong size → **400**):
   - `armor_set` icons (`helmet`…`boots`): **16×16**
   - `armor_set` layers: **64×32**
   - `item` / `handheld`: **16×16**
   - `large_handheld`: **32×32**
2. Kinds: allow `armor_set` | `item` | `handheld` | `large_handheld`. Reject `item_2d` (or map once then remove).
3. `large_handheld` requires `grip_preset` ∈ `bottom` | `middle` | `top`; store on submissions row and `meta.json`.
4. Schema migrate: add `grip_preset TEXT` nullable on `submissions`.
5. Plugin approved payload includes `kind` + `grip_preset` (null when N/A).

## Build

| File | Action |
|------|--------|
| `schema.sql` / migrate | `grip_preset` column |
| `storage.py` | read PNG IHDR width/height; reject mismatch |
| `submissions.py` | kinds + grip rules |
| `skins_routes.py` | form field `grip_preset`; kind enum |

## Verify

- [ ] 16×16 icon OK; 32×32 icon on armor slot → 400  
- [ ] Layer 64×32 OK; 32×64 → 400  
- [ ] `item` 16×16 OK; `large_handheld` without grip → 400  
- [ ] `large_handheld` 32×32 + `grip_preset=bottom` OK; `meta.json` has grip  

## Out of scope

Review-sheet PNG (2.07), Discord, ArmourShop templates, 3D/shield.
