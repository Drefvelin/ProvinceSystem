# Step 78.07 — Raid target filter

**Depends on:** [78.06](./06-battle-vehicle-eligibility.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Expose raid target allowlist from committed sets for **step 71** launch.

## Shipped

1. `RaidKind` — `NAVAL` / `AIR` / `FORT` mapped to `InstallationKind`
2. `RaidTargetCandidate` record for GUI consumption
3. `RaidTargetService.isValidTarget` and `listValidTargets`

## Tasks

1. ~~`RaidTargetService.isValidTarget(war, attackerFactionId, installationId, now)`~~ — done
2. ~~`listValidTargets(war, attackerFactionId, raidKind, now)` for GUI~~ — done
3. ~~Unit tests: uncommitted install rejected; committed OK; wrong kind rejected~~ — done

## Note

Step **71** wires launch UI and battle templates; this batch only provides the filter API.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=RaidTargetServiceTest"
cd simplefactions; mvn test
```
