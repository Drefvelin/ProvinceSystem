# Step 61c.08 - Campaign warband UX polish

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.07 campaign warband hotfixes](./07-campaign-warband-hotfixes.md) · **Next:** [62 war end & goals](../step-62/00-index.md)

## Goal

Polish campaign test UX: battle edit shows name, warschedule tab completion, devmode phantom fill on `battlecreate`, live warband list GUI, side lives roster display, and fix broken faction GUI auto-refresh (military view).

## Changes

| Area | Detail |
|------|--------|
| **Battle edit** | Info item at slot 13: display name + id lore |
| **Warschedule tabs** | `battlecreate`, `battlestart` in tab completion |
| **Devmode battlecreate** | When devmode on, `battlecreate` seeds phantoms to lives cap; first phantom is leader until war side leader joins |
| **InventoryUpdater** | Route by `SFGUI` type first (fixes military/installations/diplomacy when faction id == guild id) |
| **MilitaryView** | Clear stale button/regiment slots on refresh |
| **Warband list** | `populateWarbandList()`; refresh on click + 20L timer |
| **Warband lore** | Pre-start: `Players: N/cap`; post-start: `Lives: N` |
| **Join errors** | Lives-framed chat messages for roster full / no lives |

## Verification

- [x] `InventoryUpdaterTest`, `BattleDevModeTest`, `WarScheduleAdminServiceTest`, `CampaignBattleJoinServiceTest`
- [x] `mvn test` green

Manual:

- [ ] `/battle devmode on` then `warschedule battlecreate` fills both sides with test dummies
- [ ] War leader join promotes over phantom leader
- [ ] Military GUI queue timer ticks every second
- [ ] Warband list updates on click and every second
- [ ] `/battle edit` shows battle display name

**Done** (2026-08-21). **Next:** [61c.09 battle warband persistence](./09-battle-warband-persistence.md).
