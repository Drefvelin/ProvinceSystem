# Step 71.09 — Damage gating & repair embargo

**Depends on:** [71.07](./07-raid-battle-runtime.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-25)

## Goal

Protect installation structures unless vulnerable; apply 48h place/break embargo on **target** from fight start.

## Tasks

1. `InstallationVulnerabilityService.isVulnerable(installationId, now)`:
   - Active campaign raid source or target.
   - Active campaign battle in-play set (picks + siege fort) or staff battle targeting installation.
2. Listener(s): cancel vehicle/entity/block damage to installation-tied assets when not vulnerable.
3. Explosion/TNT protection within `installations.yml` `radius` when not vulnerable (mirror battle point protection pattern).
4. `InstallationRepairEmbargoService`:
   - On fight start: set `raidRepairLockUntil[targetId] = now + repair_lock_hours`.
   - `isEmbargoed(installationId, location)` — target province + radius.
   - Block place/break for non-staff.
5. Staff bypass via existing admin permission.
6. Unit tests: vulnerable during active raid only; embargo from start not end; repeat raid allowed.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=InstallationVulnerability*,InstallationRepairEmbargo*"
cd simplefactions; mvn test
```
