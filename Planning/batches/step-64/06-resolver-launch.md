# Step 64.06 — Resolver, launch & siege outcomes

**Repos:** `Workspace/simplefactions`  
**Depends on:** [64.02](./02-slot-model.md), [64.04](./04-fort-control.md), [64.05](./05-trim-initiative.md)  
**Touches:** `CampaignCapabilityService`, `CampaignProgressionService`, `CampaignBattleTypeResolver`, `CampaignBattleLaunchService`, `CampaignBattleOutcomeService`

## Goal

Progression reads the **schedule** for the next battle. Siege slots launch `SIEGE` battles. Winning a siege updates fort control.

## Scope

### `nextBattleProvince(war)`

Primary source: `campaignBattleSchedule.get(campaignScheduleIndex).provinceId()` when schedule non-empty and index in range.

Fallback for wars without schedule (dev / legacy): keep existing `cursor + cadence` behavior until migrated, or fail closed with log.

### Schedule advance

On campaign battle end (before push/hold):

- Increment `campaignScheduleIndex` (or align `campaignBattlesFought` 1:1 with schedule index).
- If live route re-enters enemy-controlled fort ZOC **before** that slot exists on pre-built schedule, either:
  - **Option A (64 scope):** pre-built schedule already included siege at first crossing; re-siege after control flip requires **dynamic insert** at current index (minimal: append re-siege slot when `FortControlService` says enemy controls fort on path — document in PR), or
  - **Option B:** rebuild tail of schedule from cursor (heavier; defer if A suffices).

**Lock for 64:** implement re-siege when counter-push crosses attacker-controlled fort: insert siege slot at next index if not already consumed (add `CampaignScheduleMutator` or check at `nextBattleProvince`).

### `CampaignBattleTypeResolver`

```text
resolve(war, slot) -> BattleType
  SIEGE kind -> SIEGE
  else -> FIELD
```

Pass full `ScheduledCampaignBattle` or lookup by province + index.

### `CampaignBattleLaunchService`

- Copy `fortInstallationId` / kind to battle metadata if needed for staff GUI (optional display).
- Set `BattleType` from resolver.
- Do **not** set `allowedProvinceIds` (64.08 removes enforcement; launch may already set empty).

### Siege outcome

In `CampaignBattleOutcomeService` (or dedicated listener):

```text
if battle type == SIEGE and slot has fortInstallationId:
  FortControlService.setController(war, fortId, winnerCoalition)
```

## Tasks

1. Wire `nextBattleProvince` to schedule index.
2. Resolver + launch type selection.
3. Siege outcome → fort controller update.
4. Re-siege on control flip (minimal path for counter-push).
5. Update `CampaignBattleLaunchServiceTest`, progression tests.

## Tests

- Schedule index 0 field, 1 siege → `nextBattleProvince` returns correct provinces in order.
- Siege win flips `fortControllers`.
- Resolver returns SIEGE for siege slot.

## Done when

Full declare → schedule → fight field → fight siege → controller flip works in unit/integration tests.
