# Step 60.07 — Siege battle runtime

**Repo:** SF · [00-index.md](./00-index.md) · **Depends on:** [60.06](./06-field-runtime.md) · **Next:** [60.08 raid runtime](./08-raid-runtime.md)

## Goal

Make **SIEGE** battles playable end-to-end: contest area hold timer, dual win paths, staff setup commands/GUI. Reuses 60.06 bounds, leave penalty, and join.

## Hold timer (Empire Total War style)

The hold timer starts at **`contest_duration_seconds`** (default **180s** from template or config).

| Contest control | Timer |
|-----------------|-------|
| **Attackers** (>=3 in area and outnumber defenders) | Ticks **down** 1s/sec toward **0** |
| **Defenders** (>=3 in area and >= attackers) | Ticks **up** 1s/sec toward max duration |
| **Contested / neutral** | **Pauses** |

Players in vehicles are ignored (same as capture points).

## Win conditions

**Attacker wins when:**
- Hold timer reaches **0**, or
- Defender side eliminated (lives = 0 and all online fighters in jail)

**Defender wins when:**
- Attacker side eliminated

If both sides are eliminated on the same tick, the battle ends with **no winner**.

On end: `BattleEndedEvent` fires. Campaign apply stays in **60.09**.

## Shared runtime (from 60.06)

- Province bounds + naval add-on via `BattleBoundsService`
- Leave penalty via `BattleLeavePenaltyService`
- `/battle join <battleId> <attacker|defender>`

## Staff setup

### Commands

```
/battle setcontestmin <battleId>
/battle setcontestmax <battleId>
/battle setcontestduration <battleId> <seconds>
```

Sets contest box corners at player feet and duration. Warns if battle type is not siege but still applies.

### Battle View (siege)

| Slot | Purpose |
|------|---------|
| 3 | Contest duration (click to cycle 60/120/180/240/300 before start) |
| 23 | Contest Area button → Contest View (min/max, duration, live hold if started) |

Field-only controls hidden on siege (sequential capture, capture points).

## Manual staging checklist

1. `/battle create siege test_siege` → apply `siege_default`
2. Verify contest area in Contest View
3. Start battle → 3+ attackers in area → timer counts down
4. 3+ defenders take area → timer counts back up
5. Contested presence → timer pauses
6. Hold reaches 0 → attacker win
7. Drain defender lives → all in jail → attacker win without hold
8. Leave province → 10s penalty still works

## Out of scope

| Item | Batch |
|------|-------|
| Raid runtime | 60.08 |
| Campaign auto-create | 60.09 |
| Fort ZOC siege selection | 63 |
