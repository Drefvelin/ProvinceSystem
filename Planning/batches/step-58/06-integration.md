# Step 58.06 — Integration

**Step:** 58 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Wire Campaign GUI into WarView navigation and extend admin `warstatus` / `warpath` for full-axis Step 58 progression fields.

## Scope

- [x] `WarCreator.createCampaignButton` + WarView slot 49 for war participants (non-raid wars with route)
- [x] WarView click opens `InventoryManager.openCampaignView`
- [x] `openCampaignView`: `WhitePeaceService.recalculateProposals` before GUI; auto-end or persist
- [x] `WarDebugFormatter`: `lastBattleOccupied`, `cursorProvinceId`, `nextBattleNodes`
- [x] `/faction warpath`: richer success line (cursor, phase, initiative, reset note)
- [x] Unit tests: extended `WarDebugFormatterTest`
- [x] `mvn test`

## Navigation

War list → WarView → **Campaign** (slot 49) → CampaignView → Back (slot 53) → WarView.

Campaign button visible when: active war, not raid, non-empty `campaignProvinces`, viewer faction is a participant.

## Admin commands

| Command | Change |
|---------|--------|
| `/faction warstatus <id>` | JSON includes `lastBattleOccupied`, `cursorProvinceId`, `nextBattleNodes` |
| `/faction warpath <id>` | Success line includes cursor index/province, phase, initiative; notes progression reset |

Regen still calls `populateCampaign` → `initProgressionState` (required for legacy step-57 short-axis wars).

## Files

| File | Role |
|------|------|
| `Managers/Inventory/WarCreator.java` | `createCampaignButton` |
| `Managers/Inventory/WarView.java` | Slot 49 render + click |
| `Managers/InventoryManager.java` | White-peace recalc on open |
| `War/WarDebugFormatter.java` | Extended status JSON |
| `Managers/CommandManager.java` | `warpath` success message |

## Out of scope

- Battle engine hooks (`CampaignProgressionService` / `OccupationService` on battle win) - Step **59**
- Hour voting UI - Step **59**

## Verify

- [ ] Manual: war participant opens Campaign from WarView; back returns to WarView
- [ ] Manual: `/faction warstatus <id>` shows occupation + `nextBattleNodes`
- [ ] Manual: `/faction warpath <id>` on legacy war upgrades full axis with cursor at border B
- [x] `mvn test`

## Status

**Done** (2026-08-20). **Next batch:** [58.07 docs verify](./07-docs-verify.md).
