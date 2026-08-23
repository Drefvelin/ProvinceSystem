# Step 63.04 — Surrender GUI

**Repo:** `simplefactions`  
**Depends on:** [63.02](./02-resolution-service.md)

## Tasks

1. **`CampaignCreator`**
   - `createSurrenderButton(war)` — red banner, slot PDC key `campaign_surrender`.

2. **`CampaignView`**
   - Slot **47**: show surrender for war leader when war active and no post-battle choice pending.
   - Slot **48**: accept white peace (unchanged eligibility).

3. **`InventoryManager` / confirm flow**
   - New confirm key `campaign_surrender`.
   - On confirm: `WarResolutionService.surrender(war, leader)` → `DEFENDER_VICTORY` or `ATTACKER_VICTORY`.

4. **Eligibility**
   - `FactionManager.getByLeader(player)` matches attacker or defender war leader id.

## Files

| File | Action |
|------|--------|
| `Managers/Inventory/CampaignCreator.java` | Button |
| `Managers/Inventory/CampaignView.java` | Layout + click |
| `War/resolution/WarResolutionService.java` | `surrender()` |
| `Documentation/Wars.md` | Leader interactions table (63.07 or here) |

## Tests

- Unit: surrender maps leader side → correct `WarEndReason`
- Manual: leader sees surrender + accept peace side by side
