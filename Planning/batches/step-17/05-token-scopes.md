# Step 17.05 — Scoped `/token create`

**Plan + build:** Player `/token create skin|character` on TFMCWeb; API accepts `scope`.

## API

| Route | Auth | Behaviour |
|-------|------|-----------|
| `POST /skins/codes` | `X-Plugin-Key` | Body `{player_uuid, scope?}` — `skin` (default) or `character`. Requires Discord **eligible** (linked, including in grace). |
| `POST /skins/redeem` | public | Skin codes only; character codes → 400 |
| `POST /skins/character/redeem` | public | **501** stub until creator ships |
| `GET /skins/plugin/codes/active` | plugin | Includes `scope` field |

DB: `codes.scope TEXT NOT NULL DEFAULT 'skin'` (migrated).

Self-test: `cd backend && PYTHONPATH=. python -m src.skins.codes`

## TFMCWeb

| Command | Perm | Action |
|---------|------|--------|
| `/token create skin` | `tfmcweb.token.create` (default false) | Mint skin code; redeem on skins site |
| `/token create character` | same | Mint character code; redeem not available yet |
| `/token` | — | Usage |

ArmourShop `/armourshop token create` removed in [06](./06-armourshop-cutover.md) (redirects to `/token create skin`). Admin `listtokens` / `token delete` remain on ArmourShop.

## Verify

1. Linked player: `/token create skin` → redeem on staging `/skins` → session works.
2. `/token create character` → code issued; `POST /skins/redeem` rejects; `POST /skins/character/redeem` → 501.
3. Unlinked / past grace: mint fails (“Link Discord…”).
4. ArmourShop `token create` still issues skin codes.
5. Jar: `Builds/TFMCWeb/tfmcweb-1.0-SNAPSHOT.jar`.

## Done when

Skins redeem still works from TFMCWeb-minted codes; ArmourShop mint can be deprecated in 06.

**Depends on:** [04-tfmcweb-scaffold](./04-tfmcweb-scaffold.md).
