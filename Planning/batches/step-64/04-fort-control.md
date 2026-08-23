# Step 64.04 — War-time fort control

**Repos:** `Workspace/simplefactions`  
**Depends on:** [64.03 schedule builder](./03-schedule-builder.md)  
**Touches:** `War.java`, `WarMapper`, new `FortControlService`, siege outcome path (stub hook for 64.06)

## Goal

Track which coalition **controls each fort's ZOC** during the war. Initialize at declare; update when a siege is won.

## Scope

### `fortControllers: Map<String, CampaignCoalition>`

- Key: installation id (fort)
- Value: `AGGRESSOR` or `DEFENDER` coalition

### `FortControlService`

```text
initializeAtDeclare(war):
  for each operational fort on defender territory (or all forts in schedule ZOC set):
    fortControllers[fortId] = owning faction's coalition

controller(war, fortInstallationId) -> CampaignCoalition

setController(war, fortInstallationId, winnerCoalition)

isEnemyControlled(war, fortInstallationId, advancingCoalition) -> boolean
```

### Schedule builder integration

- 64.03 siege insertion at declare: enemy = defender coalition for all forts initially.
- **Live progression (64.06):** when resolving whether next node needs siege, consult current `fortControllers`, not static declare-time ownership.

### Persistence

- `fortControllers` on `War` JSON

## Tasks

1. Add map field + mapper.
2. `initializeAtDeclare` called from `WarCampaignService` after axis + schedule build.
3. Unit tests: init assigns defender; `setController` flips; enemy check symmetric.

## Deferred to 64.06

- Call `setController` from siege battle outcome handler.

## Done when

Fort controllers persist and schedule builder / tests use them for siege eligibility.
