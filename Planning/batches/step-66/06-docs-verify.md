# Step 66.06 — Docs + verify

**Repos:** `simplefactions`, `ProvinceSystem`  
**Depends on:** [66.05 FE battle markers](./05-fe-battle-markers.md)

## Docs updated

| File | Changes |
|------|---------|
| [`Wars.md`](../../../../simplefactions/Documentation/Wars.md) | Web map campaign line + battle pins; step 66 reference; build table row |
| [`war-build-order.md`](../../war-build-order.md) | Step 66 done; step 71 for raids |
| [`16-map-platform.md`](../../16-map-platform.md) | Requirement 10 partial delivery note |
| [`step-68/00-index.md`](../step-68/00-index.md) | Route slice shipped in 66; occupation remains |
| [`step-44/00-index.md`](../step-44/00-index.md) | Campaign line + battle pins unblocked |

## Automated verify

```bash
cd simplefactions && mvn test
cd ProvinceSystem/frontend && npm test -- --run
cd ProvinceSystem/backend && python -m unittest src/scripts/loader/test_markers.py -q
```

## Manual smoke (operator)

- [ ] Declare campaign war on staging/dev map.
- [ ] Trigger map regen / `map_markers` upload.
- [ ] Web map shows smooth dotted line attacker capital → objective along axis.
- [ ] Battle pins at invasion + counter schedule provinces.
- [ ] Hover pin: battle kind + status (next/upcoming/fought).
- [ ] Counter-push switches "next" highlight to counter leg.
- [ ] No occupation tint (expected - step 68).

## Migration

Wars active before 66 deploy: re-upload markers or wait for next regen. No SF war JSON migration required.

## Status

**Done** (2026-08-23).

## Next

[step 71 inter-battle raids](../step-71/00-index.md)
