# Step 53 — One province per settlement

**Repos:** `Workspace/simplefactions` · `ProvinceSystem` (dev data only)  
**Depends on:** [step-42](../step-42/00-index.md) settlements on map  
**Supersedes:** Multi-province settlement rules in [step-42/01-planning-lock](../step-42/01-planning-lock.md) and `simplefactions/Documentation/Settlements.md`

## Goal

Each **settlement is exactly one province** — the province where it was founded. No neighbour absorption at founding, no join-by-adjacency, no claim growth into settlements, no hop-distance founding rules.

## Problem (today)

| Issue | Root cause |
|-------|------------|
| Cities span multiple provinces | `initialTerritory()`, `join()`, `onProvinceClaimed()` |
| Can't found adjacent cities | `settlement-found-distance` + hop checks |
| Lanbury owns 705 + 704 | Legacy founding rules |

## Build order

```mermaid
flowchart LR
  lock[53.01 lock] --> handler[53.02 SF handler]
  handler --> data[53.03 dev data]
  data --> docs[53.04 docs verify]
```

## Batches

| # | Batch | Repo | Summary |
|---|-------|------|---------|
| 1 | [01-planning-lock](./01-planning-lock.md) | Planning | Locked rules — **done** |
| 2 | [02-sf-handler-simplify](./02-sf-handler-simplify.md) | SF | Handler + config + export — **done** |
| 3 | [03-dev-data-fix](./03-dev-data-fix.md) | SF + PS | Lanbury → province 705 only — **done** |
| 4 | [04-docs-verify](./04-docs-verify.md) | SF | `Settlements.md` + smoke checks — **done** |

## Status

**Done** (2026-08-18).
