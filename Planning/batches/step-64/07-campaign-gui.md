# Step 64.07 — Campaign GUI battle kinds

**Repos:** `Workspace/simplefactions`  
**Depends on:** [64.02 slot model](./02-slot-model.md), [64.05 trim](./05-trim-initiative.md)  
**Touches:** `CampaignRouteRenderer`, `CampaignCreator`, `CampaignView`, `CampaignUiCopy`, `WarDebugFormatter`, `WarScheduleAdminService`

## Goal

Campaign route GUI shows **what kind of battle** each scheduled province is.

## Scope

### Lore labels (player-facing, no em dashes)

| `CampaignBattleKind` | Lore |
|----------------------|------|
| `FIELD` | `Field Battle` |
| `SIEGE` | `Siege` |

Objective slot: `Field Battle` + existing objective / capital / target region lines + next-battle marker when applicable.

### Route rendering

- Build `Map<Integer, ScheduledCampaignBattle>` or list index by province from `war.getCampaignBattleSchedule()`.
- `CampaignRouteRenderer.buildRouteLore` appends battle kind for provinces on schedule.
- Optional: distinct item material or enchant glint per kind (FIELD vs SIEGE) on route row items in `CampaignCreator` / `CampaignView`.

### Admin / debug

- `warschedule` command output: slot index, province id, kind, required, fort id.
- `WarDebugFormatter` includes schedule summary.

## Tasks

1. `CampaignUiCopy` constants for battle kind lines.
2. Renderer + creator lore integration.
3. Tests in `CampaignRouteRendererTest` for siege vs field lore on scheduled provinces.

## Out of scope

- Naval / naval invasion icons (step 65)
- Map export battle markers (step 67)

## Done when

Opening campaign view on a declared war shows Field Battle / Siege on correct route provinces.
