# Step 47.06 — Trade labels

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [03-calavorn-trade-data](./03-calavorn-trade-data.md), [05-title-labels-frontend](./05-title-labels-frontend.md)

## Goal

Guild names on trade-map blobs for `/map/main` (and `dev`), using dominant-guild province assignment from 47.03/47.04.

## Locked rules

| Rule | Choice |
|------|--------|
| Region data | `trade.json` entries with `provinces[]` after compile extend |
| Label text | Guild `name` (cleaned) |
| Visibility | All guilds with `rgb` and `size` > 0 |
| Drill | None |
| Spoof data | Labels work with spoofed guilds; replace when real data lands |

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/compile/trade_compiler.py`](../../../backend/src/scripts/compile/trade_compiler.py) | Accumulate `provinces[]` per guild during dominance pass |
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | `trade` branch in `provincesForRegionLabel` |
| [`frontend/app/lib/mapLabels.test.ts`](../../../frontend/app/lib/mapLabels.test.ts) | Trade guild blob label test |
| [`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) | Include `trade` in label allowlist |

## Verify

- [x] `/map/main` trade mode: guild names on territory blobs (spoof guilds OK)
- [x] Multi-blob guild (if exclaves): multiple labels same name
- [x] Hover scales guild label when hovering that guild’s pick colour
- [x] Nation / title modes unaffected

## Out of scope

- Mixed-colour province labels (trade map uses dominant guild only)
- Guild hierarchy / overlord

## Status

**Done.**

## Next

[07-docs-verify](./07-docs-verify.md).
