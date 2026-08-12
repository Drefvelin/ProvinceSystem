# Step 29 — Kit customise visibility + claim gate

**Repos:** `ProvinceSystem` (FE + BE) · `Workspace/rpcharacters`  
**Depends on:** Step 27 templates + resetkit · Step 28 book journal · deny purge (no retained `denied` rows)  
**Playbook:** [14-character-creator.md](../../14-character-creator.md)

## Goal

Make custom kit items **visible and manageable** on the character kit screen, and make **in-game claim** the place players learn when skins are not on ArmourShop yet. Drop the fake “kit ready” Discord DM promise.

## Locked rules

| Piece | Choice |
|-------|--------|
| Kit list label | Show customise `display_name` when present; else catalog / path label |
| Pending approval | Item row grayed; **Edit disabled** while that item’s skin submission is still `pending` (or customise `pending_skin` tied to pending review) |
| Custom tag | Blue **Custom** chip on the Edit control (or beside it) when a non-default customise exists and is not pending |
| Edit | Opens editor with saved name / lore / skin as today |
| Submit | Disabled until the form is **dirty** vs loaded baseline (also for first edit of a default item) |
| Delete | Player control on custom items: wipe **that** `lore_item_customisations` row only → back to catalog default. Does **not** delete `/skins` submission or applied skin |
| Optional customise | Customising only knife **or** only journal is fine |
| Kit-ready DM | **None.** Remove / rewrite status copy that promises a Discord DM when the kit is ready |
| Website status | Show **pending staff approval** for skins; do not frame as “kit ready notify” |
| Claim pull | On `/rpcharacter kit <id>`, pull customise payloads from PS (already) |
| Claim AS gate | If any customise for that kit needs a skin slug that is **not** present on ArmourShop/IA → message *Kit is not ready yet, awaiting skins* and **return** (no grant) |
| Claim approval gate | If any linked submission is still staff-`pending`, keep blocking with a clear in-game line (approval vs pack are distinct messages) |

## Batches (implement in order)

1. **[01-planning-lock](./01-planning-lock.md)** — Playbook claim/UX locks  
2. **[02-delete-api](./02-delete-api.md)** — Player wipe one kit-item customise  
3. **[03-kit-list-ux](./03-kit-list-ux.md)** — Labels, Custom tag, pending, dirty submit, delete  
4. **[04-claim-as-gate](./04-claim-as-gate.md)** — RPC pull + ArmourShop presence check + copy  
5. **[05-status-copy](./05-status-copy.md)** — Status card / pending-approval wording (no kit-ready DM)  
6. **[06-docs-verify](./06-docs-verify.md)** — Hubs + STAGING + handoff  

## Checkpoint

```text
customise knife or journal → list shows Custom / Pending
  → Edit dirty-gated; Delete resets item only
  → claim while skin pending approval → blocked (approval)
  → claim after approve before pack → "awaiting skins"
  → claim after AS has slug → grant with customise
```

**Done when:** Players can see and reset custom items on the site; claim tells them in-game when skins are missing from ArmourShop; no kit-ready DM copy.

## Status

**29.01–29.06 done** (code+docs). Operator ticks in STAGING Step 29.
