# Batch 18.01 — ArmourShop catalog sync

**Plan + build:** Define scrolls in ArmourShop config; on plugin load push categories + skin-set keys + scrolls to ProvinceSystem; expose read API for the website.

**Repos:** `Workspace/armourshop` · `ProvinceSystem/backend`

**Depends on:** [00-index](./00-index.md) locked rules

## Plan

1. **ArmourShop `config.yml`** — add a scrolls list (id + display label), e.g. the `m.loot.*_item_skin_scroll` ids already used in Categories. Source of truth = plugin config, not scraped Mythic.
2. **On enable** (and optional `/armourshop catalog sync`): build payload:
   - categories from `categories.yml` + each `Categories/<id>.yml` (id, name, `is-item`, skin-set keys)
   - scrolls from config
   - omit nothing needed for collision checks; staff UI will hide `ps_*` later
3. **API** — `PUT` or `POST /skins/plugin/catalog` (`X-Plugin-Key`) replaces stored catalog snapshot; `GET /skins/catalog` (or staff/session-authenticated) for the site.
4. Persist simply (SQLite table or JSON file under skins data) — full replace on each sync is fine.
5. Log counts; fail soft on enable if API down (retry command exists).

## Build

| Area | Action |
|------|--------|
| AS `config.yml` + loader | `scrolls:` list |
| AS client + enable hook | push catalog |
| API routes + store | put + get catalog |

## Verify

- [x] API: `PUT /skins/plugin/catalog` + `GET /skins/catalog` (module/route smoke)
- [ ] AS enable → API has categories + scrolls (tick on live server after jar deploy)
- [ ] `/armourshop catalog sync` refreshes after YAML edit (tick on live server)

## Implemented

- ProvinceSystem: `armourshop_catalog` table; `catalog.py`; `PUT /skins/plugin/catalog`; `GET /skins/catalog`
- ArmourShop: `scrolls:` in config; `CatalogSyncService`; client PUT; async push on enable/reload; `/armourshop catalog sync`
- Also restored missing `BOW_KINDS` / `ITEM_KINDS` in `storage.py` (blocked skins router import)

## Out of scope

Staff tokens; pack writers; website dropdowns (consume GET in 05).
