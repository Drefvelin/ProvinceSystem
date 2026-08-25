# Step 75.02 — Repackage `War/schedule`

**Depends on:** [75.01](./01-planning-lock.md)  
**Status:** **done** (2026-08-24)

## Scope

Move all types from `me.Plugins.SimpleFactions.War.schedule` into `me.Plugins.SimpleFactions.War.campaign.*` per the migration map. **No logic edits.**

## Steps

1. Create packages:
   - `War/campaign/schedule`
   - `War/campaign/zoc`
   - `War/campaign/runtime`
   - `War/campaign/vote`
   - `War/campaign/admin`
   - `War/campaign/ui`

2. IDE **Move class** (not copy/paste) for each file in [01-planning-lock.md](./01-planning-lock.md#migration-map--warschedule--warcampaign).

3. Update imports in:
   - `War/campaign/WarCampaignService.java`
   - `War/progression/CampaignRouteRenderer.java` (until 75.04)
   - `Managers/WarManager.java`, `Managers/Inventory/*War*`, `Managers/Inventory/Campaign*`
   - `War/battle/campaign/*`
   - All `src/test/java/.../War/**` touching schedule types
   - `Database/*` if any reference schedule types (unlikely)

4. Delete empty `War/schedule` directory.

5. Grep cleanup:
   ```text
   War.schedule
   import me.Plugins.SimpleFactions.War.schedule
   ```

## Verify

```bash
cd simplefactions && mvn test -Dtest="me.Plugins.SimpleFactions.War.**"
```

Spot-check compile of classes that only import schedule from outside War:

```bash
cd simplefactions && mvn -q compile
```

## Done when

- [x] `War/schedule` does not exist
- [x] Each new subpackage has ≤12 files
- [x] War tests green
- [x] No gameplay or JSON field changes
