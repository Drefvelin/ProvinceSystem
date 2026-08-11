# Batch 21.07 — Create-window knife customise + claim gate

> **Superseded by [09-kits-web-character-ui](./09-kits-web-character-ui.md).** Product moved customise to character → Kits on `/character` (not create wizard). Keep this file for history; do not extend the wizard path.

**Plan + build:** Knife customise only during **website character creation**. Block whole-kit claim while customise is `pending_skin`. On successful claim when customise is `ready`, grant kit with skin+lore applied. No player tip/nudge copy (Discord owns messaging).

**Repos:** `ProvinceSystem` · `frontend` · `Workspace/rpcharacters`  
**Depends on:** [02](./02-lore-item-api.md)–[04](./04-apply-skin-and-lore.md); [06](./06-kit-claim-command.md)

## Locked

| Piece | Choice |
|-------|--------|
| Entry | Create wizard step (optional skip). Not character-list “Customise knife” as the player path |
| In-game create | No knife editor |
| Eligibility | Character **claimable** (`eligible` / not yet `granted`). Drop `kit_status=granted` requirement |
| Pending | `pending_skin` → `/rpcharacter kit starter` fails with clear reason until Discord → `ready` |
| Ready / lore-only | Claim allowed; grant applies customise in the same pass |
| No customise | Claim grants vanilla kit knife as today |
| Messaging | No new website/in-game nudges about Discord or “use the website next time” |

## Implemented

- API `_require_customise_allowed` (claimable roster or pending create UUID); `granted` → 403
- `remount_character_id` on create apply; plugin `GET …/lore-items/claim-status`
- Wizard knife step + post-create `customiseLoreItem(createId)`; list CTA removed
- `tryClaim` blocks on `pending_skin`; pulls ready customise before grant

## Verify

- [x] Web create can customise knife before claim; list has no customise CTA *(code path)*
- [x] In-game-created character claims vanilla kit (no customise) *(no in-game knife UI)*
- [x] Upload → `pending_skin` → claim blocked *(claim-status gate)*
- [x] Discord approve → `ready` → claim gives full kit with skin + lore *(ingest before grant + applyStored)*
- [x] Lore-only (no new PNG) can claim without Discord wait *(ready state)*
- [x] No new tip strings about website/Discord in FE or RPC create finish

Operator smoke: [STAGING.md](../../../STAGING.md) Step 21.

## Out of scope

21.05 docs; Ascended gate; changing Discord bot review UX.
