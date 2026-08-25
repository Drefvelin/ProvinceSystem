# Step 75.01 — Planning lock (War package tree)

**Plan + docs only.**  
**Authority for:** all 75.02–75.06 moves. Do not invent new package names mid-batch.  
**Status:** **done** (2026-08-24)

---

## Locked decisions (75.01)

| Decision | Value | Batch |
|----------|-------|-------|
| `BattleNamingService` | `War/battle/campaign/` | 75.04 |
| `BattlePermissions` | `War/battle/ui/` | 75.04 |
| `War/validation/*` | `War/declare/` | 75.04 |
| `War/core` | **Required** - move all root war types listed below | 75.04 |
| `ObjectiveProvincePicker` | `War/campaign/` (declare-time only) | 75.04 |

**War/core files (75.04):** `War.java`, `Side.java`, `Participant.java`, `WarGoal.java`, `WarCommitment.java`, `WarMapper.java`, `WarDeclareHelper.java`, `WarCommandHelper.java`, `WarDebugFormatter.java`.

---

## Principles

1. **Domain folders, not layer dumps.** Name packages after what staff/players say: campaign schedule, battle vote, fort ZOC, battle win checks.
2. **Repackage before merge.** IDE move/refactor + import updates only in 75.02–75.04.
3. **Prefer subpackages over mega-files.** SF core uses fat `Faction.java`, but war code is test-heavy; keep services separate until a domain clearly wants one owner class.
4. **No new top-level `War/schedule`.** That name meant two different things (campaign slot list vs hourly battle window).
5. **Enums stay enums.** Consolidate `War/enums` + war-domain enums in place; do not inline enums into services.

---

## Target tree (after 75.04)

```text
War/
├── core/                    # War, Side, Participant, WarGoal, WarCommitment, WarMapper, helpers
├── enums/
├── declare/                 # WarDeclareHelper, WarCommandHelper, validation (from War/validation)
├── commitment/
├── pathfinder/
├── objective/               # empty after 75.04 (ObjectiveProvincePicker → campaign/)
├── resolution/
├── campaign/
│   ├── WarCampaignService.java
│   ├── ObjectiveProvincePicker.java   # from War/objective (75.04)
│   ├── schedule/            # build, placer, trimmer, validator, build context, scheduled slot model
│   ├── zoc/                 # fort/port indexes, operational DTOs, FortControlService
│   ├── runtime/             # hourly window: tick, lookups, autoresolve, battle schedule orchestration
│   ├── vote/                # vote, quorum, eligibility, hour tally, close results
│   ├── admin/               # warschedule admin + feedback formatter
│   ├── ui/                  # CampaignUiCopy, time formatter, schedule logger
│   └── progression/         # moved from War/progression (route renderer, occupation, choices, white peace)
└── battle/
    ├── enums/
    ├── events/
    ├── engine/
    │   ├── core/            # Battle, BattleManager, sides, join, setup, factory, bounds, end support
    │   ├── capture/         # CapturePoint, PointManager, markers, BattleCapturePoints
    │   ├── win/             # FieldWin, SiegeWin, SiegeContest
    │   └── raid/            # Raid setup, respawn, elimination, RaidWin
    ├── campaign/            # scheduled-battle bridge + BattleNamingService (75.04)
    ├── warband/
    ├── military/
    ├── template/
    ├── persistence/
    ├── ui/                  # BattlePermissions (75.04)
    └── dev/                 # BattleDevMode
```

**Max siblings:** aim for ≤12 `.java` files per directory. Split again if a folder grows past that.

---

## Migration map — `War/schedule` → `War/campaign/*`

