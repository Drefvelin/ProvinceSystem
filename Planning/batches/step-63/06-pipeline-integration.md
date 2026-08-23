# Step 63.06 — Pipeline integration

**Repo:** `simplefactions`  
**Depends on:** [63.03](./03-stalemate-peace.md), [63.04](./04-surrender-gui.md), [63.05](./05-battle-victory.md)

## Tasks

1. **Unify all end paths through `WarResolutionService`**
   - `CampaignPostBattleChoiceService.applyLoserAcceptPeace` → `WHITE_PEACE` via service
   - `CampaignChoiceService.acceptWhitePeaceAndEnd` → service
   - Remove direct `WarManager.endWar` from progression except service + admin command

2. **`openCampaignView`**
   - Replace `recalculateAndMaybeEnd` with `WhitePeaceService.recalculateProposals` only (flags update, no end).
   - Optional: lore line on info book when enemy proposed peace.

3. **`CampaignPostBattleChoiceService.afterChoiceResolved`**
   - Walkover → `evaluateAndMaybeEnd` with empty battle context.

4. **Admin / dev**
   - `WarScheduleAdminService` / `winbattle` paths: pass battle context into resolver.

5. **grep cleanup**
   - No references to `AUTO_WHITE_PEACE` or `SURRENDER`.

## Verify

Full `mvn test`. Manual E2E:

1. Declare → muster → fight → capital win → war ends with attacker message.
2. Hold → accept peace → white peace message.
3. Surrender → defender win message.
4. Both 0 offensive at next node during voting → white peace.
