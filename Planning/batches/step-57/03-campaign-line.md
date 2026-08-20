# Step 57.03 — Campaign line + objective picker

**Step:** 57 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Persist campaign metadata on `War`, pick objective province per locked rules, and compute campaign polyline via `ProvincePathfinder`.

## Scope

- [x] `War` / `WarData` campaign fields (`objectiveProvinceId` as integer, `campaignStartProvinceId`, `campaignProvinces`, `cursorIndex`, `subjectFactionId`)
- [x] Province `centerX` / `centerZ` from `provinces.txt` for geometric center fallback
- [x] `ObjectiveProvincePicker` (capital > settlement > centroid)
- [x] `WarCampaignService.populateCampaign(War)` wires picker + pathfinder
- [x] `WarMapper`, `WarDebugFormatter` updated
- [x] Unit tests
- [x] Declare hook + persist at declare (57.04)

## Objective picker rules

| Goal | Province set | Target faction |
|------|--------------|----------------|
| `de_jure_annex` | `TitleManager.getProvinces(title)` | Title owner (defender) |
| `subjugate` | `TitleManager.getProvinces(defender)` | Defender |
| `transfer_subject` | `TitleManager.getProvinces(subject)` | Subject from `subjectFactionId` |

Pick order: capital in set → largest settlement (capital settlement beats non-capital; population tiebreak) → geometric centroid of set.

## Files

| File | Role |
|------|------|
| `War/War.java` | Campaign fields |
| `Database/WarData.java` | Gson DTO |
| `War/WarMapper.java` | Round-trip |
| `War/objective/ObjectiveProvincePicker.java` | Objective selection |
| `War/campaign/WarCampaignService.java` | Populate campaign on war |
| `Map/Provinces/Province.java` | `centerX`, `centerZ` |
| `Loaders/ProvinceLoader.java` | Parse coords from provinces file |

## Verify

- [x] `mvn test` - all tests pass
- [x] `ObjectiveProvincePickerTest` - capital, settlement, centroid
- [x] `WarCampaignServiceTest` - end-to-end route + fields
- [x] `WarMapperTest` / `WarPersistenceFileTest` / `WarDataRoundTripTest` - campaign JSON round-trip

## Status

**Done** (2026-08-20). **Next batch:** [57.04 integration](./04-integration.md) (TBD) - declare hook, persist, admin debug.
