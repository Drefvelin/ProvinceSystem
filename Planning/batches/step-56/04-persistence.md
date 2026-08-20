# Step 56.04 — Persistence

**Step:** 56 · **Repo:** SF

## Goal

Wars save on **every state change**, not only plugin disable.

## Scope

- [x] `Database.saveWar(War)` uses `WarMapper.toData`; `loadWars` uses `WarMapper.fromData`
- [x] `WarManager.persist(War)` called on: create (`addWar`), participant change (`acceptRequest`)
- [x] `schemaVersion: 2` in JSON (v2-only via mapper; no v1 migration)
- [x] Delete war file on `endWar`
- [x] `SimpleFactions.onDisable()` kept as safety flush
- [x] `RelationView`: `persist(w)` after civil-war flags

## Files

| File | Change |
|------|--------|
| `Database/Database.java` | War I/O via `WarMapper`; removed v1 serialize helpers |
| `Managers/WarManager.java` | `persist()`; hooks on `addWar`, `acceptRequest` |
| `Managers/Inventory/RelationView.java` | `persist(w)` after civil-war flags |
| `War/WarDataRoundTripTest.java` | Gson round-trip on v2 `WarData` |

## Verify

- [x] `mvn test package` passes
- [ ] Manual: create war → restart → war still active with same fields
- [ ] Manual: end war → file deleted

## Status

**Done** (2026-08-19). **Next batch:** [56.05 — Declare flow](./05-declare-flow.md).
