# Step 55 — Installation upkeep, construction, and GUI

**Repos:** `Workspace/simplefactions`  
**Depends on:** [step-54](../step-54/00-index.md) (placement + map markers)  
**Blocks:** [step-43](../step-43/00-index.md) (fort ZOC should apply to **operational** forts only)

## Goal

1. **Daily upkeep** per installation kind (ledger `INSTALLATIONS` line; pay in `Faction.newDay()`).
2. **Construction time** — one build at a time; fort/port/airport complete after configured seconds.
3. **Pay or lose** — cannot afford an installation's daily upkeep → destroy that installation (**cheapest upkeep first**).
4. **Faction GUI** — Installations tab (march icon), list + detail views, queue slot, GUI confirm on deconstruct.
5. **Commands** — `/faction deconstruct` opens installations GUI when no id; with id → confirm GUI.

## Problem (today)

| Issue | Root cause |
|-------|------------|
| Instant forts in war | `construct()` registers immediately |
| No economic cost | `Cashflow.INSTALLATIONS` ledger stub (`//TODO`) |
| No player-facing management | No installations GUI |
| Deconstruct is instant, no confirm | `deconstruct()` runs immediately |

## Build order

```mermaid
flowchart LR
  lock[55.01 lock] --> cfg[55.02 config loader]
  cfg --> queue[55.03 construction queue]
  queue --> upkeep[55.04 upkeep ledger]
  upkeep --> gui[55.05 GUI commands]
  gui --> docs[55.06 docs verify]
```

## Batches

| # | Batch | Repo | Summary |
|---|-------|------|---------|
| 1 | [01-planning-lock](./01-planning-lock.md) | Planning | Locked rules + config + GUI + payment — **done** |
| 2 | [02-config-loader](./02-config-loader.md) | SF | `daily-upkeep` + `construction-time` per kind — **done** |
| 3 | [03-construction-queue](./03-construction-queue.md) | SF | Queue max 1, tick, persist, defer map export — **done** |
| 4 | [04-upkeep-ledger](./04-upkeep-ledger.md) | SF | `Cashflow.INSTALLATIONS`, `newDay()` pay-or-destroy — **done** |
| 5 | [05-installations-gui](./05-installations-gui.md) | SF | Faction tab, list/detail, confirm deconstruct — **done** |
| 6 | [06-docs-verify](./06-docs-verify.md) | SF | `Installations.md`, STAGING, checklist — **done** |

## Status

**Complete** (2026-08-19). All batches 55.01–55.06 shipped.

## Next

[step-43](../step-43/00-index.md) — fort ZOC overlay (operational forts only).
