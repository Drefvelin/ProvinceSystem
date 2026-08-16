# Step 50.04 — Regenerate main

**Repos:** `ProvinceSystem`  
**Depends on:** [03-seed-live-input](./03-seed-live-input.md)

## Goal

Compile political data and regenerate all map layers for **`main`** (Adavaar world + live input).

## Commands

```bash
cd ProvinceSystem/backend/src

# Full compile + mapgen + regions (nation, kingdom, duchy, county, empire, trade, terrain, fertility, prosperity)
python -c "
from scripts.util.regeneration import _sync_regeneration
_sync_regeneration('main', 'fullregen')
"
```

Or via API (staging/prod):

```http
GET /main/{hashedKey}/api/regenerate/fullregen
```

### Province overlay modes (if not included in fullregen)

```bash
# Windows: set PYTHONIOENCODING=utf-8 if emoji print fails
python -m scripts.mapgen.mapmodes.terrain_mapmode --map main
python -m scripts.mapgen.mapmodes.fertility_mapmode --map main
python -m scripts.compile.trade_compiler --map main
python -m scripts.mapgen.mapmodes.trade_mapmode --map main
python -m scripts.mapgen.mapmodes.prosperity_mapmode --map main
```

## Outputs to verify

| Path | Purpose |
|------|---------|
| `output/main/maps/parchment_base.png` | Base layer |
| `output/main/maps/nation_map.png` | Political |
| `output/main/maps/terrain_map.png` | Toolbar terrain |
| `output/main/maps/fertility_map.png` | Toolbar fertility |
| `output/main/maps/trade_map.png` | Toolbar trade |
| `output/main/maps/prosperity_map.png` | Toolbar prosperity |
| `output/main/regions/nation/` | Cropped overlays |
| `defines/main/nation.json` | Compiled nations |

Commit `output/main/` and updated `defines/main/*.json` if repo tracks them.

## Verify

- [x] `GET /main/data/nation` returns S5 factions (e.g. Lantan)
- [x] `GET /main/data/markers` returns settlements with `map_x`/`map_y` (Lanbury → 1723, 2642)
- [x] `output/main/maps/*` — all seven toolbar/base PNGs present
- [x] `defines/main/nation.json` — Lantan provinces 705/704; Calavorn factions gone
- [ ] `GET /main/mapdata/nation` returns 200 (operator after deploy)
- [ ] Nation colours on map match SF RGBs (operator visual pass)

## Status

**Done** (2026-08-16). Local `fullregen` ~18 min on 6400²; terrain/fertility run separately.

## Next

[05-ps-frontend-registry](./05-ps-frontend-registry.md).
