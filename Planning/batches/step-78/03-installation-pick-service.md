# Step 78.03 — Installation pick service & persistence

**Depends on:** [78.02](./02-battle-raid-schedule.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Persist per-faction installation commits per battle day; lock at `vote_close_hour`; clear on battle-day advance.

## Shipped

1. **War model** — `battleInstallationPicks` (faction id → installation ids), `battleInstallationPicksBattleDay`
2. **WarMapper** — JSON round-trip via `WarData`
3. **`BattleInstallationPickService`** — `togglePick`, `getPicks`, `getAllPicks`, `isLocked`, `clearForNewBattleDay`, `syncBattleDay`
4. **Clear hooks** — `BattleScheduleService.postpone` / `skipBattleDay`, `WarManager.endWar`

## Rules

| Rule | Detail |
|------|--------|
| Editor | Faction leader only |
| Empty pick | Valid — faction has nothing in play |
| Lock | Same instant as hour vote tally (`isVoteCloseDue`) |

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=BattleInstallationPickServiceTest,WarMapperTest,BattleScheduleServiceTest"
cd simplefactions; mvn test
```
