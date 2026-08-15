# Step 47.03 — Calavorn trade & prosperity data

**Repos:** `ProvinceSystem` backend + frontend  
**Depends on:** [02-calavorn-terrain-fertility](./02-calavorn-terrain-fertility.md)

## Goal

Enable **trade** and **prosperity** on `/map/main` using the same pipeline as Adavaar (`dev`), with **spoofed** input until SimpleFactions exports real guild trade for Calavorn.

## Locked rules

| Rule | Choice |
|------|--------|
| Pattern | Mirror [`input/dev/guilds.json`](../../../backend/src/input/dev/guilds.json) + [`province_data.json`](../../../backend/src/input/dev/province_data.json) |
| Guild count | 5–8 fake guilds with distinct RGBs |
| Province trade | Script assigns per-province `trade` weights + `prosperity` (deterministic seed) |
| Compile | `process_trade("main")` → `defines/main/trade.json` |
| Regen | Remove `main` trade skip in [`regeneration.py`](../../../backend/src/scripts/util/regeneration.py) |
| Maps | `trade_map.png` + `prosperity_map.png` via existing trade regen path |
| Canonical | Mark spoof as **non-canonical** in docs/STAGING until SF export replaces files |

## Build

| File | Action |
|------|--------|
| `backend/src/input/main/guilds.json` | **Add** — spoof guild list |
| `backend/src/input/main/province_data.json` | **Add** — generated per province id from `provinces.txt` |
| `backend/src/scripts/tools/generate_spoof_province_data.py` | **Add** — one-off generator (re-runnable) |
| [`backend/src/scripts/util/regeneration.py`](../../../backend/src/scripts/util/regeneration.py) | Call `process_trade("main")`; remove trade skip |
| [`frontend/app/components/map/MapToolbar.tsx`](../../../frontend/app/components/map/MapToolbar.tsx) | Expose trade + prosperity for `main` |

### Generator sketch

```text
For each province id in provinces.txt:
  prosperity: seeded random in [10, 100]
  trade: normalize random weights across guild ids
Skip or zero trade for sea/water if metadata says so
```

## Operator commands

```bash
cd ProvinceSystem/backend/src
python -m scripts.tools.generate_spoof_province_data --map main
python -m scripts.compile.trade_compiler --map main
python -m scripts.mapgen.mapmodes.prosperity_mapmode --map main
python -m scripts.mapgen.mapmodes.trade_mapmode --map main
```

Or queued `fullregen` after removing skip (trade compile runs when `input/{map}/guilds.json` exists).

**Non-canonical:** `input/main/guilds.json` and `province_data.json` are placeholders — replace when SF exports real Calavorn trade.

## Verify

- [x] `defines/main/trade.json` exists with guild entries + `size` > 0
- [x] `output/main/maps/trade_map.png` and `prosperity_map.png` exist
- [x] `/map/main` Trade mode: pick + hover (guild dominance tooltip)
- [x] `/map/main` Prosperity mode: heat overlay + hover
- [x] Region overlays generated under `output/main/regions/trade/`
- [x] Document: replace spoof files when SF exports real Calavorn trade

## Out of scope

- Real guild names from SF
- `guilds.json` from live faction export
- Trade labels (batch 47.06)

## Status

**Done.**

## Next

[04-title-province-rollup](./04-title-province-rollup.md).
