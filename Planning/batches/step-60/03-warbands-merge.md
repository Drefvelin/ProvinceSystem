# Step 60.03 — Warbands merge + membership fix

**Code batch.** Move Warbands into SimpleFactions under `War.battle.*`, wire lifecycle/commands, UUID membership with quit cleanup and auto rejoin.

**Repos:** `Workspace/simplefactions` (source copied from `Workspace/warbands`)  
**Depends on:** [60.02 province presence](./02-province-presence.md)  
**Next:** [60.04 battle domain](./04-battle-domain.md)

## Delivered

| Component | Path |
|-----------|------|
| Battle engine | `War/battle/engine/*` (`Battle`, `BattleSide`, `BattleManager`, `CapturePoint`, `LifeRecord`, `PointManager`) |
| Warband domain | `War/battle/warband/*` (`Warband`, `WarbandSlot`, `WarbandManager`) |
| Membership fix | `WarbandMembershipService`, `WarbandRejoinState`, `WarbandMembershipListener` |
| Staff UI / commands | `War/battle/ui/*` (`BattleCommandManager`, `BattleInventoryManager`, `BattleTabCompletion`) |
| Permissions | `War/battle/util/BattlePermissions.java` |
| Enums | `War/battle/enums/LifeType.java` |
| SF integration | `WarView.java`, `WarCreator.java` imports updated |
| Plugin wiring | `SimpleFactions.onEnable()` — managers, listeners, `/warband` + `/battle` |
| Dependencies | Removed external Warbands jar; added VehicleFramework system dependency + `softdepend` |
| Marker tick | Ally/friend particles every **20 ticks** (1s), online members only |

## Package map

| Warbands source | SF target |
|-----------------|-----------|
| `Objects.Side` | `BattleSide` (rename; avoids clash with `War.Side`) |
| `Objects.Battle`, `CapturePoint`, `LifeRecord` | `War.battle.engine.*` |
| `Objects.Warband`, `WarbandSlot` | `War.battle.warband.*` |
| `Managers.*` | `War.battle.engine.*`, `warband.*`, `ui.*` |
| `Enums.LifeType`, `Util.Permissions` | `War.battle.enums.*`, `War.battle.util.BattlePermissions` |

## Membership fix

- Warband members stored as `Set<UUID>` (`leaderId` + `memberIds`).
- **Quit:** save `WarbandRejoinState`, remove member, decrement faction slot, detach boss bar / `currentBattle`.
- **Join:** auto re-add when warband still exists and slot/open rules pass; restore boss bar + per-player life record if battle active.
- Particle markers iterate `getOnlineMembers()` only (no stale logout positions).

## Tests

| Test class | Coverage |
|------------|----------|
| `War/battle/warband/WarbandMembershipServiceTest` | Quit state + removal, open rejoin, deleted warband skip, slot full, faction mismatch |

**163 tests** passing (2026-08-20).

## Manual staging checklist

- [ ] Muster warband from war GUI; ally markers show between online members
- [ ] Player quits; markers at logout spot stop immediately; member count drops
- [ ] Same player rejoins within a few seconds; auto re-added; markers return
- [ ] `/warband leave` still works; leader cannot leave without delete
- [ ] `/battle create` + staff setup still opens battle GUI
- [ ] Server starts with standalone **Warbands.jar removed** from plugins folder; only SF jar

## Deployment note

Remove standalone `Warbands.jar` from the TFMC server plugins folder after deploy to avoid duplicate command/listener registration.

## Status

**Done** (2026-08-20). **Next:** [60.04 battle domain](./04-battle-domain.md).
