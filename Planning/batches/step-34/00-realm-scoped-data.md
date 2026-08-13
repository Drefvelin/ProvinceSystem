# Step 34 — Realm-scoped game data

**Repos:** `Workspace/tfmcweb` · `ProvinceSystem` · `Workspace/rpcharacters` · `Workspace/armourshop` · `Workspace/drinkbuilder`  
**Depends on:** Realm stamp on codes/creates ([step-33](../step-33/00-realm-token-policy.md))

## Goal

Characters (and skin/drink apply queues) created in one realm do not land on another. Lobby mint → `main` create → **only main RPC** ingests; tutorial/dev stay isolated.

**Superseded by [step-35](../step-35/00-http-gateway-per-realm.md):** plugins now call PS only through TFMCWeb `ProvinceSystemGateway` (hard depend). Skin/drink slug uniqueness and character display names are **per-realm** (Plan 3 had kept them global).

## Locked defaults

- Realm is defined **only** in TFMCWeb `realm.id`.
- Plugins soft-depend TFMCWeb and call `getRealmId()` (via reflection helpers); fallback `"main"` if TFMCWeb is absent.
- Lobby + main share `main`; tutorial / dev are separate.
- Staff Discord review queues stay **unfiltered** (one bot sees all realms).
- Skin/drink slug uniqueness and `rpc_player_meta` / `character_player_meta` stay **global**.

## What shipped

1. TFMCWeb `TFMCWeb.getRealmId()` (+ soft-dep docs in `config.yml`)
2. PS pending creates filtered by `realm_id`; `character_roster` PK `(player_uuid, realm_id, character_id)`; `list_for_player` scoped
3. `submissions.realm_id` / `drink_submissions.realm_id` stamped at create; plugin approved / pending-apply filtered
4. RPCharacters / ArmourShop / DrinkBuilder pass `realm_id` on pending/roster/apply HTTP

## Operator notes

See [STAGING.md](../../../STAGING.md) **Step 34**. Main RPC must share TFMCWeb `realm.id: main` with lobby; tutorial/dev boxes must run TFMCWeb with matching realm.
