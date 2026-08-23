# Step 61c.05 — Docs verify & campaign E2E

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.02](./02-template-settings-only.md), [61c.03](./03-warschedule-output.md), [61c.04](./04-campaign-warband-signup.md) · **Next:** [62 war end & goals](../step-62/00-index.md)

## Goal

Test gate, doc updates, and **full campaign E2E checklist** from declare through battle loop to war end probe (goal enforcement remains step 62).

## Docs

| File | Action |
|------|--------|
| [DEV-SHORTCUTS.md](../../DEV-SHORTCUTS.md) | 61c section: template rules-only, warschedule formatted output, signup flow |
| [Wars.md](../../../../simplefactions/Documentation/Wars.md) | Staff-light: templates = rules; geometry per battle via staff edit; campaign signup |
| [61b.05](../step-61b/05-docs-verify.md) | Add note: solo checklist superseded by 61c E2E (keep 61b test suite refs) |
| [00-index](./00-index.md) | Mark 61c batches done |
| [war-build-order.md](../../war-build-order.md) | 61c status |
| [62 00-index](../step-62/00-index.md) | Depends on 61c |

## Test gate

```bash
cd simplefactions && mvn test
```

Expected new / touched suites:

- `BattleFactoryTest` (settings-only templates)
- `WarScheduleFeedbackFormatterTest`
- `WarbandCampaignSignupTest` / updated roster + devmode tests
- Existing 61b + 61 military suites still green

---

## Campaign E2E checklist (test server)

Run with one admin (+ optional second account for wrong-side check). Use `dev_min_players: 1` and optional `/battle devmode on` for solo capture.

**Operator sign-off:** Run this checklist on the test server before treating 61c as fully verified in staging. Items below remain unchecked until an operator completes the run.

### A. War setup

1. [ ] `/battle devmode on` (optional) - status enabled  
2. [ ] Declare war (GUI or admin) - `/faction warstatus <id>` shows commitments JSON  
3. [ ] `/faction warschedule <id> opencvote` - **formatted** lines only (no JSON blob)  
4. [ ] `/faction warschedule <id> castvote 21 both` - shows hour, voters, phase  
5. [ ] `/faction warschedule <id> forcequorum`  
6. [ ] `/faction warschedule <id> closevote` - shows scheduled instant + province  
7. [ ] Or `setscheduled <iso>` - formatted scheduled + province  

### B. Battle prep (auto + staff)

8. [ ] Campaign battle exists (`campaign_w<id>_p<province>`) - sides have warband shells, **0 members** until signup  
9. [ ] `/warband list` - faction warband visible; **you are not auto-added**; leader `Pending signup` until join (61c.06)  
10. [ ] Staff: `/battle edit` (or GUI) - set spawns, jails, capture point(s) (templates did not seed coords)  
11. [ ] `/warband list` → join - you sign up; first joiner is leader (or war leader promotes if they join)  
12. [ ] Devmode: with `battlecreate`, phantoms fill both sides (first dummy is leader); otherwise phantoms after first signup  

### C. Fight loop

13. [ ] Battle starts (scheduled tick or `/battle start`) - boss bar lives from signups + 61.04 formula  
14. [ ] Wrong-side player cannot join warband (61b side check)  
15. [ ] Capture point progresses with `capture_min_players: 1`  
16. [ ] `/kill` - collective lives drop; ledger tracks  
17. [ ] Win or end battle - 61.06 casualties apply; war phase returns to **VOTING**; commitments decreased  

### D. War end probe (pre-62)

18. [ ] Repeat B–C for a second battle OR skip with `warschedule skipday` / mock vote  
19. [ ] End war: `/faction endwar <id>` **or** white peace via Campaign GUI if conditions met  
20. [ ] `/faction warstatus <id>` - status ended (goal **not** auto-applied until step 62)  

### E. Cleanup

21. [ ] `/battle devmode off`  
22. [ ] Restart plugin - devmode off, no phantom persistence  

---

## Done when

- [x] All 61c.02–61c.04 code merged  
- [x] Docs updated  
- [x] `mvn test` green  
- [ ] E2E checklist executed on test server (operator sign-off pending)

**Done** (2026-08-21). **Next:** [62 war end & goals](../step-62/00-index.md).
