# Step 61.03 — Battle pool resolver

**Done** (2026-08-21). **Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61.02 war commitment](./02-war-commitment.md) · [61.01b levy & vassal lock](./01b-levy-vassal-lock.md) · **Next:** [61.05 casualty ledger](./05-casualty-ledger.md)

## Goal

Given a campaign battle (`warId`, `provinceId`, side membership), compute **eligible committed regiment totals** per side using offense/defense mode and militia deployment rules from [61.01](./01-planning-lock.md). Levy rows from [61.01b](./01b-levy-vassal-lock.md) are summed by **holder** factions on that side.

## New component

Path: `simplefactions/.../War/battle/military/BattlePoolService.java`

| Method | Output |
|--------|--------|
| `resolvePoolMode(War war, int battleProvinceId, BelligerentRole side)` | `OFFENSIVE` or `DEFENSIVE` regiment filter for that belligerent side |
| `eligibleRegiments(War war, int battleProvinceId, Side belligerentSide, PoolMode mode)` | Map `factionId -> regimentId -> committed count` |
| `totalCommittedRegiments(...)` | Integer sum for lives formula |
| `isMilitiaEligible(Faction faction, int battleProvinceId)` | Own-land + vassal/overlord rules |

### Offense/defense mode

Use `CampaignProgressionService.getOffensiveSide(war)`:

- Side matching offensive role → filter `Regiment.isOffensive() == true` (+ levies per lock)  
- Other side → filter `!isOffensive()` for professional; militia allowed when eligible  

### Militia matrix (implement as unit tests)

| Battle province owner | Faction | Militia in pool? |
|-----------------------|---------|------------------|
| Faction A | A | Yes |
| Vassal V | V | Yes |
| Vassal V | Overlord O | **No** |
| Faction A | Unrelated ally | No (not own land) |

### Levy inclusion

Levies follow the **offensive** pool on the faction's war side (levy regiment is `offense: true` in `regiments.yml`). Sum frozen levy commitment rows where `holderFactionId` is a fighter on that side. Source attribution (`sourceFactionId`) is for casualty apply only (61.06), not pool double-counting.

Levy-only factions do not deploy militia in battle (they are not fighters). Militia rules apply only to fighter factions' own regiments.

## Consumers (later batches)

| Batch | Use |
|-------|-----|
| 61.04 | `totalCommittedRegiments` → collective lives |
| 61.06 | `eligibleRegiments` → casualty debit order by regiment type |

## Tests

New `BattlePoolServiceTest`:

- Invasion battle on defender border province — attacker offensive, defender defensive  
- Counter-push phase on attacker-owned province — pools swap  
- Nested vassal chain — levy counted once under nearest fighter holder (61.01b); no duplicate on main overlord  
- Vassal land battle — overlord militia excluded, vassal militia included  
- Ally contributor — only own-land militia for ally faction  

Mock: `TitleManager.getByProvince`, `WarManager.getCommitmentsForWar`, sample `War` + commitments from 61.02.

## Verification

- [x] `PoolMode` + `BattlePoolService` (`resolvePoolMode`, `isMilitiaEligible`, `eligibleRegiments`, `totalCommittedRegiments`)
- [x] `BattlePoolServiceTest` (invasion/counter-push, militia matrix, levy offensive-only, nested holder levy, total sum)
- [x] `WarCommitmentService.totalCommittedRegiments` stub comment points to `BattlePoolService`
- [x] `mvn test` passes

## Out of scope

- Mutating commitments (61.06)
- Siege vs field type (63)
