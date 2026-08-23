# Step 61.07 — Docs verify & staging

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61.06 casualty apply](./06-casualty-apply.md) · **Next:** [62 war end & goals](../step-62/00-index.md)

## Goal

Full test pass, Wars.md alignment, and manual staging checklist for step **61**.

## Docs

| File | Action |
|------|--------|
| [Wars.md](../../../../simplefactions/Documentation/Wars.md) | Mark 61 shipped; document config keys, commitment debug, lives formula reference |
| [00-index](./00-index.md) | Mark 61.02–61.07 done |
| [war-build-order.md](../../war-build-order.md) | Update step 61 status row |

## Test gate

```bash
cd simplefactions && mvn test
```

Expected new/extended suites:

- `WarCommitmentTest`
- `BattlePoolServiceTest`
- `BattleLivesServiceTest`
- `BattleCasualtyLedgerTest`
- `BattleCasualtyServiceTest`
- `CampaignBattleOutcomeServiceTest`
- `WarDebugFormatterTest`
- `WarDataRoundTripTest`

## Manual staging checklist

Run on staging server after deploy:

1. **Declare war** — `/faction warstatus <id>` shows non-zero `commitmentRows` (militia/professional/levy) per faction  
2. **Ally accepts CTA** — ally faction gains commitment rows  
3. **Schedule campaign battle** on defender border — at start, boss bar lives reflect `5 × regiments - players` (not template 25)  
4. **Fight with deaths** — side lives drop; ledger increments  
5. **Battle ends** — commitment counts decrease; faction military GUI shows slot loss; war returns to `VOTING`  
6. **Vassal province battle** — overlord militia not in pool; vassal militia present  
7. **Counter-push battle** on attacker land — offense/defense pools swapped vs invasion  
8. **Staff `/battle create`** — template lives unchanged; no commitment apply  
9. **No winner** (double wipe) — casualties still apply; vote reopens  

## Done when

- [x] All 61.02–61.06 code merged  
- [ ] Checklist passed on staging server (manual)  
- [x] `mvn test` green  
- [x] Index + Wars.md updated  

**Done** (2026-08-21). **Next batch:** [62 war end & goals](../step-62/00-index.md).
