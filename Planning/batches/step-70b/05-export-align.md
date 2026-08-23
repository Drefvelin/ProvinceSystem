# Step 70b.05 — Export & map align

**Repos:** SF (+ PS FE if needed)  
**Depends on:** [70b.04](./04-battle-display-names.md)  
**Touches:** `WarMapExporter`, `WarMapper`, `warBattleMarkers.ts` (optional), `markers.py` (optional)

## Goal

Exported war JSON matches in-game schedule; map markers work for multi-slot same province.

## Tasks

### 1. Always export counter schedule

`WarMapExporter.exportWar`:

- Emit `campaign_counter_schedule` whenever counter natural list is non-empty at export time (already conditional on non-empty; verify Brume war includes it after regen)
- Add regression in `WarMapExporterTest`: Brume-shaped war with counter slots → JSON has counter array length ≥ 2

### 2. Optional `display_name` on slots

Extend `exportSlot` with:

```json
"display_name": "Siege of Greenfort"
```

Computed via same ordinal helper as GUI (70b.04). FE can use for tooltips without re-deriving.

Update `map-export-schema.json` `$defs/war_schedule_slot` if present.

### 3. Map FE dedupe fix (if batching PS work here)

`warBattleMarkers.ts` currently dedupes by province + coords → siege + field at 705 collapses to one pin.

- Dedupe key: `leg + schedule_index` or allow multiple markers per province with vertical offset
- Prefer minimal fix: one marker per slot

Defer to separate commit if user wants SF-only 70b server test first; document in 70b.06 checklist.

### 4. Siege coords (known 66 bug)

`markers.py` `enrich_war_schedule_slots`: resolve siege/port coords from `fort_installation_id` / installation index, not province centroid only.

Include in 70b if quick; else track as 66.07 follow-up with note in verify checklist.

## Done when

- [x] `map_markers.json` wars[] for Brume includes `campaign_counter_schedule` with wilderness province ids
- [x] Invasion schedule slots match GUI order and count
- [x] `WarMapExporterTest` + PS marker tests updated if schema changes
