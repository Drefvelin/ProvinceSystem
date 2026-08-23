# Step 70b.03 — Schedule-only campaign GUI

**Repos:** `Workspace/simplefactions`  
**Depends on:** [70b.01](./01-planning-lock.md)  
**Supersedes:** [70.05 route GUI](../step-70/05-route-gui.md) axis-walk behavior (keep leg tagging)  
**Touches:** `CampaignRouteRenderer`, `CampaignRouteEntry`, `CampaignCreator`, `CampaignView`, `CampaignScheduleService`

## Goal

Campaign route row = **scheduled battles only**, in list order. No geographic axis filler.

## Tasks

### 1. Rewrite `buildRouteEntries(War war)`

Replace axis loop with schedule iteration:

```text
entries = []
for index, slot in invasionSchedule:
  entries.add(CampaignRouteEntry(slot.provinceId(), axisIndexOr(-1), index, INVASION))
for index, slot in counterSchedule:
  entries.add(CampaignRouteEntry(slot.provinceId(), axisIndexOr(-1), index, COUNTER))
```

- `axisIndexOr(-1)`: `campaignProvinces.indexOf(provinceId)` when axis present, else `-1`
- Include **all** indices (fought + upcoming), not `scheduleFrom` filter
- Empty schedule → empty entries (GUI shows empty route row; info book still works)

### 2. `CampaignCreator`

- Remove `resolveRouteDisplayName` `slot == null` branch (or assert `entry.hasBattleSlot()`)
- `createRouteEntryItem`: require slot from `CampaignScheduleService.slotAt(war, index, leg)`
- **Fought slots:** `resolveRouteMaterial` → gray/muted variant when `index < scheduleIndexForLeg(war, leg)`
- Keep trident / iron sword materials for naval kinds

### 3. `CampaignView`

- First-battle marker: invasion schedule index **0**, first invasion entry on current page (sub-row `slot + 9` unchanged)
- Pagination: `maxPage` from `entries.size()` only
- Optional: invasion entries first, counter entries after (single paginated list per 70b.01)

### 4. Lore

- `buildRouteLore`: append `Fought` for past indices on that leg
- Keep battle kind, realm lines, objective line on required field slots
- Remove reliance on axis-only `buildRouteLore(war, provinceId)` for route items (admin may still use)

### 5. `CampaignRouteRenderer.resolveMaterial`

- Green concrete: active leg + `index == getActiveScheduleIndex`
- Do not green provinces from `CampaignProgressionService.resolveNextBattleNodes` when that province is not the current schedule slot (schedule is authoritative)

### 6. Tests — update `CampaignRouteRendererTest`

| Test | New expectation |
|------|-----------------|
| `buildRouteEntries_brumeShaped_expandsMultipleBattlesOnSameProvince` | 3 entries (naval, siege, field) — **no** capital filler at 452 |
| `buildRouteEntries_afterSiege_showsOnlyFieldOnCapital` | 3 entries; fought naval at index 0 still shown OR grayed per lock |
| `buildRouteEntries_includesCounterLegSlots` | Counter slots appear after invasion slots in list |
| Delete / replace tests asserting `hasBattleSlot() == false` |

Add `buildRouteEntries_noAxisFiller_allSlotsHaveScheduleIndex`.

## Done when

- [x] Opening Brume vs Lantan campaign shows **only** real schedule slots (2 invasion on current export, counter page shows wilderness fights)
- [x] No item named `Battle of Wilderness` unless a schedule slot resolves to wilderness location
- [x] Tests updated and green
