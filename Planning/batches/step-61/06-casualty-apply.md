# Step 61.06 — Regiment casualty apply

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61.05 casualty ledger](./05-casualty-ledger.md) · **Next:** [61.07 docs verify](./07-docs-verify.md)

## Goal

After a **campaign** battle ends, convert ledger casualties into `WarCommitment` and faction military slot reductions, then continue 60.09 progression/voting flow.

## New component

Path: `simplefactions/.../War/battle/military/BattleCasualtyService.java`

| Method | Purpose |
|--------|---------|
| `applyBattleCasualties(War war, Battle battle, Map<String, Integer> sideCasualties)` | Main entry |
| `debitFaction(Faction, regiment breakdown, int casualties)` | Militia-first then proportional army/levy |
| `persistCommitments(War war)` | Update in-memory + DB when ready |

### Apply order (per side)

1. Load eligible pool from `BattlePoolService` (61.03)  
2. For each faction contributor on that side:  
   - Debit **militia** commitment first (if eligible at battle province)  
   - Debit remaining casualties **proportionally** across army + levy committed counts  
3. Mirror debits to `Regiment.currentSlots` / levy sent counts  

Run for **both** sides. Run when **no winner** (casualties still apply).

## Outcome hook

Update [`CampaignBattleOutcomeService`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleOutcomeService.java):

```text
load ledger → applyBattleCasualties (if campaign field/siege)
→ existing progression / occupation (if winner)
→ openVote → delete battle → persist war
```

Skip when:

- `warId == null`  
- `BattleType.RAID` (66 may extend later)  

## Persistence

| Data | 61.06 target |
|------|--------------|
| `WarCommitment` rows | Persist in war save payload or sidecar table |
| Faction military | Existing faction DB save path after slot decrement |

If war reload loses commitments today, add minimal JSON blob on `WarData` for commitments (align with 56.04 persistence style).

## Player feedback

Broadcast summary to war participants (optional v1):

```text
Campaign battle losses: attacker N, defender M regiments.
```

No em dash in message strings.

## Tests

`BattleCasualtyServiceTest`:

| Test | Assert |
|------|--------|
| `militiaDebitedFirst_onOwnLand` | Militia commitment hits zero before professional |
| `proportionalAcrossContributors` | Two factions same side split fairly |
| `overlordMilitiaNotDebited_inVassalLand` | Overlord militia count unchanged |
| `noWinnerStillApplies` | Commitments decrease both sides |
| `skipsManualBattle` | No-op when warId null |

Extend `CampaignBattleOutcomeServiceTest` — casualties invoked before `openVote`.

## Out of scope

- Goal apply (62)
- Rebuilding regiments / economy

## Verification (61.06)

- [x] `BattleCasualtyService` + militia-first proportional apply
- [x] `BattleEndedEvent` snapshots ledger before `battle.end()`
- [x] `CampaignBattleOutcomeService` hook before progression/`openVote`
- [x] `WarData.commitments` persistence via `WarMapper`
- [x] `BattleCasualtyServiceTest` + outcome/round-trip tests
- [x] Full `mvn test` green

**Done when:** this file + [00-index](./00-index.md) + [Wars.md](../../../../simplefactions/Documentation/Wars.md) aligned.

**Done** (2026-08-21). **Next batch:** [61.07 docs verify](./07-docs-verify.md).
