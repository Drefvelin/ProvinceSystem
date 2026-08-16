# Step 50.03 — Seed live input on main

**Repos:** `ProvinceSystem`  
**Depends on:** [02-promote-dev-world](./02-promote-dev-world.md)

## Goal

Put **runtime** faction/guild/settlement data on `input/main` from what SF already uploaded to **live PS `dev`**.

SF **`map-reference` stays `dev`** — do not change SF config for this batch.

## Source (used for 50.03)

Copied from [`Workspace/simplefactions/src/main/resources/MapAPI/`](../../../../Workspace/simplefactions/src/main/resources/MapAPI/) (user-confirmed snapshot matching live SF uploads to PS `dev`).

## Source (alternate)

Manual copy from **live ProvinceSystem server** `input/dev/*.json` if MapAPI is stale.

## `map_id` in map_markers.json

SF exports `"map_id": "dev"` while `map-reference` is `dev`. When placing files in `input/main`:

- **Optional:** set `"map_id": "main"` for local `GET /main/data/markers` consistency ([`markers.py`](../../../backend/src/scripts/loader/markers.py) passes through file value)
- **Do not** change SF `map-reference` or server config in this batch

## Do not

- Change SF `config.yml` `map-reference`
- Run `fullregen` before JSON is in place (50.04)

## Verify

- [x] Province ids in `nation.json` exist in `defines/main/provinces.txt` (705, 704)
- [x] `map_markers.json` — Lanbury `province_id: 705`; `map_id: main`
- [x] Faction **Lantan** (S5), not Calavorn Machinarium
- [x] Markers loader smoke: `ok 1 settlements`

## Status

**Done** (2026-08-16). Source: SF MapAPI → `input/main/`.

## Next

[04-regen-main](./04-regen-main.md).
