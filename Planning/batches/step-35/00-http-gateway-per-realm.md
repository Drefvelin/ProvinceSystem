# Step 35 — TFMCWeb HTTP gateway + per-realm isolation

**Repos:** `Workspace/tfmcweb` · `ProvinceSystem` · `Workspace/rpcharacters` · `Workspace/armourshop` · `Workspace/drinkbuilder`  
**Depends on:** Realm-scoped create/apply queues ([step-34](../step-34/00-realm-scoped-data.md)) · `rpc_player_meta` ([step-32](../step-32/00-rpc-player-meta.md))

## Goal

Domain plugins stop opening their own HTTP to ProvinceSystem. TFMCWeb is the only holder of `api.base-url` / `api.plugin-key` and auto-injects `realm_id`. Entitlements, lore-items, and cosmetic/character uniqueness are scoped per realm.

## Locked defaults

| Topic | Choice |
|-------|--------|
| Gateway | In-process `ProvinceSystemGateway` (JSON + bytes + download) |
| Plugin dep | Hard `depend: [TFMCWeb]` on RPC / ArmourShop / DrinkBuilder |
| Meta writer | TFMCWeb only; AS/DB player-meta sync removed |
| `rpc_player_meta` | PK `(player_uuid, realm_id)` |
| Skin/drink ids | Uniqueness per realm; non-`main` ids prefixed `{realm}_` |
| IA namespaces | `tfmc_submissions` / `tfmc_drinks` on main; `_*_{realm}` elsewhere |
| Character names | Unique per `(realm_id, name)` |
| Staff Discord queues | Still global |

## What shipped

1. TFMCWeb `ProvinceSystemGateway` + realm injection allowlist
2. Plugin clients via reflective `GatewayClient`; removed per-plugin API config
3. Retired AS/DB `PlayerMetaSyncService`; deprecated PS legacy player-meta routes
4. Per-realm `rpc_player_meta` + optional `player-meta.by-realm.<id>` ladders
5. Lore-item `realm_id` stamp + pending filter
6. Per-realm slug/name uniqueness + IA namespaces

## Operator notes

See [STAGING.md](../../../STAGING.md) **Step 35**. Every game box that runs RPC/AS/DB **must** run TFMCWeb (no soft fallback for HTTP). Remove stale `characters-api` / `skins-api` / DrinkBuilder `api` blocks from live configs.

## Status

**Done** (code). Operator ticks: [STAGING.md](../../../STAGING.md) Step 35.
