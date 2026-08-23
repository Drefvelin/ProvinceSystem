# Step 70.04 — Counter-push schedule progression

**Repos:** `Workspace/simplefactions`  
**Depends on:** [70.03 per-side initiative](./03-per-side-initiative.md)  
**Touches:** `CampaignScheduleService`, `CampaignCapabilityService`, `CampaignPushProjection`, `CampaignBattleOutcomeService`

## Goal

At runtime, resolve the **active leg** from `pushTarget` so counter-push battles read and advance the counter schedule while invasion progress is preserved independently.

## Shipped

### Active-leg resolution (`CampaignScheduleService`)

| `pushTarget` | Active schedule | Active index |
|--------------|-----------------|--------------|
| `TOWARD_OBJECTIVE` | `campaignBattleSchedule` | `campaignScheduleIndex` |
| `TOWARD_AGGRESSOR_CAPITAL` | `campaignCounterSchedule` | `campaignCounterScheduleIndex` |
| `RETAKE_OBJECTIVE` | invasion schedule | `campaignScheduleIndex` |

New API:

- `ScheduleLeg activeLeg(War war)`
- `hasActiveSchedule(War war)` — non-empty active leg (battle progression)
- `hasSchedule(War war)` — invasion leg only (route GUI until 70.05)
- `slotAtActiveIndex(War war)` — current slot without re-siege insert

Refactored to use active leg: `currentSlot`, `advanceIndex`, `insertSiegeAtCurrentIndex`, `ensureReSiegeInsert`, `slotForProvince`.

Switching `pushTarget` does **not** reset the other leg's index.

### Battle-flow callers

- `CampaignCapabilityService.nextBattleProvince` — `hasActiveSchedule`
- `CampaignPushProjection.nextBattleProvince` — `hasActiveSchedule`
- `CampaignBattleOutcomeService` — `slotAtActiveIndex` before outcome; `advanceIndex` on active leg

### Deferred (70.05)

- `CampaignRouteRenderer`, `CampaignCreator`, `WarScheduleFeedbackFormatter` — still invasion-only display

## Tests

- `CampaignScheduleServiceTest`: counter `currentSlot`, counter `advanceIndex`, re-siege on counter schedule, dual-index preservation on push-target switch
- `CampaignBattleOutcomeServiceTest`: counter push advances `campaignCounterScheduleIndex` only
- `CampaignCapabilityServiceTest`: counter push uses counter schedule when present

## Done when

- [x] Active-leg resolution in `CampaignScheduleService`
- [x] Battle progression uses active schedule/index
- [x] Re-siege inserts on active leg
- [x] Tests + planning doc
