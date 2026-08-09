# Batch 7.02 — Armor set pack writer

**Plan + build:** Pure-Java writer for `armor_set` → IA YAML + six texture paths (mirror `tfmc_armor`).

**Repo:** `Workspace/armourshop`

**Depends on:** [01-scaffold](./01-scaffold.md)

## Plan

1. Add Bukkit-free pack package (e.g. `…/pack/`) with input DTO: slug, display_name, kind, file map / bytes.
2. Implement `armor_set` writer:
   - `armors_rendering.{slug}` with `layer_1` / `layer_2`, `use_color: false`
   - Four items `{slug}_helmet|chestplate|leggings|boots`: `generate: true`, icon textures, `custom_armor: {slug}`, slots
   - Copy/write six PNGs to agreed texture paths under `tfmc_submissions`
3. Match pattern in [05](../../05-skins-system.md) / curated `tfmc_armor` (e.g. celtic).
4. Unit or small main: one armor fixture → inspect YAML + files.

## Build

| File | Action |
|------|--------|
| `pack/*Writer*.java` (names TBD) | create armor path |
| Fixture PNGs (minimal valid sizes) | under `pack-fixtures/` or test resources |

## Verify

- Output YAML has `armors_rendering` + four items with `generate: true`  
- Six PNG paths exist; icons 16×16 / layers 64×32 in fixtures  

## Out of scope

`item` / `handheld` / `large_handheld`; harness for all kinds; live poll.
