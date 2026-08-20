# Step 53.04 — Docs verify

**Repo:** `simplefactions`

## Files

| File | Action |
|------|--------|
| `Documentation/Settlements.md` | Rewrite for one-province model |

## Smoke checklist

- [x] `mvn package -DskipTests` passes in `simplefactions`
- [x] First faction capital: `/faction setcapital <name>` founds one-province city (code: `SettlementHandler.found()`)
- [x] Second city in adjacent province: requires new name (code: `resolveCapital()` + `requiresFoundingName()`)
- [x] Claim does not add provinces to settlement (code: `ProvinceHandler.addProvince()` — no settlement hook)
- [x] `map_markers` export shows single `provinces` entry per settlement (`Markers.java` + fixture)
- [x] PS markers API returns Lanbury with `provinces: [705]`

## Status

**Done** (2026-08-18). `Settlements.md` matches 53.01 lock; compile clean; smoke verified via code paths, fixtures, and `GET /main/data/markers`.
