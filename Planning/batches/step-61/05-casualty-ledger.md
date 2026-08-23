# Step 61.05 — Battle casualty ledger

**Done** (2026-08-21). **Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61.04 collective lives](./04-collective-lives.md) · **Next:** [61.06 casualty apply](./06-casualty-apply.md)

## Goal

Track **per-side casualty counts** during campaign field/siege battles for regiment loss application in 61.06.

## New component

Path: `simplefactions/.../War/battle/military/BattleCasualtyLedger.java`

| Method | Purpose |
|--------|---------|
| `recordSideCasualty(Battle battle, BattleSide side)` | Increment side total |
| `getSideCasualties(Battle battle)` | Map `sideId -> count` |
| `clear(Battle battle)` | On battle end / cancel |

Store in `Battle` metadata map or static `WeakHashMap` keyed by battle id (match `RaidAttackerEliminationService` pattern).

## Event hooks

| Source | File | When |
|--------|------|------|
| Player death (collective life tick) | `BattleManager.playerDeath` | Campaign field/siege, started |
| Player quit | `BattleManager.playerQuit` | Extend beyond raid — campaign field/siege |
| Leave penalty death | `BattleLeavePenaltyService` | If battle death triggered |

### Counting rules

| Rule | Detail |
|------|--------|
| One increment per **life-consuming** event | Collective: each `tickLife`; avoid double-count same death frame |
| Disconnect | Count once when quit during started campaign battle |
| Raid / staff | No ledger writes |

## Tests

`BattleCasualtyLedgerTest`:

- Death increments attacker side  
- Quit increments defender side  
- Manual battle (`warId null`) → no increments  
- `clear` resets totals  

Optional integration test with mocked `BattleManager` death path.

## Verification

- [x] `BattleCasualtyLedger` (`tracksCasualties`, `recordSideCasualty`, `getSideCasualties`, `clear`, `resetForTests`)
- [x] `BattleManager.playerDeath` records after `tickLife` for campaign field/siege
- [x] `BattleManager.playerQuit` records disconnect for campaign field/siege
- [x] Penalty deaths counted via `playerDeath` only (no double-count in `BattleLeavePenaltyService`)
- [x] `Battle.end()` clears ledger; `BattleManager.resetForTests` clears store
- [x] `BattleCasualtyLedgerTest` + full `mvn test` pass

## Out of scope

- Applying losses to regiments (61.06)
- Chronicle / map export (67)
