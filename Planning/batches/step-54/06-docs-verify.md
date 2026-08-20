# Step 54.06 — Docs verify

**Repos:** `simplefactions` · `ProvinceSystem`

Close step 54: authoritative SF docs, hub/STAGING updates, automated verify.

## Docs created

| File | Action |
|------|--------|
| [`Installations.md`](../../../../simplefactions/Documentation/Installations.md) | Authoritative SF installations spec |
| [`ProvinceGrid.md`](../../../../simplefactions/Documentation/ProvinceGrid.md) | Authoritative SF province grid spec |

## Hub docs updated

| File | Action |
|------|--------|
| [00-index.md](./00-index.md) | Step 54 **complete** |
| [03-roadmap.md](../../03-roadmap.md) | Step 54 done; next step 43 |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | M5b step-54 done |
| [01-current-state.md](../../01-current-state.md) | Step 54 shipped |
| [batches/README.md](../README.md) | step-54 row → done |
| [step-43/00-index.md](../step-43/00-index.md) | Unblocked |
| [STAGING.md](../../../STAGING.md) | Step 54 operator checklist |

## Automated verify

**SimpleFactions:**

```bash
cd simplefactions
mvn -q package -DskipTests
```

**ProvinceSystem backend:**

```bash
cd ProvinceSystem/backend/src
python -m unittest scripts.loader.test_markers -v
python -m unittest scripts.tools.test_build_province_id_grid -v
```

**Frontend:**

```bash
cd ProvinceSystem/frontend
npm test
npm run build
```

- [x] SF `mvn package -DskipTests` passes
- [x] PS marker loader tests pass
- [x] PS province grid build tests pass
- [x] Frontend `npm test` + `npm run build` pass

## STAGING operator checklist (summary)

See [STAGING.md](../../../STAGING.md) Step 54 section for full list.

### SF setup

- [ ] `Input/province_id_grid.bin.gz` present (copy from PS defines after grid rebuild)
- [ ] `port-sea-proximity-blocks` in config (default 20)
- [ ] Plugin fails loud if grid missing

### Gameplay

- [ ] `/faction claim` / `setcapital` resolve province locally (no webapp error)
- [ ] `/faction construct fort|port|airport <name>` on owned land
- [ ] Second same-kind same province rejected; port inland rejected
- [ ] Unclaim dissolves installation

### Map data

- [ ] `map_markers.json` includes `installations[]` after construct + regen
- [ ] `GET /main/data/markers` returns enriched `installations` with `map_x`/`map_y`

### Website

- [ ] `/map/main` shows fort/port/airport pins with labels
- [ ] Settlement markers unchanged

## Status

**Done** (2026-08-18).

## Next

[step-55](../step-55/00-index.md) (installation upkeep + construction + GUI), then [step-43](../step-43/00-index.md) (fort ZOC)
