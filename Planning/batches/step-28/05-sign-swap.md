# Batch 28.05 — Book sign texture swap

**Plan + build:** When a player signs a book that carries a book skin, switch from `{slug}` (unsigned) to `{slug}_signed`.

**Repos:** `Workspace/armourshop` (listener / SkinManager hook)  
**Depends on:** [04-pack-apply](./04-pack-apply.md)

## Locked

| Piece | Choice |
|-------|--------|
| Trigger | Writable book → signed/written book while stack is an ArmourShop book skin (`{slug}`) |
| Action | Replace / re-merge stack to IA id `{slug}_signed` (WRITTEN_BOOK + signed texture) |
| Preserve | Custom display name, lore, kit PDC / skin binding where possible |
| Content | Keep signed book pages/title/author from the sign event |
| Non-skinned | No-op |
| Kit PDC | Copy full PDC so kit customise identity survives |

## Done

- `BookSignSkinListener` — `PlayerEditBookEvent` + 1-tick swap to `{id}_signed` when sibling IA item exists
- Registered in `ArmourShop.registerListeners`

## Verify

- [ ] Apply book skin → unsigned look on writable book  
- [ ] Sign → signed look without losing skin binding / custom name  
- [ ] Unsigned vanilla book without skin unchanged  
- [ ] Kit-claimed journal signs to signed texture  

## Status

**Implemented** (28.05 code). Operator ticks above. Next: [06-kit-journal](./06-kit-journal.md).
