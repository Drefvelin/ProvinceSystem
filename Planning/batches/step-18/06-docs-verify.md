# Batch 18.06 — Docs + staging verify

**Plan + build:** Docs only + staging checklist. No new features.

**Depends on:** 18.01–18.05

## Docs hubs

| File | Change |
|------|--------|
| [10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md) | Staff lane: `tfmc_armorshop`, catalog sync, scroll config |
| [05-skins-system.md](../../05-skins-system.md) | Staff token + auto-approve vs player review |
| [12-end-to-end-flows.md](../../12-end-to-end-flows.md) | Short staff curated flow |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | Step 18 pointer |
| This step `00-index` | Status **18.01–18.06 done** when shipped |

## Staging checklist (humans tick)

- [ ] Scrolls listed in AS `config.yml`; enable syncs catalog  
- [ ] `/token create skin staff` → redeem → category + scroll visible  
- [ ] Staff armor → `tfmc_armorshop` + chosen `a_*` category + scroll; usable in shop  
- [ ] Staff gun → applies (IA + GaG) into item category  
- [ ] Player `/token create skin` → still Discord review + `tfmc_submissions` / `ps_*`  
- [ ] No bot / `#bot-feed` post for staff submit
- [ ] Staff skin id is display-slug only (no MC IGN); reusing an existing category key is rejected
- [ ] `/armourshop skin delete <id>` clears `tfmc_armorshop` + category YAML + API row (not legacy `tfmc_armor`)
- [ ] `/armourshop submission delete` still only for player `ps_*` lane

Also mirrored under [STAGING.md](../../../STAGING.md) Step 18.

## Implemented

- [STAGING.md](../../../STAGING.md) Step 18 deploy notes + operator checklist (`tfmcweb.token.create.staff`)
- Track D / checklist / hubs / batches README marked done
- Step-18 `00-index` closed as **18.01–18.06 done**

## Out of scope

Character creator; `tfmc_armor` migration.
