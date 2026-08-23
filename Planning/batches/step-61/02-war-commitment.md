# Step 61.02 — War commitment snapshot

**Done** (2026-08-20). **Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61.01 planning lock](./01-planning-lock.md) · [61.01b levy & vassal lock](./01b-levy-vassal-lock.md) · **Next:** [61.04 collective lives](./04-collective-lives.md)

## Goal

Replace step **56.07** stub commits (`count = 0`) with real declare-time snapshots for every regiment type and levy pool, scoped by `war_id`. Implement the nearest-fighter holder algorithm from 61.01b (not naive per-fighter `getLevies()`).

## Current gap

**Resolved in 61.02.** Implemented in [`WarCommitmentService`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/commitment/WarCommitmentService.java) + [`LevySnapshotCalculator`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/commitment/LevySnapshotCalculator.java). Commitments remain in-memory until 61.06 persistence.

## Deliverables

### `WarCommitmentService` (new, or expand `WarManager`)

| Method | Purpose |
|--------|---------|
| `commitFaction(War war, Faction faction)` | Idempotent own-regiment snapshot for one fighter |
| `snapshotLevyForSide(War war, Side side)` | Nearest-holder levy walk for all fighters on side |
| `snapshotLevyForFighter(War war, Faction fighter)` | Ally-join levy snapshot (joiner only) |
| `removeLevySubtree(Faction brokenSubject)` | Cascade removal per 61.01b |
| `commitAllParticipants(War war)` | All fighters + levy snapshots both sides |
| `getCommitmentsForWar(int warId)` | Existing API — return frozen rows |
| `totalCommittedRegiments(warId, factionIds, poolFilter)` | Used by 61.03/61.04 |

### Snapshot rules

Authoritative spec: [61.01b levy & vassal lock](./01b-levy-vassal-lock.md).

For each **fighter** faction:

**Own regiments** (non-levy): row per `(warId, factionId, regimentId)` at first commit. Battle pool (61.03) reads **live** `currentSlots` for fighters.

**Levy** (frozen): one row per `(holderFactionId, sourceFactionId, levy)` via nearest-fighter walk:

- Do **not** call `getLevies()` independently on every fighter (double-count risk)
- Walk each levy-only source up to nearest fighter in `BattleSideMembers.collectParticipatingFactions`
- Count uses same math as `Military.getLevies()` for the path from source to holder

### `WarCommitment` schema change

Add `sourceFactionId` (nullable). Levy unique key: `(warId, holderFactionId, sourceFactionId, levy)`.

### Triggers

| Call site | When |
|-----------|------|
| `WarManager.declareWar` | `commitAllParticipants` + `snapshotLevyForSide` both sides |
| Ally join (`War.call` success path) | `commitFaction(war, joiner)` + `snapshotLevyForFighter(war, joiner)` |
| `RelationManager.endVassalage` | `removeLevySubtree` on active wars |
| `RelationManager.transferSubject` | Remove only (no re-snapshot) |
| `RelationManager.setRelation` new vassalage | Explicit no-op for war levy |
| New vassal mid-war | **No** new levy rows (main or ally overlord) |

### Persistence (minimal for 61.02)

| Option | Batch |
|--------|-------|
| In-memory only (match today) | 61.02 OK if tests cover reload gap |
| Serialize in `WarData` / DB | Prefer **61.06** with casualty apply; document gap in 61.02 |

## Tests

Extend [`WarCommitmentTest`](../../../../simplefactions/src/test/java/me/Plugins/SimpleFactions/War/WarCommitmentTest.java):

| Test | Assert |
|------|--------|
| `commitFaction_capturesRegimentSlots` | professional/militia counts match mocked military |
| `nestedVassal_holderIsNearestFighter` | M→V→V2→V3: rows `V←V2`, `V←V3`; not duplicated on M |
| `commitFaction_idempotent` | second call returns same rows, no duplicate |
| `commitAllParticipants_includesSubjects` | subject fighters get own rows; levy-only nested vassals are sources only |
| `allyJoin_addsLevySnapshot` | joiner levy rows at accept; main pool unchanged |
| `bottomVassalBreak_removesSubtree` | V2 break removes `V←V2` and `V←V3` |
| `newVassal_noAdd` | mid-war vassalage creates no levy rows |
| `transferSubject_removeOnly` | old subtree removed; new overlord gets no snapshot |

## Manual staging

1. Declare test war → `/faction wardebug` (or admin) shows non-zero commitment counts per regiment  
2. Re-declare attempt on same factions → counts unchanged (idempotent per war)  
3. Nested vassal war: confirm levy rows show nearest fighter as holder, not top overlord

## Out of scope

- Battle pool filtering (61.03)
- Applying casualties (61.06)

## Verification (61.02)

- [x] `WarCommitment.sourceFactionId` added
- [x] `WarCommitmentService` + `LevySnapshotCalculator` implemented
- [x] Declare / ally join / vassal break hooks wired
- [x] `WarCommitmentTest` + `LevySnapshotCalculatorTest` passing
- [x] Full `mvn test` green
