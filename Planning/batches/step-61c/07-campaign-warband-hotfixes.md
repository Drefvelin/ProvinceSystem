# Step 61c.07 - Campaign warband hotfixes

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.06](./06-warband-list-naming.md) · **Next:** [62 war end & goals](../step-62/00-index.md)

## Goal

Fix test-server campaign pain: one warband per battle side, regiment-driven lives (no faction slots), mid-battle join/leave, staff `battlecreate`/`battlestart`, remove Muster Army GUI.

## Locked changes

| Area | Behavior |
|------|----------|
| Warband model | One shell per side (`campaign_w{id}_{attacker\|defender}`), auto-created at battle prep |
| Join who | Faction must be on the warband's war side |
| Join how many | Pre-battle: roster cap = preview lives from committed regiments. Mid-battle: requires side lives > 0; join consumes 1 life |
| 0 regiments | Side lives = 0 at start (no min floor) |
| Leave | Campaign warbands cannot be deleted; leader may leave with oldest promotion; mid-battle voluntary leave blocks rejoin |
| Staff | `warschedule battlecreate` (green province only, any phase), `warschedule battlestart` |
| GUI | Muster Army removed; signup via `/warband list` only |

## Files touched

- [`Warband.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/warband/Warband.java) - side shells, removed slots
- [`CampaignBattleRosterService.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleRosterService.java)
- [`CampaignWarbandBattleService.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignWarbandBattleService.java)
- [`CampaignWarbandLeaveBlock.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignWarbandLeaveBlock.java)
- [`WarScheduleAdminService.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/WarScheduleAdminService.java)
- [`WarView.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Managers/Inventory/WarView.java) - removed muster
- Deleted [`WarbandSlot.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/warband/WarbandSlot.java)

## Test gate

```bash
cd simplefactions && mvn test
```

New/updated: `CampaignBattleRosterServiceTest`, `WarbandCampaignSignupTest`, `CampaignBattleJoinServiceTest`, `CampaignWarbandBattleServiceTest`, `BattleLivesServiceTest`, `WarScheduleAdminServiceTest`, `BattleScheduleTickServiceTest`

## Status

**Done** (2026-08-21)
