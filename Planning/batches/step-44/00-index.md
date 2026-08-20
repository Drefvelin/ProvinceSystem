# Step 44 — War map layer

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** SF war rework ([Wars.md](../../../../simplefactions/Documentation/Wars.md)) · [step-38](../step-38/00-index.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 10

## Goal

Display active wars on the web map: **occupation zones** (tinted provinces), campaign line, objective province, and belligerents. **Do not infer wars or occupation from territory diffs alone.**

## Planning lock

**[01-planning-lock](./01-planning-lock.md)** — **done** (2026-08-19). Authoritative war design: [simplefactions/Documentation/Wars.md](../../../../simplefactions/Documentation/Wars.md).

## Locked rules (map layer)

| Piece | Choice |
|-------|--------|
| Data | `wars[]` per [map-export-schema.json](../../assets/map-export-schema.json) |
| Occupation | `occupied_by_attacker` / `occupied_by_defender` province id lists |
| Campaign | `campaign_provinces`, `cursor_index`, `objective_province_id` |
| Render | Province tint overlay (bulge/front), optional campaign line + objective pin |
| Events | `war_declared`, `battle_result`, `province_occupied`, `war_ended` → chronicle ([step-45](../step-45/00-index.md)) |

## SF implementation steps

Full locked order: [war-build-order.md](../../war-build-order.md).

| Step | SF scope |
|------|----------|
| [56](../step-56/00-index.md) | Foundation (no declare codes) |
| [57](../step-57/00-index.md) | Pathfinder & campaign |
| [58](../step-58/00-index.md) | Initiative & occupation |
| [59](../step-59/00-index.md) | Battle scheduling |
| [60](../step-60/00-index.md) | Warbands & battles |
| [61](../step-61/00-index.md) | Military & casualties |
| [62](../step-62/00-index.md) | End & goals |
| [63](../step-63/00-index.md) | Forts & sieges |
| [64](../step-64/00-index.md) | Naval & installations |
| [65](../step-65/00-index.md) | Inter-battle raids |
| [66](../step-66/00-index.md) | Raid war type |
| [67](../step-67/00-index.md) | **Map export** → unblocks PS batches below |
| [68](../step-68/00-index.md) | Declare codes (production gate, last) |

## PS batches (after SF step 67)

| # | Batch | Summary |
|---|-------|---------|
| 1 | [01-planning-lock](./01-planning-lock.md) | **Done** |
| 2 | 02-sf-war-export | Validate + document SF `wars[]` in `map_markers` upload |
| 3 | 03-ps-war-overlay | Occupation tint compile or direct FE from markers API |
| 4 | 04-frontend-war-mode | War layer on map viewer (toggle / auto when wars active) |
| 5 | 05-docs-verify | STAGING Step 44, hub checklist |

Batch files **02–05** are created when SF P9 starts.

## Status

**Planning lock done.** SF **[step 56](../step-56/00-index.md)** is next. PS batches blocked until SF **[step 67](../step-67/00-index.md)** export.
