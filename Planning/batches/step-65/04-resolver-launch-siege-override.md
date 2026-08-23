# Step 65.04 — Invasion siege override, resolver & launch

**Repos:** `Workspace/simplefactions`  
**Depends on:** [65.03 naval invasion](./03-naval-invasion-detection.md), [64.06 resolver](../step-64/06-resolver-launch.md)  
**Touches:** `CampaignScheduleBuilder`, `CampaignBattleLaunchService`, `CampaignBattleTypeResolver`, `BattleFactory`, tests

## Goal

Amphibious landing into **enemy fort ZOC** becomes a **siege**. Naval kinds launch as **field** battles with **`navalVariant`**.

## Scope

### Siege override (schedule build)

When a `NAVAL_INVASION` target province is inside fort F's ZOC and `fortControllers[F]` is enemy of aggressor at declare:

- **Do not** add `NAVAL_INVASION` at landing province.
- Ensure **`SIEGE`** at fort province with `fortInstallationId` (reuse 64 dedupe).

Apply in builder **before** or **instead of** invasion insertion (65.03 hook).

### Launch

In `CampaignBattleLaunchService.createCampaignBattle`:

```text
if slot.kind in (NAVAL, NAVAL_INVASION):
  battle.setNavalVariant(true)
```

`CampaignBattleTypeResolver` unchanged (non-SIEGE → FIELD).

Optional: stash `portInstallationId` on battle for staff reference (display only).

### Re-siege

No change to 64.06 dynamic insert; naval progression uses same schedule index rules.

## Tasks

1. Builder override: invasion province in enemy fort ZOC → siege slot.
2. Launch sets `navalVariant` from slot kind.
3. Tests: invasion + fort ZOC → schedule has siege, no invasion.
4. Tests: launch `NAVAL` / `NAVAL_INVASION` → field battle, `navalVariant == true`.
5. Extend `CampaignBattleLaunchServiceTest`.

## Out of scope

- Campaign GUI labels (65.05)
- Map export (65.06)

## Done when

Siege override and naval launch behavior covered by unit tests; existing 64 launch/siege tests still pass.
