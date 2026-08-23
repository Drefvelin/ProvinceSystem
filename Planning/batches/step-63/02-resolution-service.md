# Step 63.02 — Resolution service & end reasons

**Repo:** `simplefactions`

## Tasks

1. **`WarEndReason`**
   - Remove `AUTO_WHITE_PEACE` and `SURRENDER`.
   - Add `ATTACKER_VICTORY`, `DEFENDER_VICTORY`.
   - `fromJson` / `toJson`: only current reason ids (no aliases).

2. **`WarResolutionService`**
   - `evaluateAndMaybeEnd(War war, ResolutionContext context)` → `Optional<WarEndReason>`
   - `ResolutionContext` optional fields: `battleProvinceId`, `battleWinnerCoalition`, `battleResolved` flag
   - Delegates victory checks (63.05), stalemate (63.03), then `WhitePeaceService.recalculateProposals`
   - On non-empty: `WarManager.endWar(war, reason)`

3. **`WarManager.notifyWarEnded`**
   - Switch on `ATTACKER_VICTORY` / `DEFENDER_VICTORY` / `WHITE_PEACE` messages per lock.

4. **`CampaignChoiceService`**
   - `recalculateAndMaybeEnd` → delegate to `WarResolutionService` with empty context.

5. **Tests / callers**
   - Replace every `AUTO_WHITE_PEACE` and `SURRENDER` reference in tests and production code.

## Files (expected)

| File | Action |
|------|--------|
| `War/enums/WarEndReason.java` | Enum cleanup |
| `War/resolution/WarResolutionService.java` | New |
| `War/resolution/ResolutionContext.java` | New |
| `Managers/WarManager.java` | Messages |
| `War/progression/CampaignChoiceService.java` | Delegate |
| `War/progression/WhitePeaceService.java` | Return `WHITE_PEACE` only |

## Tests

- `WarEndReasonTest` — json round-trip for current values only
- `WarResolutionServiceTest` — stub coalition checks; mutual flags → `WHITE_PEACE`

## Verify

`mvn test` green.
