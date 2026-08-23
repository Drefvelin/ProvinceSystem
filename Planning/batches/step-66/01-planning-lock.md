# Step 66.01 — War campaign map lock

**Plan + docs only.** Lock export contract, smoothing rules, visual spec, and batch boundaries before 66.02+ code.

**Repos:** `Workspace/simplefactions`, `ProvinceSystem` (backend + frontend)  
**Depends on:** [step 70.01](../step-70/01-planning-lock.md) (dual-leg schedules), [step 58.01](../step-58/01-planning-lock.md) (full campaign axis), [map-export-schema.json](../../assets/map-export-schema.json), [step 44.01](../step-44/01-planning-lock.md) (war map layer lock)  
**Authoritative gameplay:** [Wars.md](../../../../simplefactions/Documentation/Wars.md)

**Status:** **Done** (2026-08-23).

---

## Problem

Campaign wars are playable in-game (axis, dual schedules, route GUI) but **invisible on the web map**. Operators and players cannot see where the campaign line runs or where battles are scheduled without opening the in-game campaign view.

Step 68 originally bundled full `wars[]` export (occupation, chronicle, everything). That blocked a useful **route-only** slice until the entire war export was done. Step 66 ships the **minimum map visualization** needed to validate campaign geometry before raids and occupation tint.

---

## Locked — scope

| Area | Step 66 | Deferred |
|------|---------|----------|
| Smooth campaign line + battle pins + hover | Occupation tint (step 68 + PS [44](../step-44/00-index.md)) |
| `wars[]` route slice in `map_markers` | Chronicle `events[]` |
| Auto-show when active wars exist | War layer toggle polish (step 44 batch 04) |
| Campaign war types only | `raid` wars (step 67), inter-battle raids (step 71) |

**Rule:** Frontline/occupation overlay still **must not** infer from territory diffs alone when it ships in step 68. Step 66 does not render occupation at all.

---

## Locked — war filter

Export wars where:

- `WarManager.getActive()` includes the war
- `status == active`
- `war_type != raid` (`de_jure`, `subjugate`, `transfer_subject` only)

---

## Locked — JSON naming

**snake_case** throughout in `map_markers.json` (`campaign_battle_schedule`, not camelCase). Debug `/warstatus` JSON may remain camelCase; map export follows [map-export-schema.json](../../assets/map-export-schema.json).

---

## Locked — per-war export fields (route slice)

| Field | Source |
|-------|--------|
| `id`, `name`, `war_type`, `goal`, `status` | `War` |
| `attacker_leader_id`, `defender_leader_id`, `belligerents[]` | participants |
| `campaign_provinces[]`, `cursor_index`, `objective_province_id` | campaign axis |
| `push_target` | `CampaignPushTarget.toJson()` |
| `campaign_schedule_index`, `campaign_counter_schedule_index` | invasion / counter active indices |
| `campaign_battle_schedule[]`, `campaign_counter_schedule[]` | trimmed schedules at declare |
| `attacker_capital`, `defender_capital` | optional `{ province_id, center_x, center_z }` from faction capital settlements |

**Omit from step 66 export** (step 68): `occupied_by_*`, `initiative_*`, `last_battle_occupied`, chronicle fields, `started_at` / `ended_at` / `end_reason`.

PS enriches `map_x` / `map_y` on schedule slots and optional `campaign_line_points[]` from province centroids. When a waypoint province is a faction capital, prefer capital settlement `center_x` / `center_z` over centroid.

---

## Locked — schedule slot row

```json
{
  "schedule_index": 0,
  "leg": "invasion",
  "province_id": 452,
  "kind": "siege",
  "kind_label": "Siege",
  "battle_type": "SIEGE",
  "required": false,
  "status": "next",
  "fort_installation_id": "Greenfort",
  "port_installation_id": null
}
```

| Field | Source |
|-------|--------|
| `kind` | `CampaignBattleKind.toJson()` (`field`, `siege`, `naval`, `naval_invasion`) |
| `kind_label` | `CampaignUiCopy.formatBattleKind()` (player-facing hover text) |
| `battle_type` | `ScheduledCampaignBattle.battleType().name()` (`FIELD` / `SIEGE`) |
| `leg` | `invasion` \| `counter` |

### Slot `status` (computed at SF export time)

| Value | Rule |
|-------|------|
| `fought` | `schedule_index < activeIndexForLeg` |
| `next` | `schedule_index == activeIndexForLeg` **and** `leg == activeLeg(war)` |
| `upcoming` | otherwise |

