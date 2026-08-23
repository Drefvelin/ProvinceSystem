# Step 60.06 — Field battle runtime

**Repo:** SF · [00-index.md](./00-index.md) · **Depends on:** [60.05](./05-template-gui.md) · **Next:** [60.07 siege runtime](./07-siege-runtime.md)

## Goal

Make **FIELD** battles playable end-to-end: province bounds, leave penalty, `/battle join`, lives/jail win condition, capture point QoL, and field-only point ticking.

## Win condition (v1 fun test)

A side **loses** when:

- Collective lives are **0**, and
- Every **online** fighter on that side is at **jail** (within 5 blocks of side jail; skip check if jail unset)

The battle **ends** when exactly one side is eliminated; the other side wins. If both sides are eliminated on the same tick, the battle ends with **no winner**.

**Capture points do not decide victory.** They gate spawn teleports only (Respawn Points GUI).

## Province bounds

`BattleBoundsService` resolves allowed provinces when a field (or siege) battle starts:

| Source | Rule |
|--------|------|
| Primary | `battle.provinceId` if set |
| Fallback | Province at **defender spawn** (then attacker spawn) via `province_id_grid` |
| Naval variant | Adds **one adjacent sea province** neighbour |

Raids have **no bounds**.

## Province-leave penalty

`BattleLeavePenaltyService` listens to central province enter/leave events.

| Step | Behavior |
|------|----------|
| Filter | Started **field** or **siege** participant |
| Leave allowed set | Start countdown = `battle.province_leave_countdown_seconds` (default **10s**) |
| Re-enter allowed | Cancel countdown |
| Expire | Death; penalty respawn always goes to **side spawn** (not jail) even when lives are 0 |

Raids and non-participants are ignored.

## `/battle join`

```
/battle join <battleId> <attacker|defender>
```

Same rules as Side Selection GUI (`BattleJoinService`):

- Caller must **lead a warband**
- Battle exists, not started, not locked
- Not already in another battle

## Capture points

### Quick add

```
/battle addpoint <battleId> <side>              # auto id A, B, C... per side
/battle addpoint <battleId> <id> <side>         # manual id
```

Each point stores `sequenceIndex` and `advanceSideId` (usually the side that must capture in order).

### Sequential capture toggle

Battle View slot **8**: **Sequential capture** on/off.

When **on**, only the **front** point per `advanceSideId` can progress (lowest `sequenceIndex` not fully controlled by that side). When **off**, all points behave as before.

### Field-only ticking

`Battle.tick()` runs `PointManager.tick()` only for **FIELD** battles that have started.

## Events

`BattleEndedEvent` fires when a field battle auto-ends (`battleId`, `BattleType`, optional `warId`, optional `winningSideId`). Campaign apply stays in **60.09**.

## Manual staging checklist

1. `/battle create field test_field` → apply `field_default` template → start
2. Walk out of battle province → 10s warning → death → respawn at **spawn**
3. Walk back in before 10s → countdown cancels
4. `/battle addpoint test_field attacker` twice → points **A**, **B** at feet
5. Toggle **Sequential capture** → verify C cannot progress until A/B captured
6. Drain one side lives → all sent to jail → battle auto-ends
7. `/battle join test_field defender` as warband leader (no GUI)
8. Naval template: allowed sea tile adjacent to land province

## Out of scope

| Item | Batch |
|------|-------|
| Siege contest area + hold timer | 60.07 |
| Raid target / no respawn attackers | 60.08 |
| Campaign battle create + outcome apply | 60.09 |
| Lives formula from regiments | 61 |

## Note vs 60.01 doc

60.01 listed "win = capture points" for early planning. **60.06 locks lives + jail** for v1 field fun tests; capture points remain spawn/front-line gameplay only.
