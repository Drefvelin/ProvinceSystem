# Step 31.05 — Website drinks UI

**Repos:** `ProvinceSystem/frontend`

## Goal

`/drinks` redeem + brew editor (parallel to `/skins`).

## Plan

1. Redeem drink session (reuse redeem patterns; separate storage key).
2. Form fields: recipe key, 3 quality names, ingredients (+ amounts), cookingtime, distillruns/time, wood, age, difficulty, alcohol, lore, drink message/title, glint, effects (filtered by blacklist), color **or** texture.
3. Ingredient picker from catalog (grouped by category).
4. Noble: hide texture upload + reuse. Gilded+: upload PNG (16×16) **or** pick existing textures from API.
5. Client validation matching API.
6. Status page after submit (pending / approved / denied / pending_pack).

## Verify

- [x] Noble cannot enable texture UI.
- [x] Submit creates pending drink.
- [x] Catalog empty → clear empty state.

## Done when

- [x] Happy-path submit from browser for color-only and textured (ui-dev or staging).
