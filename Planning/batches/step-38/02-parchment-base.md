# Step 38.02 — Parchment base from `map.png`

**Repos:** `ProvinceSystem` backend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Read the plain Xaero background (`input/{map}/map.png`), generate `parchment_base.png`, wire into fullregen, and serve it as the visual map base.

## Plan

1. **Input validation** — Check `map.png` exists and matches `provinces.png` dimensions; clear warning in regen logs on failure.
2. **`parchmentgen.py`** — Implement grade pipeline from [01-planning-lock](./01-planning-lock.md): desaturate → warm tone → paper multiply → vignette → save PNG. **Never** overwrite `map.png`.
3. **Assets** — Add tileable `backend/src/assets/map/paper_texture.png` (neutral parchment grain; ~512×512; committed asset).
4. **`dirs.py`** — `parchment_image(map_name)` → `output/{map}/maps/parchment_base.png`.
5. **`regeneration.py`** — Call `create_parchment_base(map_name)` once per regen (after compile, before `create_map` loop) when `map.png` valid.
6. **`map_routes.py`** — `GET /{map}/map` serves parchment output when file exists; else existing `input/{map}/map.png`.

## Build

| File | Action |
|------|--------|
| `backend/src/scripts/mapgen/parchmentgen.py` | create — grade pipeline + `create_parchment_base()` |
| `backend/src/scripts/mapgen/parchmentgen.py` or `util/map_background_validate.py` | inline or helper — dimension / existence checks |
| `backend/src/scripts/util/dirs.py` | `parchment_image()` helper |
| `backend/src/scripts/util/regeneration.py` | hook parchment before map loop |
| `backend/src/api/map_routes.py` | prefer parchment in `get_base_map` |
| `backend/src/assets/map/paper_texture.png` | add texture asset |
| `Planning/06-local-development.md` | note `map.png` (Xaero export) + sample for `dev` |

## Operator workflow

1. In-game: export Xaero world map for the season world at the same scale/crop as `provinces.png`.
2. Place as `backend/src/input/{map}/map.png` (or mount in Docker volume) — **same file the site already uses**.
3. Run `fullregen` for that map.

Until regen runs, `/map` keeps serving raw `map.png` (no breakage).

## Verify

- [x] `map.png` + `provinces.png` same width/height or regen logs readable warning and skips parchment
- [x] `fullregen` writes `output/{map}/maps/parchment_base.png`
- [x] `GET /{map}/map` returns parchment bytes when output exists
- [x] Missing or mismatched `map.png` → warning only; regen continues; `/map` still serves raw `map.png`
- [x] `map.png` on disk unchanged after regen
- [ ] Spot-check: coastlines, rivers, and biome contrast still readable after grade (operator on staging)

## Status

**Done** (38.02 code). Operator spot-check on `/map/main` after next fullregen.

## Out of scope

Muted nation colours ([03-muted-political](./03-muted-political.md)); frontend opacity ([04-frontend-composite](./04-frontend-composite.md)).
