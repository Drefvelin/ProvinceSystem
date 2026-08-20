# Step 58.05 — Campaign GUI + white peace

**Step:** 58 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Campaign view (route row, cursor, initiative/phase info, leader actions) and `WhitePeaceService` (auto-propose recalc, accept, auto-end). GUI-first for hold, counter-push, and accept peace.

## Scope

- [x] `WhitePeaceService` - recalc flags, accept validation, auto-end when both propose
- [x] `WarManager.endWar(War, WarEndReason)` for white peace endings
- [x] `CampaignRouteRenderer` - blue/red/green/yellow concrete logic + lore tags
- [x] `CampaignCreator`, `CampaignView`, `CampaignInventoryHolder`, `SFGUI.CAMPAIGN_VIEW`
- [x] InventoryManager wiring + confirm flow for hold / counter-push / accept peace
- [x] `InventoryManager.openCampaignView(Player, War)` for 58.06 WarView button
- [x] Unit tests: `WhitePeaceServiceTest`, `CampaignRouteRendererTest`
- [x] `mvn test` - **85 tests**, 0 failures

## GUI layout

| Area | Content |
|------|---------|
| Route row (slots 10-18) | Paginated axis; prev/next arrows |
| Info (slot 4) | Initiative, phase, proposal flags |
| Actions (48-50) | Accept white peace; Hold / Counter-push for defender leader |
| Back (53) | War view |

Concrete legend: blue = viewer coalition, red = enemy/neutral, green = next battle, yellow = hold/counter-push choice.

## Leader actions

| Action | Who | Service call |
|--------|-----|--------------|
| Hold | Defender leader | `CampaignProgressionService.applyDefenderHold` |
| Counter-push | Defender leader | `CampaignProgressionService.applyDefenderCounterPush` |
| Accept white peace | Enemy leader | `WarManager.endWar(..., WHITE_PEACE)` |

After hold/counter-push: `WhitePeaceService.recalculateProposals` + persist; auto-end if both propose.

## Files

| File | Role |
|------|------|
| `War/progression/WhitePeaceService.java` | Proposal recalc + accept validation |
| `War/progression/CampaignRouteRenderer.java` | Route materials + lore |
| `Managers/Inventory/CampaignView.java` | Campaign GUI |
| `Managers/Inventory/CampaignCreator.java` | Item builders |
| `Managers/Holder/CampaignInventoryHolder.java` | warId + route page |
| `Managers/WarManager.java` | `endWar(War, WarEndReason)` |
| `Managers/InventoryManager.java` | View instance + confirm handlers |

## Out of scope (58.06+)

- WarView **Campaign** button (58.06)
- `warstatus` / regen polish (58.06)
- Hour voting UI (59)
- Battle engine hooks (59)

## Status

**Done** (2026-08-20). **Next batch:** [58.06 integration](./06-integration.md) (TBD).
