# Step 47 — Map mode labels & Calavorn data layers

**Repos:** `ProvinceSystem` frontend + backend  
**Depends on:** [step-40](../step-40/00-index.md) (nation labels on `/map/main`)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — extends requirement 4 (labels) + province overlay modes

## Goal

1. **Labels** on political map modes other than nation: `county`, `duchy`, `kingdom`, `empire`, and `trade` — same blob layout as nations (connected components, inset corridors, hover scale).
2. **Calavorn (`main`) province layers** currently dev-only in the UI: enable `terrain`, `fertility`, `trade`, and `prosperity` on `/map/main` with generated/spoofed data where SF has not exported yet.

**Not in scope:** labels on `terrain`, `fertility`, or `prosperity` (overlay + province tooltip only).

## Problem statement

| Issue | Root cause |
|-------|------------|
| Kingdom/duchy/empire maps have no names | `MapViewer` gates labels to `mapType === "nation"`; title JSON has `titles[]` not `provinces[]` |
| Trade map has no guild names on blobs | `trade.json` has no `provinces[]`; dominance computed from `province_data.json` at compile only |
| Calavorn has no terrain/fertility/trade in toolbar | `MapToolbar` hides those modes unless `mapId === "dev"` |
| Calavorn trade regen skipped | `regeneration.py` skips `trade` for `main`; no `input/main/guilds.json` or `province_data.json` |
| Title drill unchanged | Title tiers have no `overlord`/`subjects`; nation drill rules from 40.07 do not apply |

## Locked rules (summary)

See [01-planning-lock](./01-planning-lock.md). Highlights:

| Piece | Choice |
|-------|--------|
| Label modes | `county`, `duchy`, `kingdom`, `empire`, `trade` on `/map/main` |
| No labels | `terrain`, `fertility`, `prosperity` |
| Province rollup | Recursive `titles[]` down to `county.provinces[]` (mirror `colour_mapping.py`) |
| Trade provinces | Per-province dominant guild from `province_data.json`; compile adds `provinces[]` to `trade.json` |
| Nation rules | Unchanged — full realm at overview, direct holdings when drilled (40.07 + full-realm union) |
| Title visibility | All title entries with `rgb` visible at once (no hide-until-drill v1) |
| Geometry | Reuse `province_neighbors`, `province_centroids`, `province_label_grid` from step 40 |
| Calavorn terrain/fertility | Generate from existing `defines/main/provinces.txt` (terrain + fertility already present) |
| Calavorn trade | Spoofed `input/main/guilds.json` + `province_data.json` until SF exports real data |
| Pick / hover | Unchanged — labels never on pick canvas |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Scope, rollup algorithm, spoof vs real data contract **done**
2. **[02-calavorn-terrain-fertility](./02-calavorn-terrain-fertility.md)** — Generate `terrain_map` / `fertility_map` for `main`; expose in toolbar **done**
3. **[03-calavorn-trade-data](./03-calavorn-trade-data.md)** — Spoof guild + province trade data; enable trade regen for `main` **done**
4. **[04-title-province-rollup](./04-title-province-rollup.md)** — `resolveTitleProvinces()` (frontend Option A per 47.01) **done**
5. **[05-title-labels-frontend](./05-title-labels-frontend.md)** — Multi-layer fetch, `computeVisibleRegionLabels`, wire `MapViewer` **done**
6. **[06-trade-labels](./06-trade-labels.md)** — Guild province lists + trade mode labels **done**
7. **[07-docs-verify](./07-docs-verify.md)** — Hub, STAGING Step 47, operator checklist **done**

## Checkpoint

```text
/map/main toolbar shows terrain, fertility, trade, prosperity (not dev-only)
terrain_map.png + fertility_map.png exist for main; hover tooltips work
trade.json + trade_map.png + prosperity_map.png exist for main (spoofed data OK)
/map/main county|duchy|kingdom|empire|trade: region names on each province blob
/map/main nation: unchanged (full realm, drill, inset, hover scale)
/map/main terrain|fertility|prosperity: no labels; overlay + province meta hover only
pick canvas, drill (nation), modal unchanged
```

## Status

**47.01–47.07 done.**

## Next

[step-48 label neighbor graph](../step-48/00-index.md) (water bridges for archipelago labels) · [step-41 staff map access](../step-41/00-index.md) (can run in parallel) · [step-42 capitals](../step-42/00-index.md).
