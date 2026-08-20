# Step 57.02 — ProvincePathfinder

**Step:** 57 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Implement terrain-weighted campaign routing: Dijkstra on the province graph, three-pass fallback, border-first start, and sea-contact fallback.

## Scope

- [x] `War/pathfinder/` package (`PathfinderPass`, `PathfinderResult`, `ProvinceOwnerLookup`, `BelligerentTerritory`, `ProvincePathfinder`, `TitleManagerProvinceOwnerLookup`)
- [x] Config keys: `war.pathfinder.neutral_penalty`, `sea_pass_enabled`, `water_cost` (optional)
- [x] `ProvincePathfinderTest` synthetic graph cases
- [x] **No** `War` field changes, declare hook, or objective picker (57.03–57.04)

## Implementation notes

| Rule | Detail |
|------|--------|
| Terrain cost | `1.0 / Cache.getTradeCarry(terrain)`; optional `water_cost` override for WATER |
| Ocean on pass 2 | `Terrain.SEA` tiles are always traversable on sea pass (open ocean is not neutral country) |
| Land passes | `Terrain.SEA` blocked; use `terrain == Terrain.SEA`, not `Province.isSea()` |
| Border start | Min-cost attacker border province `B` to objective; sea-contact fallback when no land border |

## Files

| File | Role |
|------|------|
| `War/pathfinder/ProvincePathfinder.java` | Dijkstra + three-pass + `computeCampaignLine` |
| `War/pathfinder/BelligerentTerritory.java` | Belligerent sets, border/sea-contact helpers |
| `War/pathfinder/PathfinderPass.java` | Pass enum |
| `War/pathfinder/PathfinderResult.java` | Route result DTO |
| `War/pathfinder/ProvinceOwnerLookup.java` | Owner lookup interface |
| `War/pathfinder/TitleManagerProvinceOwnerLookup.java` | Production owner lookup |
| `src/test/.../ProvincePathfinderTest.java` | Unit tests |

## Verify

- [x] `mvn test` - all tests pass (36 total including 7 pathfinder tests)
- [x] River crossing prefers WATER over mountain detour
- [x] SEA blocked on land pass; pass 2 routes through ocean
- [x] Neutral blocked pass 1; pass 3 with penalty
- [x] Border start picks cheapest invasion corridor
- [x] Sea-contact fallback when no land border

## Status

**Done** (2026-08-20). **Next batch:** 57.03 — campaign fields on `War` + `ObjectiveProvincePicker`.
