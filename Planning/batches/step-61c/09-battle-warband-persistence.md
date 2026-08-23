# Step 61c.09 - Battle & warband persistence

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.08 campaign warband UX](./08-campaign-warband-ux.md) · **Next:** [62 war end & goals](../step-62/00-index.md)

## Goal

Persist battles and attached warbands to JSON (crash-safe autosave), resume in-progress fights on restart, enforce one manual battle at a time with a GUI delete button, and purge orphan manual warbands on shutdown.

## Changes

| Area | Detail |
|------|--------|
| **DTOs** | `BattleData`, `BattleSideData`, `CapturePointData`, `WarbandData` under `Database/` |
| **Mappers** | `BattleMapper`, `WarbandMapper` under `War/battle/persistence/` |
| **Service** | `BattlePersistenceService`: `saveAll`, `loadAll`, `persistBattle/Warband`, orphan purge, campaign delete |
| **Files** | `plugins/SimpleFactions/Battles/battle_{id}.json`, `Warbands/warband_{id}.json` |
| **Lifecycle** | Load after `WarManager.start()`; 60s autosave; `onDisable` saves instead of `battleManager.end()` |
| **Resume** | `started=true`, side lives, capture state, contest timer restored; tick loop resumes |
| **Manual limit** | `/battle create` blocked when any `warId == null` battle exists |
| **GUI delete** | Slot 22 TNT button on manual, not-started battle edit view |
| **Orphan purge** | Manual warbands not referenced by any battle removed on `saveAll` / disable |

## Verification

- [x] `BattleMapperTest`, `WarbandMapperTest`, `BattlePersistenceServiceTest`
- [x] `mvn test` green

Manual:

- [ ] Create manual battle, set spawn/point, restart - battle restored
- [ ] Start manual battle, change lives/capture, restart - fight resumes
- [ ] Second `/battle create` blocked until delete
- [ ] Delete button removes battle + frees slot
- [ ] Create manual warband not on any battle, restart - warband gone
- [ ] Campaign battle + signup, restart - warbands and battle restored

**Done** (2026-08-21). **Next:** [61c.10 battle side fast edit](./10-battle-side-fast-edit.md).
