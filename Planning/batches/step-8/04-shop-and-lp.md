# Batch 8.04 — Shop YAML + LuckPerms

**Plan + build:** Write player submission SkinSets into `ps_armor` / `ps_items`; grant LP; merge `item-start-points` into jar config.

**Repos:** `Workspace/armourshop`

**Depends on:** [03-pull-and-write](./03-pull-and-write.md)

## Plan

1. Ensure category index entries + `Categories/ps_armor.yml` / `ps_items.yml` (create if missing).
2. Append/update SkinSet per submission that successfully wrote pack:
   - Armor → `ps_armor`: helmet/chestplate/leggings/boots → `ia.tfmc_submissions:{slug}_…`
   - `handheld` / `large_handheld` (and later bow kinds) → `ps_items`: `item: ia.tfmc_submissions:{slug}`
   - `set: {base_set}`, `name` from display_name, `permission: armourshop.submission.{slug}`, **no scroll**
3. Grant issuer UUID `armourshop.submission.{slug}` via LuckPerms API.
4. Set `pack-apply.categories-path` to live Categories path (match loaders).
5. **Config merge:** add `item-start-points` from server `config_new.yml` into jar `config.yml`; keep `pack-apply`; do **not** commit staging secrets. Remove or ignore `config_new.yml` after merge.

## Build

| File | Action |
|------|--------|
| Shop writer | ensure categories + append sets |
| LP helper | grant node to `player_uuid` |
| `config.yml` | `item-start-points` + categories-path |
| Apply pipeline | call after successful pack write |

## Verify

```bash
cd Workspace/armourshop
mvn -DskipTests package
```

In game (admin): approve armor + handheld, then `/armourshop pack pull` with `skins-api.*` + `pack-apply.*` set.

- [x] `item-start-points` + `categories-path` in jar `config.yml`; `config_new.yml` removed  
- [x] `ShopSubmissionWriter` ensures `ps_*` + upserts SkinSets  
- [x] `LuckPermsGrant` + shop/LP/`reload()` on pack pull main-thread callback  
- [ ] In game: issuer sees set after auto-reload; others do not  
- [ ] SkinSet `set:` matches uploaded `base_set`  
- [ ] Item GUI uses `item-start-points` slots  

**Implemented:** shop writer + LP console grant; pack pull sync path wires both then `reload()`.

## Out of scope

IA pack reload; applied ack (05); bow writers (07).
