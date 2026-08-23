# Step 61c.04 — Campaign warband signup

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.01 planning lock](./01-planning-lock.md) · **Next:** [61c.05 docs verify](./05-docs-verify.md)

## Goal

Campaign battles auto-create and auto-enroll faction warband **shells**. Players **opt in** via warband join. No auto-add of war leader. Leader rules: first signup leads; war leader signup promotes.

## Files to change

| File | Change |
|------|--------|
| [`Warband.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/warband/Warband.java) | Campaign constructor: empty `memberIds`, pending leader UUID; `addPlayer` promotes leader; war-leader promotion hook |
| [`CampaignBattleRosterService.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleRosterService.java) | Create shell only; move phantom seed to first signup |
| [`BattleDevMode.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/dev/BattleDevMode.java) | `seedPhantomsIfEnabled` on first real signup (called from join path) |
| [`WarbandManager.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/warband/WarbandManager.java) / list GUI | Join path calls promotion + phantom seed |
| [`CampaignBattleLaunchService.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleLaunchService.java) | Broadcast: `/warband list` signup, not `/battle join` |
| [`BattleCommandManager.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/ui/BattleCommandManager.java) | Campaign `/battle join` redirect message |
| [`BattleJoinService.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/BattleJoinService.java) | Allow warband with pending leader on side (already on side via roster service) |

## Campaign warband constructor (new behavior)

```text
id = par.getLeader().getId()
name = par.getLeader().getName() + " Host"
leaderId = pendingLeaderUuid(warbandId)
memberIds = empty
locked = true, faction = true
slots = unchanged (participant military)
NO muster title until first signup (optional: broadcast on battle ready instead)
```

Remove block that adds online war leader to `memberIds` at construct time.

## Signup leader rules

```java
void onCampaignSignup(Warband warband, War war, Player player) {
    if (isPendingLeader(warband.getLeaderId())) {
        warband.setLeader(player);
    } else if (isWarSideMainLeader(war, player)) {
        warband.setLeader(player); // promotes over first joiner
    }
    warband.addPlayer(player);
    BattleDevMode.seedPhantomsOnFirstSignupIfEnabled(...); // once per warband
}
```

`isWarSideMainLeader`: player name equals `Participant.getLeader().getLeader()` for the warband's main faction on that side.

## Auto-enroll unchanged

[`CampaignBattleRosterService.enrollParticipant`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleRosterService.java) still calls `BattleJoinService.join(warband, battle, side)` after shell create. Guard: pending leader must not block join (skip "already signed up" checks that require real leader online).

Update guard at line 44-46: only skip if warband already on battle side, not if `getLeaderId()` is pending sentinel with zero members.

## `/battle join` on campaign

When `battle.getWarId() != null` and player uses `/battle join`:

- Return: `Sign up with /warband list - your faction warband is already on this battle`
- Do not add duplicate bands

Player-led `/battle join` for campaign is **deprecated**; warband shell is pre-enrolled.

## Tests

| Suite | Cases |
|-------|--------|
| `WarbandCampaignSignupTest` (new) | Shell has 0 members; pending leader |
| | First join sets leader |
| | Second join does not steal leader |
| | War leader join promotes to leader |
| | Devmode phantoms after first signup only |
| `CampaignBattleRosterServiceTest` | Shell auto-joins battle side with 0 members |
| `CampaignBattleJoinServiceTest` | Adjust fixtures: signup before cap tests |
| `BattleDevModeTest` | Phantom seed moved to signup hook |

## Verification

- [x] War leader online at battle create is **not** in warband until they join  
- [x] First signup becomes leader; war leader signup promotes  
- [x] Campaign broadcast mentions warband signup  
- [x] `mvn test` green  

**Done** (2026-08-21). **Next:** [61c.05 docs verify](./05-docs-verify.md).
