# Step 58.07 — Docs verify

**Step:** 58 · **Repo:** SF + Planning

## Goal

Close step 58 with tests, manual checklist, and hub doc updates.

## Tests

```bash
cd simplefactions
mvn -q test
mvn -q package
```

**Result (2026-08-20):** `mvn test` — **85 tests**, 0 failures. `mvn package` — **pass**.

### Step 58 unit tests

| Class | Cases | Covers |
|-------|-------|--------|
| `CampaignProgressionServiceTest` | 16 | FSM, cursor, initiative, next battle nodes, hold/counter-push |
| `OccupationServiceTest` | 10 | Zone compute, battle win merge, neighbor rules |
| `WhitePeaceServiceTest` | 6 | Auto-propose, accept, auto-end |
| `CampaignRouteRendererTest` | 5 | Blue/red/green/yellow materials + lore |
| `WarCampaignServiceTest` | 4 | Full axis, cursor at border B, capital-closer objective |
| `WarManagerCampaignTest` | 3 | Regen, raid skip, persist |
| `WarDebugFormatterTest` | 4 | `warstatus` JSON incl. 58.06 fields |
| `WarPersistenceFileTest` | 1 | Round-trip all Step 58 persistence fields |
| `WarMapperTest` | 1 | Mapper serialization of 58 fields |

### Step 57 carry-over (still in suite)

- [x] `ProvincePathfinderTest` — 7 cases
- [x] `ObjectiveProvincePickerTest` — 4 cases
- [x] `WarCampaignServiceTest` — pathfinder integration via populate
- [x] `WarManagerCampaignTest` — declare/regen hook
- [x] `WarDataRoundTripTest`, `WarDeclareHelperTest`, `WarCommitmentTest`, `WarGoalValidatorTest`

## Manual checklist (staging verify)

Run on a test server before production declare codes (step 68):

Prerequisites: `war.require_declare_code: false`, two factions with a reachable land/sea route, admin permission for war commands, active test war (e.g. Brume vs Lantan war `0` if still on staging).

- [ ] **Declare** subjugate war - `/faction warstatus <id>` shows full axis (`campaignProvinces` includes attacker capital), `cursorIndex` at border **B** (not legacy step-57 short axis with `cursorIndex: 0`)
- [ ] **Restart** - `war_{id}.json` retains Step 58 fields (`initiativeAttacker`, `initiativeDefender`, `campaignPhase`, `occupiedByAttacker`, `occupiedByDefender`, `lastBattleOccupied`, proposal flags, `campaignBattlesFought`)
- [ ] **`/faction warpath <id>`** - regen succeeds; success line shows cursor/province/phase/initiative; JSON dump includes `nextBattleNodes`, `cursorProvinceId`
- [ ] **WarView navigation** - participant sees Campaign button (slot 49); opens CampaignView; back (slot 53) returns to WarView
- [ ] **Campaign GUI** - route row colors match legend; info slot shows initiative/phase/proposals; defender leader can hold/counter-push when attacker initiative exhausted; enemy leader can accept white peace when proposed
- [ ] **Legacy upgrade** - `/faction warpath <id>` on old short-axis war upgrades to full axis with cursor at border B

## Post-58 follow-up

- [ ] Battle engine hooks (`CampaignProgressionService` + `OccupationService` on battle win) - Step **59**
- [ ] Hour voting UI - Step **59**
- [ ] Re-enable declare pre-checks in `RelationView` before production - Step **68**
- Raid war type skips campaign at declare (implemented); full raid routes - Step **66**; map occupation export - Step **67**

## Docs

- [x] [Wars.md](../../../../simplefactions/Documentation/Wars.md) - step 58 marked done in build order
- [x] [war-build-order.md](../../war-build-order.md) - step 58 status
- [x] [08-implementation-checklist.md](../../08-implementation-checklist.md) - M7 step 58 batches
- [x] [01-current-state.md](../../01-current-state.md) - step 58 done, next 59

## Status

**Done** (2026-08-20). **Next step:** [59 - Battle scheduling](../step-59/00-index.md).
