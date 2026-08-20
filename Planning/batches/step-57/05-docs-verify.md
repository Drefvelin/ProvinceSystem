# Step 57.05 — Docs verify

**Step:** 57 · **Repo:** SF + Planning

## Goal

Close step 57 with tests, manual checklist, and hub doc updates.

## Tests

```bash
cd simplefactions
mvn -q test
mvn -q package
```

**Result (2026-08-20):** `mvn test` — **45 tests**, 0 failures. `mvn package` — **pass**.

### Step 57 unit tests

- [x] `ProvincePathfinderTest` — 7 cases (land/sea/neutral passes, border start)
- [x] `ObjectiveProvincePickerTest` — 4 cases (capital, settlement, centroid, goal sets)
- [x] `WarCampaignServiceTest` — 1 case (populate campaign polyline)
- [x] `WarManagerCampaignTest` — 3 cases (declare hook, regen, raid skip)
- [x] Campaign persistence round-trip — `WarMapperTest`, `WarDataRoundTripTest`, `WarPersistenceFileTest`, `WarDebugFormatterTest`

## Manual checklist (staging verify)

Run on a test server before production declare codes (step 68):

Prerequisites: `war.require_declare_code: false`, two factions with a reachable land/sea route, admin permission for war commands.

- [x] Declare subjugate war — `/faction warstatus <id>` shows `objectiveProvinceId`, `campaignStartProvinceId`, `campaignProvinces`, `cursorIndex` (staging 2026-08-20: Brume vs Lantan, war `0` — objective `705`, start `706`, route `[706,705]`, `cursorIndex` `0`)
- [ ] Server restart — `war_{id}.json` retains campaign fields
- [ ] `/faction warpath <id>` regenerates route and persists

## Post-57 follow-up

- [ ] Re-enable declare pre-checks in `RelationView` before production (step 68)
- Raid war type skips campaign at declare (implemented); full raid routes → step **66**

## Docs

- [x] [Wars.md](../../../../simplefactions/Documentation/Wars.md) — step 57 marked done in build order
- [x] [war-build-order.md](../../war-build-order.md) — step 57 status
- [x] [08-implementation-checklist.md](../../08-implementation-checklist.md) — M7 step 57 batches
- [x] [01-current-state.md](../../01-current-state.md) — step 57 done, next 58

## Status

**Done** (2026-08-20). **Next step:** [58 — Initiative & occupation](../step-58/00-index.md).
