# Step 53.03 — Dev data fix

**Repos:** `simplefactions` · `ProvinceSystem`

## Lanbury (Lantan)

Trim settlement `provinces` from `[705, 704]` → `[705]`.

Faction `provinces` may still include **704** as owned land — only the **settlement** shrinks.

| File | Change |
|------|--------|
| `simplefactions/.../MapAPI/map_markers.json` | `provinces: [705]` |
| `simplefactions/.../MapAPI/nation.json` | `settlements[0].provinces: [705]` |
| `ProvinceSystem/backend/src/input/main/map_markers.json` | same |
| `ProvinceSystem/backend/src/input/main/nation.json` | same |
| `ProvinceSystem/backend/src/defines/main/nation.json` | same if present |

## Verify

```bash
curl http://localhost:8000/main/data/markers
```

Lanbury `provinces` is `[705]`; `map_x`/`map_y` unchanged.

## Status

**Done** (2026-08-18). All five fixture files verified; API `GET /main/data/markers` returns Lanbury `provinces: [705]`, `center_x`/`center_z` 1748/2739.

## Next

[04-docs-verify](./04-docs-verify.md)
