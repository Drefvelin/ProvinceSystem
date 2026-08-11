# Batch 21.03 — Web item editor UI

**Plan + build:** Character-site UI to customise the kit knife: reuse skins upload patterns as an **item editor**, not a free-form skins form.

**Repos:** `ProvinceSystem/frontend`  
**Depends on:** [02-lore-item-api](./02-lore-item-api.md)

## Locked UX

| Piece | Choice |
|-------|--------|
| Entry | **Target:** create wizard only ([07](./07-create-window-customise.md)). **Shipped in 21.03:** `/character` list → `/character/lore-item` (to be removed as player path) |
| Hidden | Kind picker, category, base-set (injected from kit config) |
| Shown | Base/current preview; pick existing knives skin **or** upload PNG; display name; lore lines; 3D/model preview if skins already support it for handheld |
| Preview | Full name + lore (base MI lines + custom lore); update as user edits |
| Submit | Does not block on Discord; show pending like skins status |
| Copy | No em dashes in player-facing strings |

## Plan

1. **Route/component** — e.g. `/character/lore-item` or modal from list; load GET lore-items.
2. **Refactor lightly** — Share upload/validation/3D bits from [`UploadForm.tsx`](../../../frontend/app/components/skins/UploadForm.tsx) without dragging staff/category UI.
3. **Name + lore fields** — Mirror `textValidation` rules used elsewhere.
4. **Status** — Pending / approved / denied wired to existing skins status patterns where a submission id exists.

## Verify

- [ ] Create flow still works; lore editor does not appear as a generic skins kind  
- [ ] Cannot change base-set in UI  
- [ ] Preview updates with name/lore  
- [ ] Upload + pick-existing both reachable  
- [ ] Mobile usable (no card clutter; one job per section)  

## Product note (post-ship)

Standalone list editor was the 21.03 ship. Move into create wizard and drop list CTA in [07](./07-create-window-customise.md). No tip/nudge copy about Discord or website.

## Out of scope

In-game GUI editor; Ascended gate UI.
