# Batch 9.02 — Config restore + YAML migrate

**Plan + build:** Restore lost keys; split `name` / `colour` in plugins + resources.

## Plan

1. Restore `skins-api`, `pack-apply` (+ force-reload / delay) on live + resources config.  
2. Ensure `ps_armor` / `ps_items` in plugins `categories.yml`.  
3. Migrate SkinSet + category names: peel `#hex` / `§x` / `§#hex` into `colour`.  
4. Preserve `add-name`.

## Verify

- [x] Live config has skins-api + pack-apply schedule keys  
- [x] Sample SkinSets have plain name + colour  
- [x] ca_* add-name counts preserved
