# Batch 3.03 — Skins upload form

**Plan + build:** Kind picker + fixed file slots + naming + submit to `POST /skins/submissions`.

## Plan

1. Kind picker: `armor_set` | `item` | `handheld` | `large_handheld`.
2. Slots by kind (labels match API field names):
   - armor: helmet, chestplate, leggings, boots, layer_1, layer_2  
   - others: texture  
3. `large_handheld`: require grip preset `bottom` | `middle` | `top` (simple radio/segmented control — no 3D preview yet).
4. Display name + slug: auto-slugify from display name; show slug for confirm; client regex matches [07](../../07-naming-conventions.md); server still authoritative.
5. Size hints (client): icons 16×16; layers 64×32; item/handheld 16×16; large 32×32. Prefer reading IHDR in-browser before submit; show friendly error if wrong.
6. Submit multipart with `Authorization: Bearer <session>`; handle 400/409 messages.
7. On success → navigate to status for that submission id (or in-page status) — status UI finalized in 3.04; at minimum show id + status JSON.

## Build

| File | Action |
|------|--------|
| `frontend/lib/skins/sizes.ts` | expected dims + optional browser check |
| `frontend/lib/skins/slug.ts` | slugify / assert helpers |
| `frontend/components/skins/KindPicker.tsx` | create |
| `frontend/components/skins/UploadForm.tsx` | create |
| `frontend/lib/skins/api.ts` | `createSubmission(...)` |
| `frontend/app/skins/page.tsx` | flow redeem → upload |

## Verify

- [ ] Armor with correct-size fixtures uploads → pending  
- [ ] Wrong size blocked client-side (and/or shows API 400)  
- [ ] Large without grip blocked; with grip succeeds  
- [ ] Duplicate slug → 409 surfaced  

## Out of scope

Staff review sheet, Discord, applied status from plugin.
