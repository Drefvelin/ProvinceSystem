# Step 61b.04 — Campaign join rules (side + lives cap)

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61b.03 battle devmode](./03-battle-devmode.md) · **Next:** [61b.05 docs verify](./05-docs-verify.md)

## Goal

Campaign battles (`battle.warId != null`) enforce war-side membership and cap total roster size by computed collective lives. Bypass faction `WarbandSlot` limits for campaign warbands.

## New / updated components

### `CampaignBattleJoinService` (recommended)

Path: `simplefactions/.../War/battle/campaign/CampaignBattleJoinService.java`

| Method | Purpose |
|--------|---------|
| `validateJoin(War war, Battle battle, Warband warband, String sideId, Player joiningPlayer)` | Returns error message or null |
| `countSideRoster(Battle battle, String sideId)` | Sum `warband.getMemberCount()` on side |
| `previewSideLivesCap(War war, Battle battle, String sideId)` | `BattleLivesService.computeSideLives` using pool + online count on that side |

### Integration points

| Location | Change |
|----------|--------|
| [`BattleJoinService.join`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/BattleJoinService.java) | If `battle.getWarId() != null`, delegate to `CampaignBattleJoinService` before `side.addBand` |
| [`WarbandMembershipService.evaluateRejoin`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/warband/WarbandMembershipService.java) | Campaign: skip slot full check; run side cap check instead |
| [`BattleCommandManager`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/ui/BattleCommandManager.java) `/battle join` | Surfaces validation errors |
| [`BattleCommandManager`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/ui/BattleCommandManager.java) `/warband join` | If warband already on campaign battle side, validate cap on add member |

## Side membership algorithm

```text
faction = FactionManager.getByMember(playerName)
if faction == null -> reject (not in a faction)
warSide = war.getSide(faction)   // null if not at war
battleSide = map sideId to war attackers/defenders
if warSide != battleSide -> reject wrong side
```

Use [`BattleSideMembers.resolveSide`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/BattleSideMembers.java) where helpful.

## Lives cap algorithm

At join (pre-start):

```text
provinceId = battle.provinceId ?? war.scheduledBattleProvinceId
pool = BattlePoolService.totalCommittedRegiments(war, provinceId, warSide, mode)
onlineOnSide = count unique online players already on battle side warbands (excluding phantoms from lives count)
cap = BattleLivesService.computeSideLives(pool, onlineOnSide)
rosterAfter = countSideRoster including joining player's warband member count
if rosterAfter > cap -> reject
```

**Note:** Cap uses **online** count for lives formula but **member count** (incl. phantoms in devmode) for roster cap. Document in lock: devmode phantoms help test cap UI but cap is driven by lives preview; with solo + 10 phantoms, cap may block unless lives high enough - tune phantom count or cap logic in implementation:

**Implementation note (locked):** When seeding on campaign warband create, use `min(phantom_count, max(0, previewSideLivesCap - 1))` so leader + phantoms never exceed preview lives cap.

## Campaign slot bypass

In `WarbandMembershipService.evaluateRejoin` and warband join paths:

```java
if (warband.isFaction() && battle != null && battle.getWarId() != null) {
    // skip WarbandSlot.isFull()
    return campaignCapAllows(...);
}
```

Manual faction warbands (`warId null`) keep slots.

## Tests

`CampaignBattleJoinServiceTest`:

| Test | Assert |
|------|--------|
| `wrongSide_rejected` | Defender faction cannot join attacker side |
| `rosterCap_enforced` | Join fails when member count would exceed preview lives |
| `phantoms_countTowardCap_devmode` | With devmode, seeded phantoms included in roster sum |
| `playersAtStart_ignoresPhantoms` | Lives preview uses online only (mock BattleLivesService) |
| `manualBattle_noSideCheck` | warId null skips campaign validation |
| `campaignRejoin_bypassesSlotFull` | Slot max 0 but cap allows rejoin |

Extend [`BattleJoinServiceTest`](../../../../simplefactions/src/test/java/me/Plugins/SimpleFactions/War/battle/engine/BattleJoinServiceTest.java) with one campaign happy path.

## Out of scope

- Defender-side solo auto-fill  
- Changing `BattleLivesService.applyCampaignLives` formula  

## Verification

- [x] Attacker can join own side on scheduled campaign battle  
- [x] Wrong side gets clear error  
- [x] Roster cap message when full  
- [x] `mvn test` green  

**Done** (2026-08-21). **Next:** [61b.05 docs verify](./05-docs-verify.md).
