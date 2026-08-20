# Step 55.03 — Construction queue

**Repo:** `simplefactions`

Deferred construction: max **one** build per faction; tick to completion; persist across restarts.

## Model

`InstallationConstruction` (or equivalent):

| Field | Notes |
|-------|--------|
| `id` | Pre-allocated installation id (same as final) |
| `name` | Display name |
| `kind` | `InstallationKind` |
| `province` | Province id |
| `centerX` / `centerZ` | Block coords |
| `timeLeft` | Seconds remaining |
| `startedAt` | Epoch ms — tie-break for upkeep destroy order after complete |

## Handler changes

1. `construct()` — after step-54 validation, if queue non-empty → fail; else enqueue with `timeLeft = config construction-time`.
2. Reserve `byProvinceKind` (or parallel `pendingByProvinceKind`) so duplicate kind on province blocked while building.
3. `tick()` on faction — decrement active construction; at 0 → `register(Installation)`, set `completedAt`, enqueue map update, notify leader if online.
4. `deconstruct(id)` during construction — remove from queue, release province lock, map update if needed.
5. `serialize()` / `load()` on `FactionData` — `installationQueue` (single entry or list max 1).

## Map export

`Markers.java` — only operational installations (exclude queue).

## Done when

- `/faction construct fort Test` does not appear on map until timer completes
- Second construct while one building → rejected
- Restart preserves in-progress build + timeLeft

## Status

**Done** (2026-08-19). Verified: `mvn -q package -DskipTests`.

## Next

[04-upkeep-ledger](./04-upkeep-ledger.md)
