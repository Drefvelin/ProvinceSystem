# Step 70d.04 — `placeBattle` axis insertion

**Depends on:** 70d.03  
**Touches:** `CampaignBattlePlacer.java`, `CampaignScheduleBuildContext.java`, `CampaignBattlePlacerTest.java`

**Status:** **done** (2026-08-23)

## Tasks

1. Add `axisIndexOf(ctx, provinceId)` helper using war axis list.
2. Replace append/prepend with `insertAtAxisOrder(schedule, slot, axisIndex)`:
   - NAVAL invasion → force index 0
   - else find first position where existing slot's axis index > new slot's axis index
3. Keep dedupe rules from [02-planning-lock-fb.md](./02-planning-lock-fb.md).
4. Unit tests:
   - fort at 713 inserted **before** field at 706 on same leg
   - NAVAL prepend then FB field at B stays at index 1
   - duplicate optional FIELD same province skipped

## Resolution

- `CampaignScheduleBuildContext` stores `List<Integer> axis` for sort keys.
- `CampaignBattlePlacer` uses `insertOrdered` with `fightOrderKey` (ascending invasion / descending counter) and `kindPriority` tie-breaking.
- Invasion NAVAL still prepends at index 0; counter NAVAL uses `insertOrdered`.
- `CampaignBattlePlacerTest`: 11 tests including axis-order and same-province tie-break cases.
- `CampaignScheduleBuilderTest.build_capitalInsideZoc_*`: updated off-axis siege expectation (siege at fort home not on axis sorts last).

## Done when

- [x] `CampaignBattlePlacerTest` covers insertion ordering
- [x] No direct `schedule.add(...)` outside placer (except invasion NAVAL prepend and inside `insertOrdered`)
