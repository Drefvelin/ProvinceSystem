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
| [66](../step-66/00-index.md) | **War campaign map** (route + battle pins) → unblocks PS route layer |
| [67](../step-67/00-index.md) | Raid war type |
| [68](../step-68/00-index.md) | **Map export (full)** → occupation + chronicle |
| [68](../step-68/00-index.md) | Declare codes (production gate, last) |

## PS batches

| # | Batch | Summary | Blocked by |
|---|-------|---------|------------|
| 1 | [01-planning-lock](./01-planning-lock.md) | **Done** | — |
| 2 | [step 66](../step-66/00-index.md) batches 66.03–66.06 | Route line + battle pins on map viewer | SF 66.02 | **done** (2026-08-23) |
| 3 | 03-ps-war-overlay | Occupation tint compile or direct FE from markers API | SF **68** |
| 4 | 04-frontend-war-mode | War layer toggle; occupation overlay | 03 |
| 5 | 05-docs-verify | STAGING Step 44, hub checklist | 04 |

## Status

**Planning lock done.** Campaign route layer **shipped** ([step 66](../step-66/00-index.md), 2026-08-23). Occupation tint blocked until SF **[step 68](../step-68/00-index.md)**.
