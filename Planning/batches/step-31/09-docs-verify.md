# Step 31.09 — Docs + staging verify

**Depends on:** 31.02–31.08 implemented.

## Docs to refresh

- [x] [15-drink-builder.md](../../15-drink-builder.md) — mark shipped bits  
- [x] [13-tfmcweb.md](../../13-tfmcweb.md) — shared cooldown + drink token  
- [x] [12-end-to-end-flows.md](../../12-end-to-end-flows.md) — Flow drink  
- [x] [05-skins-system.md](../../05-skins-system.md) — mint cooldown moved to TW  
- [x] [STAGING.md](../../../STAGING.md) — Step 31 checklist  
- [x] Disable / document retirement of ConditionalEvents `/tfmc drinks`

## Staging checklist

Operator ticks live in [STAGING.md](../../../STAGING.md) Step 31 (leave unchecked until live smoke):

- [ ] Non-ranked cannot `/token create skin|drink`  
- [ ] Shared cooldown skin ↔ drink  
- [ ] Noble: color-only drink approve → Brewery recipe  
- [ ] Gilded: textured drink → `tfmc_drinks` + CMD match  
- [ ] Ingredient picker shows draft list (pruned as needed)  
- [ ] Discord approve/deny + DMs  
- [ ] Staff delete + shared texture refcount  
- [ ] `/tfmc drinks` disabled or redirects to token+website  

## Done when

Checklist green; playbook success criteria met.

## Status

**Done** (docs/hubs/cutover notes):

- Planning hubs mark Step 31 / Track F code done
- STAGING Step 31 deploy + operator checklist added
- CE `events/drinkbuilder.yml` → `drinkbuilder.yml.disabled` (reload ConditionalEvents on server)
