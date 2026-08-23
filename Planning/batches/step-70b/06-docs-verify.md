# Step 70b.06 — Docs & server verify

**Repos:** SF, Planning, PS  
**Depends on:** [70b.02](./02-cadence-config.md) through [70b.05](./05-export-align.md)

## Docs

### Wars.md

Updated sections:

- **Battle cadence** — default `provinces_between_battles: 3`; leg-walk grid cadence from border center
- **Campaign GUI** — schedule-only route row; invasion then counter pagination; fought / next / upcoming styling
- **Display names** — ordinal rule for scheduled slots
- **Map export** — `display_name`, one pin per slot, siege/port installation coords

### Step indexes

- [70/00-index.md](../step-70/00-index.md) — 70.05 route row superseded by 70b.03 note
- [war-build-order.md](../../war-build-order.md) — step 70b marked done

### DEV-SHORTCUTS

Cadence `3` documented; production target set to `3`.

## Automated verify

```bash
cd simplefactions && mvn test
cd ProvinceSystem/frontend && npm test -- warBattleMarkers
cd ProvinceSystem/backend/src && python -m unittest scripts.loader.test_markers
```

- [x] `mvn test` — full SimpleFactions suite passes
- [x] `npm test -- warBattleMarkers` — 11 tests pass
- [x] `python -m unittest scripts.loader.test_markers` — 26 tests pass

## Manual server checklist (user)

After deploy + plugin reload:

1. **Config** — live `plugins/SimpleFactions/config.yml` has `provinces_between_battles: 3`
2. **Regen** — `/faction warpath <Brume-Lantan war>` or re-declare test war
3. **In-game GUI**
   - [ ] Route row shows **only** scheduled battles (no gray wilderness filler)
   - [ ] Order: invasion slots in fight order (e.g. siege then Lanbury field)
   - [ ] Page 2+ (or counter section): counter slots include fight in wilderness before Brume capital
   - [ ] Hour vote row (red X) is separate from battle row
4. **warschedule / war JSON**
   - [ ] `campaignCounterSchedule` non-empty with provinces in `672–782` range
   - [ ] Invasion schedule ≤ 4 slots
5. **Map** (if export regen run)
   - [ ] `campaign_counter_schedule` in upload JSON
   - [ ] Battle pins: both slots at 705 visible (siege + field); Greenfort at fort coords

## Done when

- [x] All 70b batches marked done in [00-index](./00-index.md)
- [x] Docs committed
- [x] Automated tests green
- [ ] User sign-off on server checklist (or filed bugs for 70b.07)
