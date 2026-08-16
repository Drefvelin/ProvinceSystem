# Step 42.10 — Docs verify + STAGING

**Repos:** Planning + `ProvinceSystem` + `Workspace/simplefactions`  
**Depends on:** [02](./02-sf-settlement-core.md)–[09](./09-frontend-markers.md)

## Goal

Close step 42 in hub docs and STAGING; operator checklist for settlements on staging deploy (including TFMCWeb gateway + marker sizes).

## Docs updated

| File | Action |
|------|--------|
| [step-42/00-index.md](./00-index.md) | All batches **done** |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | M5 settlements done; next → step 43 |
| [16-map-platform.md](../../16-map-platform.md) | Req 8 done; SF via TFMCWeb note |
| [13-tfmcweb.md](../../13-tfmcweb.md) | SimpleFactions listed as gateway consumer |
| [01-current-state.md](../../01-current-state.md) | Settlements shipped |
| [03-roadmap.md](../../03-roadmap.md) | Track H step 42 done |
| [batches/README.md](../README.md) | step-42 row → done |
| [12-end-to-end-flows.md](../../12-end-to-end-flows.md) | SF uploads via TFMCWeb |
| [STAGING.md](../../../STAGING.md) | Step 42 operator checklist |
| [Settlements.md](../../../../Workspace/simplefactions/Documentation/Settlements.md) | Mark **implemented** sections |

## Automated verify

**Backend:**

```bash
cd ProvinceSystem/backend
python -m unittest discover -s src/scripts/loader -p "test_markers.py" -v
python -m unittest src.api.test_map_access -v
```

**Frontend:**

```bash
cd ProvinceSystem/frontend
npm test
npm run build
```

**SF:** manual dev-server checklist from batches 42.03–42.08.

## STAGING operator checklist (summary)

### SF + LP + TFMCWeb

- [ ] TFMCWeb `api.base-url` / `api.plugin-key` configured
- [ ] SimpleFactions `softdepend` TFMCWeb; map uploads use gateway (no SF API URL)
- [ ] `settlement-found-distance` in SF config (default 2)
- [ ] `settlement-large-population-threshold` in SF config (default 8)

### Gameplay

- [ ] Faction can found city with `/faction setcapital "Name"`
- [ ] Guild can found/join per distance rules
- [ ] City with 9+ guild capitals exports `marker_size: large`

### Map data

- [ ] `map_markers.json` uploaded on regen (via gateway)
- [ ] `GET /main/data/markers` returns settlements with `map_x`/`map_y`, `population`, `marker_size`

### Website

- [ ] Zoomed out: no settlement markers visible
- [ ] Zoomed in: correct pin per `marker_size` and `kind` (`settlement_*` vs `capital_settlement_*`)
- [ ] Straight black settlement name under each pin (no arc)
- [ ] Anonymous `/map/main` unchanged for access; staff map unchanged from step 41

### Regression

- [ ] Nation labels, pan/zoom, modals still work
- [ ] Lose centre province → city removed from map after regen

## Status

**Done** (2026-08-15). Hub docs, STAGING checklist, automated verify.

## Next

[step-43 forts](../step-43/00-index.md).
