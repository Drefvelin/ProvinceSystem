# Batch 18.07 — Staff skin delete + display-only IDs

**Plan + build:** Staff submission ids are display-slug only (no MC IGN). `/armourshop skin delete` clears `tfmc_armorshop` + category YAML (not legacy `tfmc_armor`). Player `/armourshop submission delete` stays player-lane only.

**Repos:** `ProvinceSystem/backend` · `Workspace/armourshop`

**Depends on:** [04-pack-staff-apply](./04-pack-staff-apply.md) · [02-staff-token-api](./02-staff-token-api.md)

## Plan

1. **Staff id** — `slugify(display_name)` only; reject catalog + active-DB key collisions as invalid.
2. **API** — plugin GET includes `staff` / `category` / `ia_namespace`; player vs staff deletable lists.
3. **Commands** — `submission delete` (player) · `skin delete` (staff: pack ns + `{category}.yml`, no LP).

## Verify

- [x] Staff submit id has no IGN prefix; collision → 400 with “invalid / already exists”
- [x] `/armourshop skin delete <id>` removes `tfmc_armorshop` files + category keys + API row
- [x] `/armourshop submission delete` refuses staff ids (and vice versa)
- [x] Legacy `tfmc_armor` untouched

## Implemented

- `build_staff_submission_id` + `staff_skin_set_key_taken` + sharpened catalog collision messages
- `GET /skins/plugin/skins/deletable`; player deletable excludes staff
- `PackSubmissionRemover` / `GunWriter.remove` namespace overloads; `ShopSubmissionWriter.removeStaff`
- `SkinDeleteRunner` + `DeletableStaffSkinCache`; CommandManager + plugin.yml
