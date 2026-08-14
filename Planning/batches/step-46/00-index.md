# Step 46 — Wealth history and charts

**Repos:** `ProvinceSystem` (+ SF `balance` / `global_wealth` upload)  
**Depends on:** [step-45](../step-45/00-index.md) or parallel once nation upload stable  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 12

## Goal

Time-series nation and global wealth from daily snapshots of upload data; charts on map site showing richest realms and progression over the season.

## Locked rules

| Piece | Choice |
|-------|--------|
| Source | Nation `balance` on each upload; optional `global_wealth` in map export |
| Store | Append-only table: `(date, map_id, nation_id, balance)` + global row |
| UI | Chart panel or `/map/{id}/economy` route; top-N nations + global line |
| Cadence | Daily sample aligned with chronicle job ([step-45](../step-45/00-index.md)) |

## Batches (when step starts)

1. **01-planning-lock**  
2. **02-wealth-schema** — SQLite migration + ingest on upload  
3. **03-wealth-api** — Query endpoints for charts  
4. **04-frontend-charts** — Recharts (or equivalent) panel  
5. **05-docs-verify** — STAGING Step 46  

## Status

**Planned.**
