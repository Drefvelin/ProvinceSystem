# Step 66.02 — SF wars export

**Repo:** `simplefactions`  
**Depends on:** [66.01 planning lock](./01-planning-lock.md)  
**Touches:** `Map/export/`, `War/`, tests

## Goal

Add `wars[]` to `map_markers.json` for each active campaign war, including axis, dual schedules, push target, and capital endpoints.

## Build

| File | Action |
|------|--------|
| `Map/export/WarMapExporter.java` | **New** - serialize active wars per 66.01 lock |
| `Map/export/Markers.java` | Call `WarMapExporter.addWars(root, WarManager.getActive())` |
| `War/schedule/ScheduledCampaignBattle.java` | Expose kind/type for export (if not already) |
| `Map/export/WarMapExporterTest.java` | **New** - fixture war → JSON shape |

### Export logic

For each active war where `warType != RAID`:

1. Copy identity + belligerents + `campaign_provinces`, `cursor_index`, `objective_province_id`.
2. Copy `push_target`, `campaign_schedule_index`, `campaign_counter_schedule_index`.
3. Serialize invasion + counter schedules as arrays of slot rows (`leg`, `schedule_index`, `province_id`, `kind`, `battle_type`, `required`, `status`).
4. Resolve `attacker_capital` / `defender_capital` block coords from faction capital settlements (`center_x`, `center_z`).
5. Compute per-slot `status` from active indices + `push_target` (66.01 table).

### Status helper

```text
fought    = index < legActiveIndex
next      = index == legActiveIndex AND leg is active for pushTarget
upcoming  = else
```

Active leg mapping matches `CampaignScheduleService.activeLeg(war)` from step 70.04.

## Verify

- [x] `Markers.export()` writes `wars` array when active campaign war exists.
- [x] No `wars` key (or empty) when no active wars.
- [x] Dual-leg war exports both schedules with correct `status` on border index.
- [x] Raid wars excluded.
- [x] `mvn test` green.

## Status

**Done** (2026-08-23).

## Next

[66.03 PS schema passthrough](./03-ps-schema-passthrough.md)