| Current | New package |
|---------|-------------|
| `CampaignScheduleBuilder`, `CampaignBattlePlacer`, `CampaignScheduleTrimmer`, `CampaignScheduleValidator`, `CampaignScheduleBuildContext`, `ScheduledCampaignBattle`, `CampaignScheduleService`, `BattleTrigger` | `War/campaign/schedule` |
| `FortZocIndex`, `PortSeaZocIndex`, `OperationalFort`, `OperationalPort`, `FortControlService` | `War/campaign/zoc` |
| `BattleScheduleService`, `BattleScheduleTickService`, `BattleScheduleLookups`, `BattleWindowService`, `BattleAutoresolveService`, `BattleSideMembers` | `War/campaign/runtime` |
| `BattleVoteService`, `BattleQuorumService`, `BattleVoterEligibility`, `BattleHourTally`, `QuorumResult`, `BattleVoteToggleResult`, `BattleScheduleCloseResult`, `CloseVoteOptions` | `War/campaign/vote` |
| `WarScheduleAdminService`, `WarScheduleAdminResult`, `WarScheduleFeedbackFormatter` | `War/campaign/admin` |
| `CampaignUiCopy`, `CampaignUiTimeFormatter`, `CampaignScheduleLogger` | `War/campaign/ui` |

Delete empty `War/schedule` when imports are clean.

---

## Migration map — `War/battle/engine` → subpackages

| Current | New package |
|---------|-------------|
| `Battle`, `BattleManager`, `BattleSide`, `BattleFactory`, `BattleJoinService`, `BattleSideSetupService`, `BattleContestSetup`, `BattlePlacementValidator`, `BattleBoundsService`, `BattleEndSupport`, `BattleRespawnRouting` | `War/battle/engine/core` |
| `CapturePoint`, `PointManager`, `CapturePointMarkerService`, `BattleCapturePoints` | `War/battle/engine/capture` |
| `FieldWinService`, `SiegeWinService`, `SiegeContestService` | `War/battle/engine/win` |
| `BattleRaidSetup`, `RaidRespawnService`, `RaidAttackerEliminationService`, `RaidWinService` | `War/battle/engine/raid` |

---

## Migration map — campaign tree (75.04)

| Current | New |
|---------|-----|
| `War/progression/*` (19 files) | `War/campaign/progression/*` |
| `War/campaign/WarCampaignService.java` | stays; becomes sibling of `schedule/`, `progression/` |
| `War/battle/naming/BattleNamingService.java` | `War/battle/campaign/` |
| `War/battle/util/BattlePermissions.java` | `War/battle/ui/` |
| `War/objective/ObjectiveProvincePicker.java` | `War/campaign/` |
| `War/validation/*` | `War/declare/` |
| `War/*.java` root domain types | `War/core/` (see locked decisions) |

---

## Optional merges (75.05 — done 2026-08-24)

| Candidates | Result |
|------------|--------|
| `BattleHourTally`, `QuorumResult`, `BattleVoteToggleResult`, `BattleScheduleCloseResult`, `CloseVoteOptions` | Merged into `War/campaign/vote/VoteResults.java` (nested records/enums) |
| `OperationalFort`, `OperationalPort` | Nested in `FortZocIndex` / `PortSeaZocIndex` |
| `WarScheduleAdminResult` | **Kept** in `War/campaign/admin/` (admin-specific) |
| `FieldWinService`, `SiegeWinService`, `SiegeContestService`, `RaidWinService` | **Kept separate** in `engine/win/` and `engine/raid/` |

---

## Test mirror rule

When main source moves packages, **move matching tests to the same relative path**:

| Main move | Test move |
|-----------|-----------|
| `src/main/java/.../War/schedule/Foo.java` | `src/test/java/.../War/schedule/FooTest.java` → `.../War/campaign/schedule/FooTest.java` |
| `src/main/java/.../War/progression/Bar.java` | `src/test/java/.../War/progression/BarTest.java` → `.../War/campaign/progression/BarTest.java` |
| `src/main/java/.../War/War.java` | `src/test/java/.../War/War*Test.java` → update imports; tests may stay at `War/` until renamed |

Update `package` declarations and imports in moved test files in the **same commit** as the main move.

**75.02 cleanup note:** `CampaignStatusFormatterTest` has no matching main class; during 75.02 rename to `WarScheduleFeedbackFormatterTest` if it duplicates that coverage, or delete if redundant.

