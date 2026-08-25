# Step 75 — War package reorganization

**Repo:** SF  
**Depends on:** [70d](../step-70d/00-index.md) (schedule logic stable; no open Brume schedule bugs)  
**Type:** Refactor / housekeeping (no gameplay changes)  
**Status:** done (2026-08-24)

## Problem

The `War` tree grew to **~144 Java files** during steps 56–70d. Most pain is not file count alone but **flat packages**:

| Package | Files | Issue |
|---------|------:|-------|
| `War/schedule` | 33 | Campaign build, fort/port ZOC, hourly vote window, admin, and UI copy in one folder |
| `War/battle/engine` | 22 | Runtime, capture, win checks, and raid logic mixed |
| `War/progression` | 19 | Correct domain name, but sits beside unrelated `War/campaign` (1 file) |
| Single-file packages | 6+ | `battle/naming`, `battle/dev`, `objective`, etc. |

This does not match how the rest of SF is organized (`Objects`, `Managers`, `government/*`): **domain folders, fewer siblings per folder, fat types where it helps**.

## Goal

1. **Repackage only** first (zero behavior change, full `War.**` test suite green after each batch).
2. Optional second pass: **merge micro-types** (vote result records, 4-line operational DTOs).
3. Add [`simplefactions/AGENTS.md`](../../../../simplefactions/AGENTS.md) so future war/battle code follows the same layout.

Planning lock (target tree + file migration map): [01-planning-lock.md](./01-planning-lock.md).

## Batches

| Batch | Doc | Scope | Status |
|-------|-----|-------|--------|
| **75.01** | [01-planning-lock.md](./01-planning-lock.md) | Target package tree; old→new map; rules for new code | **done** (2026-08-24) |
| **75.02** | [02-repackage-schedule.md](./02-repackage-schedule.md) | Split `War/schedule` → `War/campaign/{schedule,zoc,runtime,vote,admin,ui}` | **done** (2026-08-24) |
| **75.03** | [03-repackage-battle-engine.md](./03-repackage-battle-engine.md) | Split `battle/engine` → `core`, `win`, `capture`, `raid` | **done** (2026-08-24) |
| **75.04** | [04-repackage-campaign-tree.md](./04-repackage-campaign-tree.md) | Move `progression` under `campaign`; fold one-file packages; `War/core` | **done** (2026-08-24) |
| **75.05** | [05-merge-micro-types.md](./05-merge-micro-types.md) | Optional: vote/ZOC result records, win-service grouping | **done** (2026-08-24) |
| **75.06** | [06-docs-verify.md](./06-docs-verify.md) | Finalize `AGENTS.md`, cursor rule, `war-build-order`, import smoke | **done** (2026-08-24) |

**75.01 locked:** `BattleNamingService` → `War/battle/campaign`; `War/core` required in 75.04; see [01-planning-lock.md](./01-planning-lock.md#locked-decisions-7501).

Run **75.02 → 75.04** as separate PRs or commits. Do **not** combine repackage + merge in one step.

## Out of scope

- Changing schedule algorithms, pathfinder, or battle rules
- Renaming public API types consumed by ProvinceSystem REST (unless PS imports are updated in same batch)
- Squashing `CampaignScheduleBuilder` / `CampaignBattlePlacer` into one file
- Database table or JSON field renames

## Verify (every batch)

```bash
cd simplefactions && mvn test -Dtest="me.Plugins.SimpleFactions.War.**"
```

Optional full plugin suite after 75.06:

```bash
cd simplefactions && mvn test
```

## Done when

- [x] No flat package under `War/` has more than **~12** sibling `.java` files at one level (`campaign/progression` is 19 files by design - cohesive domain moved as one unit in 75.04)
- [x] `War/schedule` package deleted (types live under `War/campaign/*`)
- [x] [`AGENTS.md`](../../../../simplefactions/AGENTS.md) merged and linked from this index
- [x] `War.**` tests green; operator smoke unchanged (Brume schedule acceptance from 70d)
