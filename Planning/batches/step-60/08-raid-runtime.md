# Step 60.08 — Raid battle runtime

**Repo:** SF · [00-index.md](./00-index.md) · **Depends on:** [60.07](./07-siege-runtime.md) · **Next:** [60.09 schedule hook](./09-schedule-hook.md)

## Goal

Make **RAID** battles playable end-to-end: single target capture win, attacker no-respawn elimination, defender infinite or finite lives, staff setup commands/GUI. Reuses 60.06 join flow and 60.05 templates.

## Region rules

| Rule | Detail |
|------|--------|
| **Bounds** | **None.** No province fence; `allowedProvinceIds` stays empty |
| **Leave penalty** | **None** (already excluded for raids in 60.06) |
| **Movement** | Map-wide during the fight |

## Target capture

On battle start, `raidTarget` from template (or staff command) seeds **one** `CapturePoint`:

- Default controller: **defender** at 100%
- `advanceSideId`: **attacker**
- Same presence rules as field points (3+ fighters, vehicles ignored)
- **Only this point ticks** and can decide victory

## Win conditions

**Attacker wins when:**
- Target fully captured (`CapturePoint.isFullyControlledBy("attacker")`), **or**
- Defender eliminated when `defender_respawn_mode == LIVES` (lives = 0 and all online fighters in jail)

**Defender wins when:**
- All attacker participants are **out** (dead at jail, marked out, or disconnected)

If attacker win and defender win conditions hit the same tick, the battle ends with **no winner**.

On end: `BattleEndedEvent` fires. Campaign apply stays in **60.09**.

## Respawn matrix

| Side | Mode | Death | Respawn |
|------|------|-------|---------|
| **Attacker** | always | Mark out; no life tick | Once to **jail** (or spawn if jail unset); stay out |
| **Defender** | `INFINITE` | No life tick | Always **spawn** |
| **Defender** | `LIVES` | Tick collective lives | **Spawn** while lives > 0; **jail** when lives = 0 |

Attackers who **disconnect** during a started raid count as out immediately.

## Shared runtime (from 60.06)

- `/battle join <battleId> <attacker|defender>`
- Friendly fire / keep inventory per template
- Field **Respawn Points** GUI is **not** shown for raids

## Staff setup

### Commands

```
/battle setraidtarget <battleId>
/battle setdefenderlives <battleId> <n>
```

### Battle View (raid)

| Slot | Purpose |
|------|---------|
| 3 | Defender respawn mode toggle (`INFINITE` / `LIVES`) before start |
| 8 | Defender lives pool (when `LIVES`; click to cycle) |
| 23 | Raid Target button → Raid Target View (location, live capture % if started) |

Field/siege-only controls hidden on raid battles.

## Manual staging checklist

1. `/battle create raid test_raid` → apply `raid_template`
2. Verify Raid Target View shows target at `(50, 64, 50)`
3. Start battle → attackers can leave province with **no** leave countdown
4. Attacker dies → respawns to jail once, cannot rejoin fight
5. Attacker disconnect → counts as out
6. 3+ attackers at target → capture progress → 100% → attacker win
7. Toggle defender mode to `LIVES`, set pool → drain lives → all in jail → attacker win
8. Eliminate all attackers before capture → defender win

## Out of scope

| Item | Batch |
|------|-------|
| Campaign auto-create | 60.09 |
| Inter-battle raids | 65 |
| Raid war declare route | 66 |
| Collective lives formula refinement | 61 |
