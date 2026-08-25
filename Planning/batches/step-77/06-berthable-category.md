# Step 77.06 — Berthable category helper

**Depends on:** [77.05](./05-fort-land-berths.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Expose battle-prep helpers so step 78+ can distinguish berthable categories (need installation pool) from non-berthable ones (e.g. `train`). No battle UI or enforcement in this batch.

Authority: [01-planning-lock.md](./01-planning-lock.md#battle-prep-contract-7706-documented-only).

## Tasks

1. `VehicleCategoryRules.isBerthableCategory(categoryId)`
2. `VehicleCategoryRules.isBerthableType(vehicleTypeId)`
3. Unit tests in `VehicleCategoryRulesTest`

## API

```java
boolean VehicleCategoryRules.isBerthableCategory(String categoryId)
// true iff any InstallationKind has getCategorySlotCapacity(kind, categoryId) > 0

boolean VehicleCategoryRules.isBerthableType(String vehicleTypeId)
// isBerthableCategory(getCategoryId(vehicleTypeId)); false when unknown type
```

## Shipped semantics

| Category | `isBerthableCategory` |
|----------|----------------------|
| `train` | false |
| `ships` | true |
| `aircraft` | true |
| `land_vehicles` | true |
| `static_emplacements` | true |
| unknown / null | false |

## Future rule (step 78+, not implemented here)

Personal vehicle battle-eligible iff `NOT isBerthableType(type)` OR berthed at a battle-selected installation.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=VehicleCategoryRulesTest"
cd simplefactions; mvn test
```

## Done when

- [x] `VehicleCategoryRules` helpers implemented
- [x] Tests cover all shipped categories + train/unknown/null
- [x] Full `mvn test` green
- [x] [00-index](./00-index.md) updated

## Out of scope

- Battle/raid logic (78+)
- `Installations.md` / `AGENTS.md` (77.07)
