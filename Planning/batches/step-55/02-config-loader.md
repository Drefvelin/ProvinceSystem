# Step 55.02 — Config loader

**Repo:** `simplefactions`

Load per-kind `daily-upkeep` and `construction-time` from `config.yml` under `installations:`.

## Tasks

1. Extend installation config loading (new `InstallationKindConfig` or extend existing loader) with:
   - `getDailyUpkeep(InstallationKind kind)`
   - `getConstructionTimeSeconds(InstallationKind kind)`
2. Defaults if missing: fail loud on enable or use documented defaults (lock: values in [01-planning-lock](./01-planning-lock.md)).
3. Ship dev `config.yml` with `construction-time: 10` and production comments (`# 432000`, etc.).
4. Unit or smoke: loader reads all three kinds.

## Files (expected)

| File | Action |
|------|--------|
| `src/main/resources/config.yml` | Add upkeep + construction-time |
| `Cache` / new loader class | Read installation economics |
| `SimpleFactions` `loadConfigs()` | Wire loader |

## Done when

- `InstallationKind.FORT` → upkeep 50, construction 10 (dev config)
- Slot keys from step 54 still load unchanged

## Status

**Done** (2026-08-19). Verified: `mvn -q package -DskipTests`.

## Next

[03-construction-queue](./03-construction-queue.md)
