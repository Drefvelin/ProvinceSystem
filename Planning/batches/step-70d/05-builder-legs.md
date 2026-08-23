# Step 70d.05 — Builder leg segments

**Depends on:** 70d.04  
**Touches:** `CampaignScheduleBuilder.java`, `WarCampaignService.java`  
**Status:** **done** (2026-08-23)

## Tasks

1. **Phase 1 — FB anchor:** `placeBattle(INVASION, campaignStartProvinceId, BORDER)` (FB field).
2. **Phase 2 — Invasion walk:** axis indices from `indexOf(FB)` to `indexOf(DT)`, step +1.
3. **Phase 3 — Counter walk:** `cursorIndex - 1` down to `indexOf(AC)`, step -1 (skip B).
4. **Phase 4 — Sea scans** on each leg's index range (after land walks).
5. Delete old private helpers: `appendAxisStep`, `appendSeaCrossingSlots`, `addSiegeIfAbsent`, `addFieldIfAbsent`, `addInvasionSlot`, `ensureRequiredTerminalSlot`, `removeInvasionSlot`.
6. `build` / `buildCounter` / `buildAll` public API unchanged.

## Done when

- [x] Brume invasion list order: `709 FIELD`, `713 SIEGE`, `705 required` (naval optional prefix)
- [x] Counter includes 672/782 cadence + required 452
- [x] No `NAVAL_INVASION` emitted
