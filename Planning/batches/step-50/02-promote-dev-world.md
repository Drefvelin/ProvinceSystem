# Step 50.02 — Promote Adavaar world dev → main

**Repos:** `ProvinceSystem`  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Replace Calavorn (S4) **world** assets on map id `main` with Adavaar assets from `dev`. No political JSON, no SF config, no registry rename.

## Out of scope

- `input/main/*.json` (nation, guilds, markers, …) — [50.03](./03-seed-live-input.md)
- SF `map-reference` (stays `dev` until [50.06](./06-sf-map-reference.md))
- `maps.yml`, frontend labels — [50.05](./05-ps-frontend-registry.md)
- `fullregen` — [50.04](./04-regen-main.md) after 50.03

## Preconditions

- Adavaar `map.png` and `provinces.png` under `backend/src/input/dev/` (may be gitignored locally)

## Build

| Path | Action |
|------|--------|
| `defines/dev/provinces.txt` | Copy → `defines/main/provinces.txt` |
| `input/dev/map.png` | Copy → `input/main/map.png` |
| `input/dev/provinces.png` | Copy → `input/main/provinces.png` |

## Geometry rebuild

```bash
cd ProvinceSystem/backend/src
python -m scripts.map_tools.build_province_geometry main
python -m scripts.map_tools.test_province_geometry
```

## Verify

- [x] Province **705** in `defines/main/provinces.txt`
- [x] **806** provinces (Adavaar, not ~380 Calavorn)
- [x] `test_province_geometry` passes for `main`
- [x] `input/main/map.png` + `provinces.png` present
- [x] `input/main` JSON **unchanged** (still Calavorn-era until 50.03)
- [x] SF `map-reference` still **`dev`**

## Status

**Done** (2026-08-16).

## Next

[03-seed-live-input](./03-seed-live-input.md).
