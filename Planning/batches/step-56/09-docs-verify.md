# Step 56.09 — Docs verify

**Step:** 56 · **Repo:** SF + Planning

## Goal

Close step 56 with tests, manual checklist, and hub doc updates.

## Tests

```bash
cd simplefactions
mvn -q test   # after unit tests added in 56.03+
```

- [x] `WarGoalValidator` tests — `WarGoalValidatorTest`
- [x] Persistence round-trip test (temp dir) — `WarPersistenceFileTest`
- [x] `endwar` parse regression test — `WarDebugFormatterTest.parseWarId_*`

## Manual checklist (staging verify)

Run on a test server before production declare codes (step 68):

- [x] Declare war without code between two test factions (`war.require_declare_code: false`)
- [x] Invalid annex (settlement in target region) rejected with clear message (de jure option hidden)
- [ ] Ally call works and persists across restart (deferred)
- [x] Admin `/faction endwar <id>` ends correct war (regression for 56.08 parse fix)
- [x] War persists across server restart

## Post-56 follow-up (2026-08-20)

- [x] Remove **Switch sides** from war GUI; subject rebellion via **movement system** only ([Wars.md](../../../../simplefactions/Documentation/Wars.md) § Participants)

## Docs

- [x] [Wars.md](../../../../simplefactions/Documentation/Wars.md) — step 56 marked done in build order
- [x] [war-build-order.md](../../war-build-order.md) — step 56 status
- [x] [08-implementation-checklist.md](../../08-implementation-checklist.md) — M7 step 56 batches

## Status

**Done** (2026-08-19). **Next step:** [57 — Pathfinder & campaign](../step-57/00-index.md).
