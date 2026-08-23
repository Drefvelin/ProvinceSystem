# Step 60.02 — Province presence tracker

**Code batch.** Central 1-second province enter/leave poll, cached state, Bukkit events, quit cleanup.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [60.01 planning lock](./01-planning-lock.md)  
**Next:** [60.03 warbands merge](./03-warbands-merge.md)

## Delivered

| Component | Path |
|-----------|------|
| Enter event | `Events/PlayerProvinceEnterEvent.java` |
| Leave event | `Events/PlayerProvinceLeaveEvent.java` |
| Core service | `Map/presence/ProvincePresenceService.java` |
| Tick loop | `Map/presence/ProvincePresenceTickService.java` |
| Quit listener | `Map/presence/ProvincePresenceListener.java` |
| Config | `battle.province_poll_interval_ticks` (default **20**) |
| Plugin wiring | `SimpleFactions.onEnable()` after grid load |

## API

- `ProvincePresenceService.getInstance().getCurrentProvince(Player|UUID)` — cached; `-2` if untracked
- `isInProvince(Player, int)`
- Events: `PlayerProvinceEnterEvent`, `PlayerProvinceLeaveEvent`

## Tests

| Test class | Coverage |
|------------|----------|
| `Map/presence/ProvincePresenceServiceTest` | First enter, no-op same province, change, unknown transitions, quit |
| `Loaders/ConfigLoaderBattlePresenceTest` | Default interval, invalid `< 1` throws |

**158 tests** passing (2026-08-20).

## Manual staging checklist

- [ ] Join with map enabled; within ~1s first enter event fires (temporary debug listener)
- [ ] Walk across province border; leave then enter fire in order
- [ ] Quit; single leave event, no duplicate on rejoin until next enter
- [ ] `battle.province_poll_interval_ticks: 40` slows updates to 2s
- [ ] `enable-map: false` → province `-2` unknown; crossing back to enabled map fires transitions

## Status

**Done** (2026-08-20). **Next:** [60.03 warbands merge](./03-warbands-merge.md).
