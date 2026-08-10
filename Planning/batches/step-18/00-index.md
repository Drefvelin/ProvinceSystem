# Step 18 — Staff skins (curated ArmourShop via web)

**Repos:** `Workspace/armourshop` · `ProvinceSystem` · `Workspace/tfmcweb` · `frontend`  
**Depends on:** Player skins apply live ([step-8](../step-8/00-index.md)+); gun apply ([step-14](../step-14/00-index.md)/[15](../step-15/00-index.md)); TFMCWeb tokens ([step-17](../step-17/00-index.md))  
**Playbook:** [10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md) · [05-skins-system.md](../../05-skins-system.md)

## Goal

Reuse the **existing** skins upload → pack apply pipeline in **staff mode**: mint a staff token, upload on `/skins` (same kinds including **guns**), **auto-approve** (no Discord bot), write IA into a **new** namespace `tfmc_armorshop`, and upsert the SkinSet into a **real** ArmourShop category with a **scroll** — not `ps_*` + LP.

ArmourShop **syncs catalog** (categories, existing skin sets, scrolls) to ProvinceSystem on load so the website dropdowns stay honest.

## Locked rules

| Piece | Choice |
|-------|--------|
| Player lane | Unchanged: `tfmc_submissions` + `ps_armor`/`ps_items` + LP; Discord review |
| Staff lane | Same writers/kinds; destination `tfmc_armorshop` + chosen category YAML + scroll |
| Legacy pack | Leave `tfmc_armor` as-is (no migrate/rename) |
| New pack | **`tfmc_armorshop`** only for **new** staff-authored skins |
| Token | `/token create skin staff` (TFMCWeb); perm e.g. `tfmcweb.token.create.staff` |
| Approve | **Auto** on submit — **no** bot / `#bot-feed` |
| Catalog sync | On ArmourShop enable (+ optional admin command): categories, skin-set keys, scrolls |
| Scrolls | Defined in ArmourShop `config.yml`; synced to API; web dropdown only from catalog |
| UI | Category + scroll dropdowns (armor: scroll per tier OK); same upload/preview |
| Guns | **In scope** — same gun path; only landing + auto-approve differ |
| Player tokens | Cannot set category/scroll; cannot write `tfmc_armorshop` |
| Staff categories | Curated `a_*` / `i_*` / etc. — **omit** `ps_armor` / `ps_items` from staff dropdown |
| Staff submission id | **Display-slug only** (`slugify(item name)`); no MC IGN prefix; collision = invalid |
| Delete | Player: `/armourshop submission delete` · Staff: `/armourshop skin delete` (clears `tfmc_armorshop` + category YAML; never legacy `tfmc_armor`) |

## Suggested build order

1. **[01-catalog-sync](./01-catalog-sync.md)** — Scrolls in AS config; push catalog to API; `GET` for web/plugin.
2. **[02-staff-token-api](./02-staff-token-api.md)** — Staff code flag; submit stores category/scroll; auto-approve; plugin list includes staff.
3. **[03-tfmcweb-staff-mint](./03-tfmcweb-staff-mint.md)** — `/token create skin staff`.
4. **[04-pack-staff-apply](./04-pack-staff-apply.md)** — `tfmc_armorshop` scaffold; writers + shop upsert into chosen category; no LP for staff; guns included.
5. **[05-web-staff-ui](./05-web-staff-ui.md)** — Catalog-driven dropdowns; staff session UX.
6. **[06-docs-verify](./06-docs-verify.md)** — Docs + staging checklist.
7. **[07-staff-delete-ids](./07-staff-delete-ids.md)** — Display-only staff ids + `/armourshop skin delete`.

**Immediate next action:** tick human staging on live ([STAGING.md](../../../STAGING.md) Step 18 / [06-docs-verify](./06-docs-verify.md)).

## Out of this step

- Migrating or renaming existing `tfmc_armor` contents  
- Character creator / identity work  
- Changing player submission / Discord review flow  
- Rewriting gun writers (reuse as-is)

## Checkpoint

```text
catalog sync → staff token + auto-approve API → TFMCWeb mint
  → pack/shop into tfmc_armorshop + category → web dropdowns → verify
```

**Done when:** Staff mints staff token → uploads any supported kind (incl. gun) → skin lands in `tfmc_armorshop` and chosen category with scroll, without Discord approve; player flow unchanged.

## Status

**18.01–18.07 done** (code + docs). Next: operators tick staging checklist on live.
