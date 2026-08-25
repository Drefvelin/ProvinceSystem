# Step 76.03 — Installation radius config

**Depends on:** [76.01](./01-planning-lock.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Add per-kind berth **radius** and root **consent/timeout** keys to [`installations.yml`](../../../../simplefactions/src/main/resources/installations.yml). Expose via [`InstallationConfigLoader`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Loaders/InstallationConfigLoader.java) and add [`InstallationBounds`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/installation/InstallationBounds.java) for distance and province checks (used by 76.04+).

Authority: [01-planning-lock.md](./01-planning-lock.md#config-lock-installationsyml).

## Tasks

1. Root keys: `consent-proximity-blocks`, `transfer-request-timeout-seconds`
2. Per kind: required `radius: 80` (dev default)
3. `InstallationKindConfig.getRadius()`
4. Loader getters: `getRadius`, `getConsentProximityBlocks`, `getTransferRequestTimeoutSeconds`
5. `InstallationBounds`: `horizontalDistanceBlocks`, `formatDistance`, `isWithinRadius`, `isCorrectProvince`, `provinceAt`

## Config

| Key | Location | Rule |
|-----|----------|------|
| `consent-proximity-blocks` | root | `>= 0` |
| `transfer-request-timeout-seconds` | root | `> 0` |
| `radius` | per kind | `> 0`; horizontal XZ distance from `centerX`/`centerZ` |

## Bounds API

```java
InstallationBounds.horizontalDistanceBlocks(centerX, centerZ, location)
InstallationBounds.formatDistance(blocks)           // one decimal, Locale.US
InstallationBounds.isWithinRadius(installation, loc)
InstallationBounds.isCorrectProvince(installation, loc)
InstallationBounds.provinceAt(loc)                  // delegates to BattlePlacementValidator
```

Province check requires live `ProvinceGrid` at runtime; unit tests cover distance math only.

## Live server merge

Add to existing `plugins/SimpleFactions/installations.yml`:

```yaml
consent-proximity-blocks: 20
transfer-request-timeout-seconds: 60
```

Add `radius: 80` under each of `fort`, `port`, `airport`.

## Verify

```powershell
cd simplefactions; mvn test
```

Focus: `InstallationConfigLoaderTest`, `InstallationBoundsTest`, `LedgerNetIncomeTest`.

## Done when

- [x] Shipped `installations.yml` has root + per-kind `radius`
- [x] Loader exposes radius and root timeout/proximity getters
- [x] `InstallationBounds` provides distance + province helpers
- [x] Tests green; [00-index](./00-index.md) updated

## Out of scope

- `InstallationVehicleService` / `canRegister` (76.04)
- Transfer command or chat messages (76.05)
- Full `Installations.md` berth section (76.07)