Use `CampaignScheduleService.activeLeg(war)` - same logic as [`WarScheduleFeedbackFormatter`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/WarScheduleFeedbackFormatter.java) current-slot prefix.

**Legacy wars (no counter schedule):** export invasion schedule only; `next` highlight uses invasion leg when `push_target` is invasion-side (`toward_objective`, `retake_objective`).

Internal reference for schedule shape: [`WarDebugFormatter.serializeCampaignSchedule`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/WarDebugFormatter.java) (map export adds `leg`, `kind_label`, `status`, snake_case keys).

---

## Locked — line geometry

**Waypoints (ordered):** one map point per `campaign_provinces[]` entry:

1. PS resolves `map_x` / `map_y` from `province_id` via centroid enrichment.
2. When province is attacker or defender **faction capital**, prefer `attacker_capital` / `defender_capital` settlement `center_x` / `center_z`.

The axis from step 58 already spans attacker capital province through border to objective. Do **not** draw a straight chord between capitals. Do **not** render raw centroid polyline without smoothing.

**Smoothing (FE, batch 66.04):**

| Parameter | Value |
|-----------|-------|
| Algorithm | Catmull-Rom spline |
| Tension | `0.5` |
| Resample | ~12 points per inter-waypoint segment |
| SVG | Two stacked paths: border (solid, wider) under dash (dotted inner) |
| Border color | `#2a1810` |
| Dash color | `#8b3a3a` (distinct hue per war via stable hash of `war.id` when multiple wars) |
| Opacity | `0.85` on parchment |

**Visibility:** same map modes as settlement markers ([`isMarkerMapMode`](../../../../ProvinceSystem/frontend/app/lib/mapMarkers.ts) / `LABEL_MAP_MODES`).

---

## Locked — battle markers

| Rule | Choice |
|------|--------|
| Icon | `frontend/public/battle.png` (add in 66.05) |
| Placement | slot `map_x` / `map_y` after PS enrichment |
| Scale | ~75% of small settlement marker |
| Hover `title` | `{kind_label} - {province_name} - {status}` (plain hyphens) |
| `next` pin | 1.1x scale + optional ring at same coords |
| Z-order | Above political layer, below hovered settlement labels (`MapMarkerLayer`) |
| Province name | PS adds `province_name` on slot during enrichment (66.03) |

Reuse `MapMarker` with `kind: "battle"` where possible; merge war battle markers in [`MapViewer.tsx`](../../../../ProvinceSystem/frontend/app/components/MapViewer.tsx).

---

## Locked — API path

```text
SF Markers.export() → wars[]
  → RestServer upload map_markers
  → PS loader enriches map_x/map_y on slots + campaign_line_points
  → GET /{mapId}/data/map_markers → FE useMapMarkers (extend) + WarCampaignLineLayer
```

No new upload mode; extend existing `map_markers.json`.

---

## Locked — edge cases

| Case | Behavior |
|------|----------|
| No active wars | Omit `wars` key or empty array; FE hides war layer |
| Empty counter schedule | Counter pins omitted; line still full axis |
| Capital settlement missing coords | Fall back to province centroid |
| Sea-heavy axis | Smoothing follows centroid hops; no special sea curve in v1 |
| Pre-70 war JSON (no counter schedule) | Export invasion schedule only |
| Multiple wars on same map | Render all; hover picks topmost marker |
| Slot missing centroid | Omit pin; log warning; do not break payload |

---

## Locked — batches

| Batch | Delivers |
|-------|----------|
| 66.02 | `WarMapExporter` in SF; unit tests; hook in `Markers.export()` |
| 66.03 | PS loader centroid + `province_name` enrichment; API types |
| 66.04 | `WarCampaignLineLayer` SVG; Catmull-Rom util + tests |
| 66.05 | `battle.png`; battle markers; hover; active slot highlight |
| 66.06 | `Wars.md` map section; war-build-order; STAGING smoke checklist |

---

## Checklist

- [x] Schema updated with schedule legs + slot status fields ([map-export-schema.json](../../assets/map-export-schema.json))
- [x] Smoothing algorithm named (Catmull-Rom, tension 0.5, ~12 samples/segment)
- [x] Visual stroke spec locked (border `#2a1810` + dash `#8b3a3a`, opacity 0.85)
- [x] Step 71 created for displaced inter-battle raids
- [x] Step 68 index updated (occupation slice remains)
- [x] war-build-order.md updated

## Next

[66.02 SF wars export](./02-sf-wars-export.md)
