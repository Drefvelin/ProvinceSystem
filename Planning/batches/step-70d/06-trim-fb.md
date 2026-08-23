# Step 70d.06 — Trimmer FB protection

**Depends on:** 70d.05  
**Touches:** `CampaignScheduleTrimmer.java`, `CampaignScheduleTrimmerTest.java`  
**Status:** **done** (2026-08-23)

## Tasks

1. Invasion protected prefix:
   - If `schedule[0].kind == NAVAL` → protect indices `0` and `1`
   - Else protect index `0` (FB field)
2. Optional: `trimInvasion(schedule, max, borderProvinceId)` never drops first FIELD at `campaignStartProvinceId` if trim logic changes.
3. Counter `trimCounter` unchanged (drop from AC-adjacent optional fields).

## Tests

- Naval + border + siege + objective trim to cap 4 keeps naval + FB
- Brume-shaped trim keeps 709 over dropping siege first

## Done when

- [x] `CampaignScheduleTrimmerTest` green including naval prefix case
