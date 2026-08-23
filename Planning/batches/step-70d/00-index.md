# Step 70d — Chronological leg schedules (`placeBattle`)

**Repo:** SF  
**Depends on:** [70c](../step-70c/00-index.md) (geographic GUI row; unchanged)  
**Replaces:** [`CampaignScheduleBuilder`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/CampaignScheduleBuilder.java) insertion logic  
**Status:** **done** (2026-08-23)

## Problem

Schedule slots were built by scattered helpers and **append order**, which broke chronology vs the axis (Greenfort siege after capital field, border dropped on trim, naval/landing confusion).

## Goal

Pathfinder produces the **campaign axis**. Split into **two legs**, each a **chronological battle list** (fight order = list order = geographic order along that leg's axis segment). Only **`placeBattle`** mutates a leg list; it **inserts** each slot at the correct axis position (duplicates allowed).

Planning lock: [02-planning-lock-fb.md](./02-planning-lock-fb.md) (**authoritative**, locked 2026-08-23). [01-planning-lock.md](./01-planning-lock.md) is the superseded v1 sketch.

## Implementation (2026-08-23)

| Artifact | Status | Notes |
|----------|--------|-------|
| `BattleTrigger.java` | done | BORDER, CADENCE, OBJECTIVE, FORT_ZOC, NAVAL |
| `CampaignScheduleBuildContext.java` | done | invasion/counter lists, fort/port dedupe, `axis` sort keys |
| `CampaignBattlePlacer.java` | done | axis-order `insertOrdered`; invasion NAVAL prepend |
| `CampaignScheduleBuilder.java` | done | phased walks + `buildAll`; invasion sea scan `0→DT`, counter from `cursorIndex-1` |
| `CampaignScheduleTrimmer.java` | done | naval+border prefix protect (indices 0–1) |
| `WarCampaignService.java` | done | uses `buildAll` once |
| `CampaignBattlePlacerTest.java` | done | rule unit tests |
| `CampaignScheduleBuilderTest.java` | done | Brume order tests green |
| `CampaignScheduleTrimmerTest.java` | done | full suite |
| `WarCampaignServiceTest.java` | done | naval prepend + FB at index 1 |

## Batches (bite-sized)

| Batch | Doc | Scope | Status |
|-------|-----|-------|--------|
| **70d.02** | [02-planning-lock-fb.md](./02-planning-lock-fb.md) | Lock FB legs + insert-at-axis | **done** |
| **70d.03** | [03-stabilize-compile.md](./03-stabilize-compile.md) | Fix broken tests / compile; baseline `mvn test` | **done** |
| **70d.04** | [04-placer-insert.md](./04-placer-insert.md) | `placeBattle` inserts by axis index; naval before FB | **done** |
| **70d.05** | [05-builder-legs.md](./05-builder-legs.md) | Leg segments FB→DT and (B−1)→AC; delete old helpers | **done** |
| **70d.06** | [06-trim-fb.md](./06-trim-fb.md) | Trim protects FB slot (+ naval prefix) | **done** |
| **70d.07** | [07-tests-brume.md](./07-tests-brume.md) | Builder, trimmer, WarCampaignService, renderer | **done** |
| **70d.08** | [08-docs-verify.md](./08-docs-verify.md) | `Wars.md`, smoke checklist, close step | **done** |
| **70d.09** | [09-siege-chronology.md](./09-siege-chronology.md) | Siege chronology sort key; invasion past-DT guard | **done** |

Step 70d remains **done**; 70d.09 is a follow-up fix for off-axis fort home ordering.

## Out of scope

- GUI geographic sort (70c)
- Display names (70b)
- Fight progression / cursor push
- Removing `NAVAL_INVASION` enum (keep for old saves; stop emitting)

## Brume acceptance

Axis: `452, 782, 758, 757, 672, 709, 713, 705`. FB = field at **709** (naval prepended if harbour covers sea).

**Invasion list (chronological):** `709 field` → `713 siege` → `705 required`  
**Counter list:** cadence fields toward `452`, required at `452`  
**GUI row (70c):** `452 - 782 - 672 - [709] - 713 siege - 705`

Manual smoke: [08-docs-verify.md](./08-docs-verify.md) (operator sign-off).
