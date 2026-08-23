# Step 70.05 — Route GUI + warstatus counter leg

**Superseded (route row):** Axis-walk route entries in `CampaignRouteRenderer.buildRouteEntries` are replaced by schedule-only rows in [70b.03](../step-70b/03-schedule-only-gui.md). Leg tagging (`ScheduleLeg` on `CampaignRouteEntry`) and active-leg highlighting remain.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [70.04 counter-push progression](./04-counter-push-progression.md)  
**Touches:** `CampaignRouteEntry`, `CampaignScheduleService`, `CampaignRouteRenderer`, `CampaignCreator`, `CampaignView`, `WarDebugFormatter`, `WarScheduleFeedbackFormatter`

## Goal

Show **both** invasion and counter leg schedules in the campaign route GUI and admin debug output, with next-battle highlighting on the active leg.

## Shipped

### Leg-tagged route entries

- `CampaignRouteEntry` adds `ScheduleLeg scheduleLeg` (defaults to `INVASION` via compact constructor)
- `CampaignScheduleService`: `slotAt(war, index, leg)`, `firstOnAxisScheduleIndex(war, leg)`, `scheduleListForLeg`, `scheduleIndexForLeg`, `hasScheduleForLeg`, `getActiveScheduleIndex`

### Route rendering

- `buildRouteEntries` emits upcoming slots from **both** legs per axis province (invasion first, then counter)
- `buildRouteLore` resolves slots by leg; **Next battle** when entry matches `activeLeg` + `getActiveScheduleIndex`
- `CampaignCreator`: green concrete on active leg current slot; PDC `campaign_schedule_leg`
- `CampaignView`: first-battle marker still invasion-only (`firstOnAxisScheduleIndex(war, INVASION)`)

### Admin output

- `WarDebugFormatter`: `campaignCounterScheduleIndex`, `campaignCounterSchedule`
- `WarScheduleFeedbackFormatter`: labeled invasion + counter schedule sections; `(current)` on active leg only

## Tests

- `CampaignRouteRendererTest`: counter leg entries, counter-push next-battle lore
- `WarDebugFormatterTest`: counter schedule in JSON
- `WarScheduleFeedbackFormatterTest`: both schedule sections

## Deferred (70.06)

- `Wars.md` gameplay summary

## Done when

- [x] Dual-leg route entries and lore
- [x] Active-leg highlighting in GUI
- [x] warstatus / admin schedule output for counter leg
- [x] Tests + planning doc
