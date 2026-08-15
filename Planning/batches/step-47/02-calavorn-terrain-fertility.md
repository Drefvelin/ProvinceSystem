# Step 47.02 — Calavorn terrain & fertility

**Repos:** `ProvinceSystem` backend + frontend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Enable **terrain** and **fertility** map modes on `/map/main` using existing `defines/main/provinces.txt` metadata (no SF spoof required).

## Locked rules

| Rule | Choice |
|------|--------|
| Data | `provinces.txt` already has `terrain` + fertility per province |
| Output | `output/main/maps/terrain_map.png`, `fertility_map.png` |
| UI | Show modes in `MapToolbar` for `main` |
| Labels | None — overlay + province hover only |
| `regionData` | `null` (existing `useMapModeData` behaviour) |

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/mapgen/mapmodes/terrain_mapmode.py`](../../../backend/src/scripts/mapgen/mapmodes/terrain_mapmode.py) | `--map` CLI; run for `main` |
| [`backend/src/scripts/mapgen/mapmodes/fertility_mapmode.py`](../../../backend/src/scripts/mapgen/mapmodes/fertility_mapmode.py) | `--map` CLI; run for `main` |
| [`frontend/app/components/map/MapToolbar.tsx`](../../../frontend/app/components/map/MapToolbar.tsx) | Expose terrain + fertility for `mapId === "main"` |
| [`STAGING.md`](../../../STAGING.md) | Operator regen commands |

## Operator commands

```bash
cd ProvinceSystem/backend/src
python -m scripts.mapgen.mapmodes.terrain_mapmode --map main
python -m scripts.mapgen.mapmodes.fertility_mapmode --map main
```

Verify files:

```text
output/main/maps/terrain_map.png
output/main/maps/fertility_map.png
```

## Verify

- [x] PNGs exist and load at `GET /main/mapdata/terrain` and `/fertility` (404 before)
- [x] `/map/main` → select Terrain / Fertility — coloured overlay on parchment base
- [x] Hover shows terrain type / fertility value (`useProvinceHover`)
- [x] No nation/title labels on these modes
- [x] Pick canvas still works (mode switch redraws pick image)

## Out of scope

- Regen hook in `fullregen` loop (optional nice-to-have; manual script OK for v47)
- New terrain types or fertility scale changes

## Status

**Done.**

## Next

[03-calavorn-trade-data](./03-calavorn-trade-data.md).
