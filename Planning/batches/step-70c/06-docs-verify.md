# Step 70c.06 — Docs verify

**Repos:** SF, Planning  
**Depends on:** [70c.05](./05-tests.md)

## Wars.md

- Geographic route row order (AC left → DC right)
- Single row, no pagination, `max_battles_per_leg` cap 4
- Border-B first-battle marker
- No counter-push lore

## Planning

- [70c.01](./01-planning-lock.md) lock written
- [70b.01](../step-70b/01-planning-lock.md) GUI section annotated superseded
- [war-build-order.md](../../war-build-order.md) lists step 70c

## Automated verify

```bash
cd simplefactions && mvn test -Dtest=CampaignRouteRendererTest,ConfigLoaderWarGoalsTest
```

## Manual verify (live server)

1. `plugins/SimpleFactions/config.yml` has `provinces_between_battles: 3`
2. `/faction warpath` regen on Brume vs Lantan
3. Open campaign GUI:
   - Counter wilderness fields (782, 672) left of border 709
   - First-battle marker under border slot
   - Invasion siege/field toward 705 on the right
   - No pagination arrows; no `Counter-push schedule` lore

## Done when

- [x] Automated tests green
- [ ] Manual Brume vs Lantan smoke (user)
