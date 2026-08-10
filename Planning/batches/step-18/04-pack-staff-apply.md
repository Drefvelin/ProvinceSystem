# Batch 18.04 — Pack apply into `tfmc_armorshop` + category

**Plan + build:** Scaffold `tfmc_armorshop`; staff-approved pulls write there; shop upsert into chosen category with scroll; no submission LP. Reuse all existing writers including **guns**.

**Repos:** `Workspace/armourshop` · IA contents scaffold

**Depends on:** [02-staff-token-api](./02-staff-token-api.md)

## Plan

1. **Scaffold** `contents/tfmc_armorshop/` (namespace.yml + texture/model dirs) beside `tfmc_submissions` — Copy + live as needed.
2. **Writers** — parameterize namespace (default `tfmc_submissions`; staff → `tfmc_armorshop`). Prefer one constant/path helper over copy-paste forks. Guns: same GaG `skins.yml` append; IA ids under new namespace.
3. **Shop** — staff path: upsert SkinSet into `Categories/<category>.yml` with `scroll:` from payload; armor pieces / item / `gunskin({id})` as today but `ia.tfmc_armorshop:…`. **Do not** write `ps_armor`/`ps_items`; **do not** grant `armourshop.submission.*`.
4. **Player path** — unchanged (`tfmc_submissions` + `ps_*` + LP).
5. **Reload/ack** — same deferred IA reload + `markApplied` for both lanes.
6. **Delete** — player: `/armourshop submission delete` (submissions + `ps_*` + LP). Staff: `/armourshop skin delete` ([07-staff-delete-ids](./07-staff-delete-ids.md)) clears `tfmc_armorshop` + `{category}.yml`; never legacy `tfmc_armor`.

## Build

| Area | Action |
|------|--------|
| `PackPaths` / writers | namespace param |
| `ShopSubmissionWriter` or staff shop writer | category + scroll |
| scaffold | `tfmc_armorshop` |
| `PackApplyService` | branch on staff flag |

## Verify

- [x] Staff armor → files under `tfmc_armorshop` + set in e.g. `a_medieval.yml` with scroll  
- [x] Staff gun → IA + GaG skins.yml + item category entry  
- [x] Player pull still only touches `tfmc_submissions` / `ps_*`  
- [x] No LP grant for staff  

## Implemented

- Scaffold `tfmc_armorshop` (live + ItemsAdder Copy) with grip models
- Client parses `staff` / `category` / `scroll` / `tier_scrolls` / `ia_namespace`
- Writers + `GunsSkinsYml` take namespace; staff model JSON rewrite at apply
- Staff shop upsert into `{category}.yml` with scroll; player `ps_*` unchanged
- `PackPullRunner` skips LP for staff; queues on shop-only success

## Out of scope

Website UI; migrating `tfmc_armor`.
