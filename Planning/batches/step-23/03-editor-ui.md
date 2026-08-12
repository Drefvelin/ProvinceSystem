# Batch 23.03 — Lore item editor UI

**Plan + build:** Dark preview (name + inline lore), NameColourPicker, pick thumbs, 3D checkbox, duplicate UX.

**Repos:** `ProvinceSystem/frontend`  
**Depends on:** [01](./01-pickable-preview-apply.md), [02](./02-customise-name-lore-hash.md)

## Locked UX

| Piece | Choice |
|-------|--------|
| Preview | Dark box; name gradients via `NameColourPicker`; lore inline runs |
| Pick | Thumbs from character texture URL; staff + own only |
| Upload | Flat PNG default; 3D checkbox → model + texture + preview |
| Copy | No Discord tip / nudge |

## Plan

1. Extend `LoreItemEditor` + API types for colours, namespace, 3D, pick preview URLs.
2. Inline lore formatter helper (TLibs-like token parse).
3. Wire pick list thumbs; 3D checkbox; duplicate error → suggest pick.
4. UI-dev fixture rich enough to review without API.

## Verify

- [x] Preview shows mid-line lore colour
- [x] Name colour stops work with rank cap
- [x] Pick thumbs load; missing not shown
- [x] 3D checkbox uploads model path
- [x] No switch/kill / tip nudges

## Status

**Implemented** (23.03). Next: [04-docs-verify](./04-docs-verify.md).

## Out of scope

Docs close (04).
