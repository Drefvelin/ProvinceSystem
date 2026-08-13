# Step 17.05 — Scoped `/token create`

**Plan + build:** Player `/token create skin|character` on TFMCWeb; API accepts `scope`.

## API

| Route | Auth | Behaviour |
|-------|------|-----------|
| `POST /skins/codes` | `X-Plugin-Key` | Body `{player_uuid, scope?}` — `skin` (default), `character`, or `skin_staff`. Requires Discord **eligible**. Scope `skin` also enforces ArmourShop entitlements (cooldown / disallow). |

DB: `codes.scope TEXT NOT NULL DEFAULT 'skin'` (migrated).

Self-test: `cd backend && PYTHONPATH=. python -m src.skins.codes`

## TFMCWeb

| Command | Perm | Action |
|---------|------|--------|
| `/token create skin` | `tfmcweb.token.create` (default false) | Mint skin code; redeem on skins site; PS may reject if rank disallowed / on cooldown |
| `/token create character` | same | Mint character code; redeem not available yet |
| `/token create skin staff` | `tfmcweb.token.create.staff` | Staff mint; bypasses cooldown/kinds |
| `/token` | — | Usage |

ArmourShop `/armourshop token create` removed in [06](./06-armourshop-cutover.md) (redirects to `/token create skin`). Admin `listtokens` / `token delete` remain on ArmourShop.

## Verify

1. Linked ranked player: `/token create skin` → redeem on staging `/skins` → session works; KindPicker filtered.
2. Non-ranked / defaults: mint fails (“cannot create skin tokens”).
3. `/token create character` → code issued; `POST /skins/redeem` rejects; character redeem path as shipped.
4. Unlinked / past grace: mint fails (“Link Discord…”).
5. ArmourShop `token create` redirects to `/token create skin`.
6. Jar: `Builds/TFMCWeb/tfmcweb-1.0-SNAPSHOT.jar`.

## Done when

Skins redeem still works from TFMCWeb-minted codes; ArmourShop mint can be deprecated in 06; rank cooldown/kinds enforced in PS.

**Depends on:** [04-tfmcweb-scaffold](./04-tfmcweb-scaffold.md).
