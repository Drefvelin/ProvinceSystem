# Batch 29.03 — Kit list + editor UX

**Plan + build:** Character kit detail + editor: custom name, Custom tag, pending lock, dirty submit, delete.

**Repos:** `ProvinceSystem/frontend`  
**Depends on:** [02-delete-api](./02-delete-api.md)

## Locked

| Piece | Choice |
|-------|--------|
| List page | `frontend/app/character/[id]/kits/[kitId]/page.tsx` uses `customise` / draft for label + state |
| Pending | Grayed row; no Edit; View status; “Pending approval” |
| Custom | Blue **Custom** tag on Edit when customise exists and not pending |
| Editor | Prefill from draft as today |
| Submit | Disabled until dirty vs initial snapshot |
| Delete | Visible when customise exists; confirm; 29.02 API; back to kit list |

## Done

1. Kit detail: custom labels, pending / Custom UI  
2. `LoreItemEditor`: dirty Submit + Delete  
3. `deleteLoreItemCustomise` FE helper + ui-dev fixtures  

## Verify

- [ ] Pending item not editable from list  
- [ ] Custom name + tag after ready/saved customise  
- [ ] Submit stays disabled with no edits  
- [ ] Delete restores default label on list  

## Status

**Implemented** (29.03). Next: [04-claim-as-gate](./04-claim-as-gate.md).
