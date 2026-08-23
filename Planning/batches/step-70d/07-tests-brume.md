# Step 70d.07 — Integration tests

**Depends on:** 70d.05, 70d.06  
**Status:** **done** (2026-08-23)

## Files

| File | Work |
|------|------|
| `CampaignScheduleBuilderTest` | Brume axis invasion/counter; no `NAVAL_INVASION`; siege at 713 |
| `WarCampaignServiceTest` | Naval → NAVAL prepend + FB at index 1 |
| `CampaignRouteRendererTest` | Geographic row: 452 … [709] … 713 … 705 |
| `CampaignScheduleTrimmerTest` | Full suite |

## Brume axis fixture

- Axis: `452, 782, 758, 757, 672, 709, 713, 705`
- `cursorIndex` = 5 (709), DT = 705, AC = 452
- Greenfort at 713, enemy-controlled

## Done when

- [x] `mvn test` green for `War.schedule`, `War.campaign`, `CampaignRouteRendererTest`
