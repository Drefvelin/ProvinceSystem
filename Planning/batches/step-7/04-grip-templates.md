# Batch 7.04 — Grip templates + `large_handheld`

**Plan + build:** Three locked grip model templates; `large_handheld` writer with `generate: false`.

**Repo:** `Workspace/armourshop` (+ ship templates under `tfmc_submissions` models)

**Depends on:** [03-flat-item-writers](./03-flat-item-writers.md)

## Plan

1. Author **three** shared model JSONs for grip presets `bottom` / `middle` / `top` (locked `display` translation/scale; suitable parent for 32×32 handheld art).
2. Place templates once in namespace models (e.g. `models/item/grip_bottom.json` …) as part of scaffold or writer bootstrap.
3. `large_handheld` writer:
   - Requires `grip_preset` in allowed set  
   - `generate: false` + `model_path` to a **thin per-skin** JSON that parents the chosen grip template and sets the skin texture  
   - Copy 32×32 PNG  
4. Fixtures for each grip; assert model + YAML.

## Build

| File | Action |
|------|--------|
| Grip template JSONs (3) | create |
| Pack writer | `large_handheld` branch |
| Fixtures | 32×32 PNG + grip metadata |

## Verify

- Each grip writes YAML (`generate: false`) + thin model + texture  
- Templates are shared (not duplicated full display per skin)  

## Out of scope

Donor `item_3d` / `shield` JSON; shop/LP.
