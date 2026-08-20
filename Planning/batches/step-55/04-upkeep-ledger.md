# Step 55.04 — Upkeep and ledger

**Repo:** `simplefactions`  
**Status:** **done** (2026-08-19)

Rename ledger cashflow and implement pay-or-destroy daily upkeep.

## Ledger

1. Rename `Cashflow.FORTS` → `Cashflow.INSTALLATIONS` (display `#706964Installations`).
2. Update all `case FORTS:` in `Ledger.java` → `INSTALLATIONS`.
3. `getIncome(INSTALLATIONS)` on **main/base guild**:
   - Sum `-dailyUpkeep` for each operational installation on the faction.
   - Return negative total for ledger GUI expenses section.
4. **Do not** add `INSTALLATIONS` to `applySettlementFor` external delta if `newDay()` withdraws directly — ledger line is **display + net income preview** only; document in code comment to avoid double charge.

## Payment (`Faction.newDay()`)

1. After army upkeep block (or before — pick one, stay consistent), run installation pass:
2. Collect operational installations; sort by `dailyUpkeep` ascending, then `completedAt` ascending.
3. For each: if `getBank().getWealth() >= upkeep` → `withdraw(upkeep)`; else `installationHandler.dissolve(installation)` + leader message.
4. Under-construction entries: skip upkeep.

## Done when

- Ledger GUI shows `Installations: -Xd` when faction has forts
- Faction with 0 wealth loses cheapest installation on new day
- Multiple installations: cheapest removed first when broke

## Next

[05-installations-gui](./05-installations-gui.md)
