# Step 71.11 — Docs & verify

**Depends on:** [71.10](./10-intruder-province.md)  
**Repo:** `simplefactions` + planning  
**Status:** done

## Goal

Document campaign raid rules; amend step 78 docs where raid targeting changed; full test suite green.

## Tasks

1. [`Wars.md`](../../../../simplefactions/Documentation/Wars.md):
   - New **Campaign raids (step 71)** section: timeline, launch, muster, fight rules, quotas, warband lock.
   - Update inter-battle raids references; distinguish from pillage war (67).
   - Fix raid battle mode table: campaign raid = timer, no capture; staff raid unchanged.
2. [`Installations.md`](../../../../simplefactions/Documentation/Installations.md): vulnerability gating, repair embargo.
3. [`AGENTS.md`](../../../../simplefactions/AGENTS.md): service/GUI rows for campaign raid packages.
4. Amend [78.01](../step-78/01-planning-lock.md) / [78.07](../step-78/07-raid-target-filter.md) notes: committed picks **not** campaign raid target filter.
5. [00-index.md](./00-index.md) and [war-build-order.md](../../war-build-order.md): mark 71 **done** when complete.
6. `mvn test` green; no em dashes in new player-facing strings.

## Test audit

| Area | Test class |
|------|------------|
| State / quota | `CampaignRaidServiceTest` |
| Eligibility | `CampaignRaidEligibilityServiceTest` |
| Muster join | `CampaignRaidJoin*Test` |
| Warbands | `CampaignRaidWarband*Test` |
| Battle runtime | `CampaignRaidLaunch*Test` |
| Signup lock | `CampaignWarbandSignup*Test` (extended) |
| Damage / embargo | `InstallationVulnerability*Test`, `InstallationRepairEmbargo*Test` |
| Intruder | `CampaignRaidIntruder*Test` |

## Verify

```powershell
cd simplefactions; mvn test
```

## Done when

- [x] Player docs describe campaign raid rules accurately
- [x] Step 78 raid-target docs clarified
- [x] `AGENTS.md` lists campaign raid services
- [x] Step 71 marked done in index + war-build-order
- [x] `mvn test` green
