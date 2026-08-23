# Step 61b.02 — Capture point minimum players

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61b.01 planning lock](./01-planning-lock.md) · **Next:** [61b.03 battle devmode](./03-battle-devmode.md)

## Goal

Replace hardcoded **3 players** at a capture zone with config `battle.capture_min_players` (default **1**) so solo staging and linear capture work.

## Files

| File | Change |
|------|--------|
| [`config.yml`](../../../../simplefactions/src/main/resources/config.yml) | Add `battle.capture_min_players: 1` |
| [`Cache.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Cache.java) | `battleCaptureMinPlayers` field |
| [`ConfigLoader.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Loaders/ConfigLoader.java) | Load + validate `>= 1` |
| [`CapturePoint.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/CapturePoint.java) | Use `Cache.battleCaptureMinPlayers` instead of literal `3` |

## Behavior

In `CapturePoint.updateSides`, change:

```java
if (entry.getValue() == maxValueInMap && entry.getValue() >= 3)
```

to use config threshold.

Capture still requires strictly **more** players on one side than the other (existing max-side logic unchanged).

## Tests

| Test | Assert |
|------|--------|
| `ConfigLoaderBattleCaptureTest` (new or extend schedule test file) | Default 1 loaded |
| `CapturePointMinPlayersTest` | Mock side counts: 1 player on side captures when min=1; 0 does not |

## Manual

1. Start field battle with one capture point  
2. Stand alone in zone - bar progresses  
3. Set config to 2 temporarily - solo no longer caps  

## Out of scope

- Contest area min/max (siege) - separate keys if needed later  
- Devmode-specific override  

## Verification

- [x] Config default 1  
- [x] `mvn test` green  
- [x] No em dash in player-facing strings  

**Done** (2026-08-21). **Next:** [61b.03 battle devmode](./03-battle-devmode.md).
