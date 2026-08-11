# Batch 21.06 — Kit claim command (Phase 2 cutover)

> **Follow-on:** [08-kits-yml-and-kit-service](./08-kits-yml-and-kit-service.md) generalises this beyond a single starter-shaped kit (`kits.yml`, `KitService`, per-kit cooldown).

**Plan + build:** Stop auto-granting the starter kit. Players claim with `/rpcharacter kit starter` once per character, with a 48h per-player cooldown between successful claims. Align with [14 Phase 2](../../14-character-creator.md).

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `frontend` (cooldown/create warning cleanup)  
**Depends on:** [step-20](../step-20/00-index.md) 20.01–20.03 plumbing; pairs with [07](./07-create-window-customise.md) for `pending_skin` gate (can ship claim first, then wire gate in 07)

## Locked

| Piece | Choice |
|-------|--------|
| Command | `/rpcharacter kit starter` (active character) |
| Success | Give kit items → `kit_status=granted` → stamp player `last_kit_grant_at` |
| Cooldown | 48h after successful claim; create anytime; new character stays **eligible** until claim or policy |
| Remove | Auto `tryGrant` on join / reload / create; permanent `ineligible` for create-during-cooldown |
| Create warnings | Remove “wait X hours or you will not receive a kit” create warnings (web + in-game). Discord owns player messaging |
| Command feedback | Cooldown remaining, already claimed, no active character, empty kit.yml, (later) pending custom knife |
| Legacy | Null/legacy kit status: never claimable unless explicitly migrated; already `granted` stays done |

## Implemented

- `StarterKitService.tryClaim`; `onCharacterCreated` always `eligible`; no join/reload/create auto-grant
- Historical `ineligible` can still claim (recovery)
- `/rpcharacter kit starter` + tab complete
- Removed in-game create kit warnings (`CreationManager`)
- Removed web kit cooldown warning UI (`kitCooldown.ts` deleted; list/wizard cleaned)

## Verify

- [x] Claim with eligible character + clear cooldown → kit once; status `granted` *(code path)*
- [x] Second claim same character → rejected *(code path)*
- [x] New character during 48h cooldown → can create; claim rejected until cooldown clears; then claim works *(code path)*
- [x] Join / reload does **not** auto-grant *(hooks removed)*
- [x] No create warning about losing kit forever *(MC + web)*

Operator smoke: [STAGING.md](../../../STAGING.md) Step 20 (after jar deploy).

## Out of scope

Wizard knife UI (07); Discord announcement copy; changing kit item list.
