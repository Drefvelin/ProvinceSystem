# Step 65.02 — Port sea ZOC & naval schedule slots

**Repos:** `Workspace/simplefactions`  
**Depends on:** [65.01 planning lock](./01-planning-lock.md), [64.03 schedule builder](../step-64/03-schedule-builder.md)  
**Touches:** new `PortSeaZocIndex`, `CampaignScheduleBuilder`, `ScheduledCampaignBattle`, `WarMapper`, `ConfigLoader`, `config.yml`

## Goal

At war declare, detect enemy **port-blocked** sea crossings on the campaign axis and insert **`NAVAL`** slots.

## Scope

### `PortSeaZocIndex`

Mirror `FortZocIndex` pattern:

```text
build(all operational ports) -> PortSeaZocIndex
portForSeaProvince(seaProvinceId) -> Optional<PortRef>
portsBlockingSeaRun(seaProvinceIds) -> List<PortRef>  // enemy-filtered at builder
```

- BFS sea coverage per port (`war.port_sea_zoc_radius`, default 2).
- Oldest port wins per sea province (`completedAt`, then `id`).
- Only `InstallationKind.PORT`, operational.

### `ScheduledCampaignBattle`

Add optional `portInstallationId` (record field + JSON round-trip).

### `CampaignScheduleBuilder`

During axis walk, when axis index is inside a **SEA** run:

1. Resolve sea province ids in the run (contiguous `Terrain.SEA` on axis).
2. Find enemy ports whose coverage intersects the run (relative to aggressor coalition at declare).
3. For each distinct blocking port not yet scheduled → insert `NAVAL` at **port province** with `portInstallationId`.

Dedupe: one `NAVAL` per `portInstallationId` on the schedule.

### Config

- `war.port_sea_zoc_radius` in `config.yml` + `Cache` / `ConfigLoader`.

## Tasks

1. Implement `PortSeaZocIndex` with unit tests (coverage radius, overlap resolution).
2. Extend slot model + mapper for `portInstallationId`.
3. Extend builder sea-run detection + naval insertion.
4. Unit tests: mocked axis with sea hop + enemy port → `NAVAL` slot present.
5. Integration: `WarCampaignServiceTest` declare across sea with port → schedule contains naval kind.

## Out of scope

- `NAVAL_INVASION` (65.03)
- Siege override on landing (65.04)
- `navalVariant` on launch (65.04)
- GUI (65.05)

## Done when

Declare on test map with blocked sea crossing populates `NAVAL` in `campaignBattleSchedule` with correct `portInstallationId`.
