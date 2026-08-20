# Step 54.02 — PS province grid script

**Repo:** `ProvinceSystem`

## Goal

Admin script: `provinces.png` + `provinces.txt` → `defines/{map}/province_id_grid.bin.gz`.

See [01-planning-lock](./01-planning-lock.md) for binary format.

## Files

| File | Action |
|------|--------|
| `backend/src/scripts/province_id_grid.py` | `build_province_id_map`, serialize/deserialize, `lookup_at` |
| `backend/src/scripts/tools/build_province_id_grid.py` | Admin CLI |
| `backend/src/scripts/tools/test_build_province_id_grid.py` | Unit tests |
| `backend/src/scripts/mapgen/geometry_cache.py` | Uses `build_province_id_map` (no duplicate LUT) |
| `backend/src/defines/{map}/province_id_grid.bin.gz` | Output (run script to generate) |

## Run

```bash
cd ProvinceSystem/backend/src
python -m scripts.tools.build_province_id_grid --map main
```

Options: `--output PATH`, `--dry-run`.

**Not** hooked into regen — run manually when map geometry changes.

## Operator workflow

1. Run script for affected map(s)
2. Copy `defines/main/province_id_grid.bin.gz` → `plugins/SimpleFactions/Input/province_id_grid.bin.gz` (54.03)

## Verify

- [x] Script runs on `main` without error
- [x] Output at `defines/main/province_id_grid.bin.gz`
- [x] Dimensions 6400×6400
- [x] Grid lookup matches `find_province` at centroid samples
- [x] `python -m unittest scripts.tools.test_build_province_id_grid` passes

## Status

**Done** (2026-08-18). Main grid: 6400×6400, ~495 KB gzip.

## Next

[03-sf-province-grid](./03-sf-province-grid.md)
