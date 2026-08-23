# Step 63.03 — Stalemate & white peace

**Repo:** `simplefactions`  
**Depends on:** [63.02](./02-resolution-service.md)

## Tasks

1. **`CampaignCapabilityService`**
   - Add `canMountOffensive(war, coalition, provinceId)` — fuel + offensive regiments only (no initiative check).

2. **`WarResolutionService`**
   - `isOffensiveStalemate(war)`: next battle present, neither coalition `canMountOffensive` at that province, no choice pending.
   - Return `WHITE_PEACE` before proposal recalc.

3. **`WhitePeaceService`**
   - `recalculateProposals` returns `Optional<WarEndReason>` with **`WHITE_PEACE`** only (not `AUTO_WHITE_PEACE`).
   - `shouldAutoEnd` unchanged logic (both flags).

4. **Walkover dead-end**
   - `CampaignMilitaryWalkoverService` both `!canDefend` → keep `WHITE_PEACE` (already).

## Files

| File | Action |
|------|--------|
| `War/progression/CampaignCapabilityService.java` | `canMountOffensive` |
| `War/resolution/WarResolutionService.java` | Stalemate branch |
| `War/progression/WhitePeaceService.java` | Single peace reason |
| Tests | Update `WhitePeaceServiceTest`, add stalemate cases |

## Verify

Stalemate fixture: both coalitions 0 offensive regs at green node → peace. Fresh declare with unmustered armies does **not** peace (next battle hidden until mustered — optional: only stalemate when vote phase open).

**Lock decision:** Run stalemate only when `battleSchedulePhase == VOTING` or `SCHEDULED` (war is actively scheduling), not on brand-new declare before first vote day. Document in test.
