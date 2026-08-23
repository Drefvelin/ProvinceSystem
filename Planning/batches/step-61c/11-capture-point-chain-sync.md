# Step 61c.11b - Capture point chain sync

**Code batch.** Global A-Z capture point naming and spatial chain ordering when sequential capture is enabled.

**Repo:** SF  
**Depends on:** [61c.11 battle setup hardening](./11-battle-setup-hardening.md)

## Rules

| Mode | Naming | Ordering |
|------|--------|----------|
| Sequential OFF | Global `A, B, C...` (no `A'`) | Compress letters on add/delete by existing `sequenceIndex` |
| Sequential ON | Force all points to letter ids | **A = closest point to defender spawn**; `B, C, D...` via greedy nearest-neighbor (XZ distance) outward from A |

`advanceSideId` stays as placed (which side owns the capture lane for that point). Sequential ticking uses **one global front** (lowest `sequenceIndex` not yet fully controlled by its `advanceSideId`).

## Sync triggers

- Sequential capture toggled **ON** in battle edit (slot 8)
- Add or delete capture point while sequential is ON
- Load persisted battle with `sequentialCapture == true` (fixes legacy `A'` saves)

When sequential is toggled **OFF**, points compress to global letters by `sequenceIndex`.

## Edge cases

- **Defender spawn unset:** anchor distance uses attacker spawn (server log warning)
- **Single point:** becomes `A`
- **Custom ids:** removed from `/battle addpoint`; legacy names renamed on next sync/compress
- **Battle started:** add/delete/sync from GUI remain blocked (existing guards)

## Key paths

- `War/battle/engine/BattleCapturePoints.java` (`compressGlobalLetters`, `syncLinearChain`, `afterPointListChanged`)
- `War/battle/engine/CapturePoint.java` (`isFrontPoint` global sequential mode)
- `War/battle/engine/PointManager.java`
- `War/battle/engine/BattleManager.java` (sequential toggle)
- `War/battle/persistence/BattlePersistenceService.java` (load sync)
- `War/battle/ui/BattleInventoryManager.java` (Point View sort + lore)

## Tests

- `CapturePointSequenceTest` - global naming and compress on delete
- `CapturePointChainSyncTest` - defender-spawn anchor, greedy NN, global front gating

**Done** (2026-08-21).
