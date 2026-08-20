# Step 56.02 — Domain model

**Step:** 56 · **Repo:** SF

## Goal

Introduce `War` v2 types and JSON DTOs; refactor `Side` / `Participant` to match [Wars.md](../../../../simplefactions/Documentation/Wars.md).

## Scope

- [x] Enums: `WarGoalType`, `WarType`, `WarStatus`, `WarEndReason` (subset used in 56)
- [x] `War` v2 fields: `id`, `warType`, `goal`, `status`, `attackerLeaderId`, `defenderLeaderId`, `targetTitleId?`, `objectiveProvinceId?` (nullable until step 57), `startedAt`, `endedAt?`
- [x] Per-participant `warGoals` deprecated on write path (`@Deprecated` on `Participant` helpers; omitted in `WarMapper.toData` when war has top-level goal)
- [x] `WarData` / Gson DTOs aligned with v2 schema (`schemaVersion: 2`)
- [x] `WarManager.newId()` unchanged; registry API: `getActive()`, `getByFaction()`, `exists()` (active-only)

## Files (expected)

- `War/War.java`, `War/WarMapper.java`, `War/enums/*.java`
- `War/Side.java`, `War/Participant.java`
- `Database/WarData.java`, `ParticipantData.java`, `SideData.java`
- `Managers/WarManager.java`

## Legacy file inventory

Every war-touching file in `simplefactions` (grep + manual audit). Owner batch = first batch that changes the file.

| File | Role | Owner batch |
|------|------|-------------|
| `War/War.java` | War entity | 56.02 |
| `War/Side.java` | Attacker/defender side container | 56.02, 56.06 |
| `War/Participant.java` | Faction on a side (leader, subjects, allies) | 56.02, 56.06 |
| `War/WarGoal.java` | Config goal wrapper (`wargoals.yml`) | 56.02 (deprecate per-participant use) |
| `Managers/WarManager.java` | War registry, notifications, `exists()` | 56.02, 56.04 |
| `Database/WarData.java` | Gson DTO for war JSON | 56.02, 56.04 |
| `Database/SideData.java` | Gson DTO for side | 56.02, 56.04 |
| `Database/ParticipantData.java` | Gson DTO for participant | 56.02, 56.04 |
| `Database/Database.java` | `saveWar` / `loadWars` | 56.04 |
| `Managers/Inventory/WarView.java` | War list + participant GUI | 56.05, 56.06 |
| `Managers/Inventory/WarCreator.java` | War GUI factory | 56.05, 56.06 |
| `Managers/Inventory/RelationView.java` | Diplomacy declare slot (slot 24) | 56.05 |
| `Managers/Inventory/MovementView.java` | Civil-war flag on participant | 56.06 |
| `Managers/CommandManager.java` | `warlist`, `endwar` | 56.08 |
| `Loaders/WarGoalLoader.java` | Loads `wargoals.yml` | 56.03 |
| `src/main/resources/wargoals.yml` | Legacy goal definitions | 56.03 |
| `Objects/Request/WarRequest.java` | Ally call-to-arms CTA | 56.06 |
| `Managers/RequestManager.java` | Routes `WarRequest` | 56.06 |
| `enums/Goal.java` | Legacy goal enum | 56.02 |
| `enums/SFGUI.java` | War GUI enum entries | 56.02 |
| `Managers/Holder/WarInventoryHolder.java` | War GUI holder | 56.06 |
| `Managers/Holder/SFCombinedInventoryHolder.java` | Combined holder (war tab) | 56.06 |
| `Managers/Inventory/InventoryUpdater.java` | War GUI refresh routing | 56.06 |
| `Managers/Inventory/InventoryManager.java` | Opens war views | 56.06 |
| `Utils/TabCompletion.java` | `warlist` / `endwar` tab complete | 56.08 |
| `SimpleFactions.java` | `onDisable` war save loop | 56.04 |
| `Guild/income/Cashflow.java` | `WAR_REPARATIONS` ledger stub | step 62 |
| `warbands/` (external plugin) | Battle engine / muster | step 60 |

**27 Java files** + `wargoals.yml` + external `warbands/`.

## Verify

- [x] `WarMapper` round-trips v2 `WarData` (v2-only; no v1 war JSON migration)
- [x] Unit tests: `WarGoalType` + `WarMapper` (`mvn test`)

## Status

**Done** (2026-08-19). **Next batch:** [56.03 — Goal validation](./03-goal-validation.md).
