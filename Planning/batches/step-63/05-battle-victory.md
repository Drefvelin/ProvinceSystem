# Step 63.05 — Battle auto-victory

**Repo:** `simplefactions`  
**Depends on:** [63.02](./02-resolution-service.md)

## Tasks

1. **`WarResolutionService.detectBattleVictory(war, context)`**
   - Implement capital symmetry + failed retake from [01-planning-lock.md](./01-planning-lock.md).

2. **Capital helpers**
   - `defenderCapitalProvinceId(war)` — defenders war leader capital
   - `attackerCapitalProvinceId(war)` — attackers war leader capital
   - `isCapitalBattleVictory(war, provinceId, winner)` — symmetric table:
     - defender capital + aggressor win → `ATTACKER_VICTORY`
     - attacker capital + defender win → `DEFENDER_VICTORY`
     - otherwise empty (war continues)

3. **Failed retake** (non-capital or capital already handled above)
   - `pushTarget == RETAKE_OBJECTIVE`, `objectiveHeldBy == ATTACKER`, battle at objective, aggressor wins → `ATTACKER_VICTORY`

4. **Hook battle pipeline**
   - `CampaignBattleOutcomeService.applyCampaignBattleOutcome`: after occupation + battles fought increment, before `beginPostBattleChoice`:
     - Build `ResolutionContext` with province + winner coalition.
     - If `detectBattleVictory` present → end war, skip Push/Hold and `openVote`.
   - Same for `CampaignOffensiveForfeitService` and walkover wins at capital/retake.

5. **Retake behavior change**
   - Aggressor retake defense win ends war via resolution service (not cursor −1).

## Edge cases

| Case | Behavior |
|------|----------|
| Defender wins at defender capital | War continues |
| Aggressor wins at attacker capital | War continues |
| Capital objective, aggressor wins | `ATTACKER_VICTORY` (capital row) |
| Regional objective first capture | Enters retake phase (unchanged) |
| Walkover at enemy capital | Victory check runs with walkover winner |

## Tests

| Test | Expected |
|------|----------|
| Aggressor wins at defender capital | `ATTACKER_VICTORY`, no choice phase |
| Defender wins at defender capital | War active |
| Defender wins at attacker capital | `DEFENDER_VICTORY` |
| Aggressor wins at attacker capital | War active |
| Aggressor wins retake battle at objective | `ATTACKER_VICTORY` |
| Defender wins retake battle | War active, `objectiveHeldBy` defender |

## Files

| File | Action |
|------|--------|
| `War/resolution/WarResolutionService.java` | Victory detection |
| `War/battle/campaign/CampaignBattleOutcomeService.java` | Early exit |
| `War/progression/CampaignMilitaryWalkoverService.java` | Pass context after walkover win |
| `War/progression/CampaignOffensiveForfeitService.java` | Same |
