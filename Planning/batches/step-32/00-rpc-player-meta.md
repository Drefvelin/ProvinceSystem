# Step 32 — `rpc_player_meta` + TFMCWeb join sync

**Repos:** `ProvinceSystem` · `Workspace/tfmcweb` · frontend  
**Depends on:** TFMCWeb identity ([step-17](../step-17/00-index.md)) · drink/skin entitlements ([step-31](../step-31/00-index.md))

## Goal

Push **web-facing entitlements** from any server running TFMCWeb (including lobby-only) into ProvinceSystem `rpc_player_meta`, so drinks / skins / character colour stops work without DrinkBuilder, ArmourShop, or RPCharacters on that box.

## Locked rules

| Piece | Choice |
|-------|--------|
| Scope | Per `(player_uuid, realm_id)` — see [step-35](../step-35/00-http-gateway-per-realm.md) |
| Writer | TFMCWeb on join (+ `/web reload`, `/web syncmeta`) |
| Ladders | Duplicated YAML under `player-meta` in TFMCWeb `config.yml`; optional `by-realm.<id>` overrides |
| Flags | Configurable `sync-permissions` → `permission_flags` (e.g. `rulequiz.completed`) |
| Readers | Prefer realm-scoped `rpc_player_meta`; legacy drink/armourshop/character meta fallback **only for `main`** |
| Old writers | ArmourShop / DrinkBuilder player-meta PUTs **removed** (Step 35); PS routes deprecated |

## What shipped

1. PS table + module `characters/rpc_player_meta.py`
2. `PUT /characters/plugin/rpc-player-meta` · `GET /characters/player-meta`
3. Redeem/submit/list readers use `resolve_web_entitlements`
4. TFMCWeb `player-meta` config + `EntitlementResolver` + join sync
5. Frontend refresh of meta on BrewForm / skins upload

## Operator notes

See [STAGING.md](../../../STAGING.md) **Step 32**. Lobby jar must ship `player-meta` ladders matching donator groups; players join once before expecting colours on the website.
