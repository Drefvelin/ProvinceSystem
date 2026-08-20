# Step 43.03 — PS zocgen

**Repo:** `ProvinceSystem`  
**Depends on:** [01-planning-lock](./01-planning-lock.md) · [02-sf-forts-export](./02-sf-forts-export.md)  
**Unlocks:** [04-frontend-zoc-hover](./04-frontend-zoc-hover.md)

## Goal

Generate per-fort ZOC hatch PNGs from SF-exported `forts[].zoc_provinces`, serve them statically, and enrich `GET /{map}/data/markers` with `overlay`, `zoc_url`, and `map_x`/`map_y`.

## Deliverables

| Item | Path / behavior |
|------|-----------------|
| Hatch tile | `backend/src/assets/map/zoc_hatch.png` (16×16 diagonal BL→TR) |
| Generator | `backend/src/scripts/mapgen/zocgen.py` — `generate_zoc_overlays()` |
| Output PNGs | `output/{map}/zoc/{fort_id}.png` |
| Sidecar | `defines/{map}/zoc_overlays.json` — bbox per fort |
| Static route | `GET /{map}/zoc/{fort_id}.png` in `file_routes.py` |
| Markers enrich | `forts[]` in `build_markers_response()` |
| Triggers | `map_markers` upload + end of `fullregen` |
| Tests | `test_zocgen.py`, `test_markers.py` fort cases |

## Verification

- [x] `python -m unittest discover -s backend/src/scripts/mapgen -p test_zocgen.py`
- [x] `python -m unittest discover -s backend/src/scripts/loader -p test_markers.py`
- [ ] Upload `map_markers.json` with `forts[]` → PNGs appear under `output/main/zoc/`
- [ ] `GET /main/data/markers` returns `forts[].overlay` + `zoc_url`
- [ ] `GET /main/zoc/{id}.png` serves hatch overlay

## Status

**Done** (2026-08-19).