---

## 75.02 external importers (update in same batch as moves)

Grep-verified importers of `me.Plugins.SimpleFactions.War.schedule` that must be updated when 75.02 runs:

**War / campaign**

- `War/campaign/WarCampaignService.java`
- `War/WarMapper.java`, `War/War.java`, `War/WarDebugFormatter.java`
- `War/progression/CampaignRouteRenderer.java`, `CampaignRouteEntry.java`, `CampaignPushProjection.java`
- `War/progression/CampaignMilitaryWalkoverService.java`, `CampaignCapabilityService.java`
- `War/progression/CampaignPostBattleChoiceService.java`, `CampaignOffensiveForfeitService.java`
- `War/battle/campaign/CampaignBattleOutcomeService.java`, `CampaignBattleLaunchService.java`, `CampaignBattleTypeResolver.java`
- `War/battle/naming/BattleNamingService.java`
- `War/battle/military/BattlePoolService.java`, `BattleCasualtyService.java`
- `War/commitment/WarCommitmentService.java`, `LevySnapshotCalculator.java`

**Managers / bootstrap**

- `SimpleFactions.java` (schedule tick registration)
- `Managers/CommandManager.java`
- `Managers/Inventory/CampaignView.java`, `CampaignCreator.java`
- `Managers/RequestManager.java`
- `Utils/TabCompletion.java`

**Map export**

- `Map/export/WarMapExporter.java`, `ZocRealm.java`

**Tests (`src/test/java/.../War/schedule/` - 19 files, move with mirror rule)**

- `CampaignBattlePlacerTest`, `CampaignScheduleBuilderTest`, `CampaignScheduleTrimmerTest`
- `CampaignScheduleServiceTest`, `ScheduledCampaignBattleTest`
- `FortZocIndexTest`, `FortControlServiceTest`, `PortSeaZocIndexTest`
- `BattleScheduleServiceTest`, `BattleScheduleTickServiceTest`, `BattleScheduleLookupsTest`
- `BattleWindowServiceTest`, `BattleQuorumServiceTest`, `BattleVoteServiceTest`, `BattleVoterEligibilityTest`
- `WarScheduleAdminServiceTest`, `WarScheduleFeedbackFormatterTest`, `CampaignUiTimeFormatterTest`
- `CampaignStatusFormatterTest` (orphan - see test mirror note)

**Cross-package war tests (imports only, no move unless under `War/schedule/`)**

- `War/campaign/WarCampaignServiceTest.java`
- `War/WarMapperTest.java`, `WarDebugFormatterTest.java`, `WarPersistenceFileTest.java`
- `War/progression/CampaignRouteRendererTest.java`, `CampaignCapabilityServiceTest.java`
- `War/battle/campaign/CampaignBattleOutcomeServiceTest.java`, `CampaignBattleLaunchServiceTest.java`
- `War/battle/naming/BattleNamingServiceTest.java`
- `Map/export/WarMapExporterTest.java`, `ZocRealmTest.java`

---

## Import / test rules during moves

1. Update **main**, **test**, and **Database** references in the same commit.
2. Grep old package string before closing batch: `War.schedule`, old `battle.engine` flat imports.
3. Do not change serialized class names or Gson type adapters unless `WarMapper` / `BattleMapper` are updated in the same batch.
4. ProvinceSystem frontend/backend: grep `SimpleFactions/War` in the monorepo; war JSON shape is unchanged.

---

## New code rules (summary; full text in AGENTS.md)

- New campaign schedule logic → `War/campaign/schedule`
- New hourly vote / quorum logic → `War/campaign/vote`
- New battle runtime / capture / win → matching `battle/engine/*` subpackage
- New progression / occupation / peace → `War/campaign/progression`
- New war domain types → `War/core` (after 75.04)
- Do **not** add files directly under `War/` root after 75.04

---

## Acceptance

- [x] This lock reviewed before 75.02 starts
- [x] No batch renames packages outside this map without updating this file
