# Step 61b.03 — Battle devmode toggle & phantom warbands

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61b.02 capture threshold](./02-capture-threshold.md) · **Next:** [61b.04 campaign join rules](./04-campaign-join-rules.md)

## Goal

Admin-only volatile devmode toggle and automatic phantom member seeding on warband creation when enabled.

## New component

Path: `simplefactions/.../War/battle/dev/BattleDevMode.java`

| Method | Purpose |
|--------|---------|
| `isEnabled()` | Read volatile flag |
| `setEnabled(boolean)` | Toggle (command only) |
| `resetForTests()` | Test isolation |
| `seedPhantoms(Warband warband, int count)` | Add deterministic phantom UUIDs to `memberIds` |

Optional config (load once at enable or from Cache):

| Key | Default |
|-----|---------|
| `battle.devmode.phantom_count` | `10` |

## Command wiring

Extend [`BattleCommandManager`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/ui/BattleCommandManager.java):

```text
/battle devmode on
/battle devmode off
/battle devmode status
```

- Admin gate before existing `BattlePermissions.isAdmin` block pattern  
- `status` prints enabled + phantom count  
- Tab complete: `devmode`, `on`, `off`, `status`

Update [`BattleTabCompletion`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/ui/BattleTabCompletion.java) if battle subcommands are listed there.

## Warband create hooks

| Entry | Hook |
|-------|------|
| Manual `new Warband(id, player)` | After construct in `/warband create` path |
| Campaign `new Warband(war, par, offense)` | End of constructor or factory call in [`CampaignBattleRosterService`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleRosterService.java) / [`WarView`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Managers/Inventory/WarView.java) |

Add package-visible helper on `Warband`:

| Method | Purpose |
|--------|---------|
| `addPhantomMembers(int count)` | Only callable from `BattleDevMode.seedPhantoms` |
| `isPhantomMember(UUID id)` | Optional; prefix check on deterministic UUID or parallel `Set<UUID> phantomIds` |

**Do not** change `getPlayers()` - stays online-only per lock.

Display: [`BattleInventoryManager.createWarbandItem`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/ui/BattleInventoryManager.java) lore may show `getMemberCount()` (includes phantoms) vs online count for clarity in devmode.

## Tests

`BattleDevModeTest`:

| Test | Assert |
|------|--------|
| `toggle_notPersisted` | Flag resets in `resetForTests` / new JVM |
| `seedPhantoms_addsTen` | Member count = 1 leader + 10 |
| `phantomIds_deterministic` | Same warband id produces same UUIDs |
| `getPlayers_stillOnlineOnly` | Phantoms not in `getPlayers()` |

## Out of scope

- Phantom removal command (delete warband is enough)  
- Seeding defender side automatically  

## Verification

- [x] `/battle devmode on` seeds manual warband with 11 total members  
- [x] Restart clears devmode  
- [x] `mvn test` green  

**Done** (2026-08-21). **Next:** [61b.04 campaign join rules](./04-campaign-join-rules.md).
