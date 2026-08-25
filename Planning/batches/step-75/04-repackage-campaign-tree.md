# Step 75.04 — Campaign tree consolidation

**Depends on:** [75.02](./02-repackage-schedule.md)  
**Status:** **done** (2026-08-24)

## Scope

1. Move `War/progression/*` → `War/campaign/progression/*`.
2. Fold single-file packages into neighbors (no behavior change).
3. Move `War` root domain types → `War/core/*` (**required**, locked in [75.01](./01-planning-lock.md)).

## Steps

### Progression move

1. Move all 19 files from `War/progression` to `War/campaign/progression`.
2. Update imports in:
   - `WarManager`, campaign GUI inventors/views
   - `War/campaign/WarCampaignService`
   - `War/battle/campaign/CampaignBattleOutcomeService` and related
   - Tests under `War/progression` → move test package to `War/campaign/progression` (test mirror rule)

3. Delete empty `War/progression`.

### One-file package cleanup

| From | To |
|------|-----|
| `War/battle/naming/BattleNamingService` | `War/battle/campaign/` |
| `War/battle/util/BattlePermissions` | `War/battle/ui/` |
| `War/objective/ObjectiveProvincePicker` | `War/campaign/` |

Delete empty `War/battle/naming`, `War/battle/util`, and `War/objective` after moves.

### `War/core` (required)

Move from `War/` root into `War/core/`:

- `War.java`, `Side.java`, `Participant.java`, `WarGoal.java`, `WarCommitment.java`
- `WarMapper.java`, `WarDeclareHelper.java`, `WarCommandHelper.java`, `WarDebugFormatter.java`

Update imports across `Managers/`, `Database/`, tests, and map export. No types remain at `War/` root except subpackage directories.

### Validation package

Move `War/validation/*` → `War/declare/` (aligns with `WarDeclareHelper`).

## Verify

```bash
cd simplefactions && mvn test -Dtest="me.Plugins.SimpleFactions.War.**"
```

Manual: campaign GUI and declare flow still open (no compile errors in `Managers/Inventory/CampaignView`).

## Done when

- [x] `War/progression` deleted
- [x] `War/core` populated; no domain `.java` files at `War/` root
- [x] `BattleNamingService` lives under `War/battle/campaign`
- [x] No single-file packages under `War/battle/` except `events/`
- [x] War tests green
