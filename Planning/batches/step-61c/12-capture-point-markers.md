# Step 61c.12 - Capture point dust markers

**Code batch.** Per-player colored particle pillars at capture points during FIELD battles.

**Repo:** SF  
**Depends on:** [61c.11b capture point chain sync](./11-capture-point-chain-sync.md)

## Behavior

When a FIELD battle with capture points is running, each participant sees a vertical DUST pillar at every capture point. Colors are per-player and update every 0.5s (10 ticks).

| Color | Meaning |
|-------|---------|
| Gray | Sequential capture ON and point is not the current front |
| Yellow | Contested (multiple sides in zone, or capture progress between 0-100 with players present) |
| Green | Friendly-held (your side controls the point) |
| Red | Enemy-held |

Pillars rise ~100 blocks from the point location (size 3.5 DUST particles for long-range visibility). Gray DUST segments connect consecutive points in chain order (`sequenceIndex`). All particles use **`Player.spawnParticle`** (per-viewer, not `World.spawnParticle`) so markers stay visible at long range. No world blocks or light sources are placed.

## Key paths

- `War/battle/engine/CapturePointMarkerService.java`
- `War/battle/engine/CapturePoint.java` (`isContested()`)
- `War/battle/engine/PointManager.java` (tick integration)

## Tests

- `CapturePointMarkerServiceTest` - gray/yellow/green/red priority rules

**Done** (2026-08-21).
