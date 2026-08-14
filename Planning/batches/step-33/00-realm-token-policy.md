# Step 33 — Realm + token policy

**Repos:** `Workspace/tfmcweb` · `ProvinceSystem` · frontend sessions  
**Depends on:** TFMCWeb tokens ([step-17](../step-17/00-index.md)) · `rpc_player_meta` ([step-32](../step-32/00-rpc-player-meta.md))

## Goal

Per-server mint policy: lobby can mint **character only**; lobby + main share `realm=main`; tutorial disables tokens; dev tags `dev`. Codes and character creates carry `realm_id` for Plan 3 isolation later (lists/ingests not filtered yet).

## Locked defaults

| Server | `realm.id` | `tokens.enabled-scopes` |
|--------|------------|-------------------------|
| Lobby | `main` | `[character]` |
| Main | `main` | `[skin, drink, character, skin_staff]` |
| Tutorial | `tutorial` | `[]` |
| Dev | `dev` | full list |

Repo default TFMCWeb `config.yml` keeps **full scopes** + `realm.id: main` so existing boxes do not break until operators tighten lobby/tutorial.

## What shipped

1. TFMCWeb `realm.id` + `tokens.enabled-scopes` → `TokenCommand` gate/tab + mint body `realm_id`
2. PS `codes.realm_id` / `character_creates.realm_id` (migrate default `main`)
3. Redeem + `get_session` return `realm_id`; character create stamps from Bearer session
4. Frontend session storage keeps `realm_id` on redeem (no UI chrome)

## Operator notes

See [STAGING.md](../../../STAGING.md) **Step 33**. After deploy, set lobby `enabled-scopes: [character]` and tutorial to `[]`.

## Status

**Done** (code). Operator ticks: [STAGING.md](../../../STAGING.md) Step 33.
