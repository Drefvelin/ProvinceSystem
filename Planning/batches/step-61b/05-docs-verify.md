# Step 61b.05 — Docs verify & solo staging

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61b.04 campaign join rules](./04-campaign-join-rules.md) · **Next:** [62 war end & goals](../step-62/00-index.md)

## Goal

Test gate, DEV-SHORTCUTS entry, Wars.md note, and solo attacker staging checklist.

## Docs

| File | Action |
|------|--------|
| [DEV-SHORTCUTS.md](../../DEV-SHORTCUTS.md) | Step 61b section shipped + solo workflow |
| [Wars.md](../../../../simplefactions/Documentation/Wars.md) | Battle devmode + capture config under in-battle rules |
| [00-index](./00-index.md) | Mark 61b batches done |
| [war-build-order.md](../../war-build-order.md) | 61b status done |
| [61 00-index](../step-61/00-index.md) | Link 61b as shipped extension |

## Test gate

```bash
cd simplefactions && mvn test
```

Expected suites (new + touched):

- `ConfigLoaderBattlePresenceTest` (capture + phantom config)
- `CapturePointMinPlayersTest`
- `BattleDevModeTest`
- `CampaignBattleJoinServiceTest`
- `BattleJoinServiceTest` (extended)
- Existing 61 military suites still green

## Solo staging checklist (attacker path)

> **Superseded by [61c.05 campaign E2E](../step-61c/05-docs-verify.md)** (signup flow, staff battle edit, full war pipeline). Keep this list for historical 61b scope reference only.

Run on test server with one admin account:

1. [ ] `/battle devmode on` - status shows enabled  
2. [ ] Declare war - `/faction warstatus` shows `commitmentRows`  
3. [ ] `/faction warschedule` or GUI vote - schedule battle (`dev_min_players: 1`)  
4. [ ] `/warband create` - roster shows you + phantoms (member count 11)  
5. [ ] `/battle join <id> attacker` - succeeds on your side  
6. [ ] Wrong-side alt (if available) or doc that wrong side fails  
7. [ ] Battle starts - boss bar lives != template 25 (61.04)  
8. [ ] Capture point - solo progress with min=1  
9. [ ] `/kill` several times - side lives drop  
10. [ ] Win or end battle - commitments decrease (61.06), phase `VOTING`  
11. [ ] `/battle devmode off`  
12. [ ] Restart plugin - devmode off, no phantom persistence  

Defender path: separate tester (out of 61b scope).

## Done when

- [x] All 61b.02–61b.04 code merged  
- [ ] Solo checklist items 1–12 passed on staging  
- [x] `mvn test` green  
- [x] DEV-SHORTCUTS + index updated  

**Done** (2026-08-21). **Next batch:** [62 war end & goals](../step-62/00-index.md).
