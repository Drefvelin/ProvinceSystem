# Step 70.06 — Docs and verify

**Repos:** `simplefactions` · `ProvinceSystem` (planning)

## Docs updated

| File | Changes |
|------|---------|
| [`Wars.md`](../../../../simplefactions/Documentation/Wars.md) | Step 70 implementation status; dual-leg declare pipeline; per-leg trim (`max_battles_per_leg`); asymmetric initiative; active-leg progression; counter persistence fields; dual-leg route GUI; build steps table |

## Automated verify

```bash
cd simplefactions && mvn test
```

- [x] Full test suite passes (556 tests)

## Manual smoke (operator)

- [ ] Declare war on axis with asymmetric legs (e.g. invasion 4 slots, counter 2)
- [ ] Campaign view shows battle kinds on provinces **both** sides of border
- [ ] Counter-push (`TOWARD_AGGRESSOR_CAPITAL`) highlights green concrete on counter leg current slot
- [ ] `/warstatus <id>` JSON includes `campaignCounterSchedule` and `campaignCounterScheduleIndex`
- [ ] `/faction warschedule <id> opencvote` lists invasion and counter schedule sections

## Migration

Wars declared before step 70: **re-declare** to rebuild both legs and asymmetric fuel. Legacy JSON without `campaignCounterSchedule` loads with symmetric defender fuel default from invasion schedule count.

## Status

**Done** (2026-08-23).

## Next

[step 66](../step-66/00-index.md) — war campaign map.
