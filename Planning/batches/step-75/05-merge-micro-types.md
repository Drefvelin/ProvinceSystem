# Step 75.05 — Merge micro-types (optional)

**Depends on:** [75.04](./04-repackage-campaign-tree.md)  
**Status:** **done** (2026-08-24)  
**Optional:** skip entire batch if team prefers explicit record files

## Scope

Reduce tiny top-level types by nesting records or grouping static helpers. **Small behavior-preserving refactors only.**

## Candidates

### Vote / admin results → `War/campaign/vote/VoteResults.java`

Merge as public nested records:

- `BattleHourTally`
- `QuorumResult`
- `BattleVoteToggleResult`
- `BattleScheduleCloseResult`
- `CloseVoteOptions`

Keep `WarScheduleAdminResult` in `admin/` or add `AdminResults.java` in same style.

Update call sites to `VoteResults.QuorumResult` etc. Update tests.

### ZOC operational DTOs

- Nest `OperationalFort` inside `FortZocIndex`
- Nest `OperationalPort` inside `PortSeaZocIndex`

Only if Gson/Jackson and tests do not reflect on standalone classes.

### Win services

**Default:** leave `FieldWinService`, `SiegeWinService`, `RaidWinService` separate in `engine/win/`.

Merge into `BattleWinChecks` only if combined file stays ≤200 lines and tests remain readable.

## Rules

- One merge group per commit (vote results, then ZOC, then win).
- Run targeted tests after each commit:
  ```bash
  cd simplefactions && mvn test -Dtest="*Vote*,*Quorum*,*Schedule*,*Zoc*,*Win*"
  ```

## Done when

- [x] Net file count reduced without hiding domain concepts
- [x] `War.**` tests green
- [x] [01-planning-lock.md](./01-planning-lock.md) updated if merge targets differ from plan
