# Step 41.03 — Profile session + staff permission

**Repos:** `ProvinceSystem` backend · `Workspace/tfmcweb` (config)  
**Depends on:** [02-ps-map-registry](./02-ps-map-registry.md) · [step-32/00-rpc-player-meta](../step-32/00-rpc-player-meta.md)

## Goal

Wire staff map access to profile Bearer session and `permission_flags` from `rpc_player_meta`; add TFMCWeb `sync-permissions` for `tfmc.map.staff`.

## Build

| File | Action |
|------|--------|
| [`backend/src/characters/rpc_player_meta.py`](../../../backend/src/characters/rpc_player_meta.py) | Add `has_map_staff_access(player_uuid, realm_id, permission_node)` |
| [`backend/src/api/map_access.py`](../../../backend/src/api/map_access.py) | Use helper; permission lookup on **session `realm_id`**, not map registry `realm_id` |
| [`Workspace/tfmcweb/src/main/resources/config.yml`](../../../../Workspace/tfmcweb/src/main/resources/config.yml) | Add `tfmc.map.staff` under `player-meta.sync-permissions` |
| [`backend/src/characters/test_rpc_player_meta.py`](../../../backend/src/characters/test_rpc_player_meta.py) | `has_map_staff_access` unit tests |
| [`backend/src/api/test_map_access.py`](../../../backend/src/api/test_map_access.py) | Session-realm permission tests |

### Permission lookup (locked)

| Piece | Rule |
|-------|------|
| LP node | `tfmc.map.staff` — network-global LuckPerms permission |
| Meta storage | Per `(player_uuid, realm_id)` on whichever TFMCWeb box the player joined |
| Map gate | Uses **character session `realm_id`** (from profile redeem), not map registry `realm_id` |
| Map registry `realm_id` | SF `mapRef` / data-folder alignment only |

Staff who join lobby (realm `main`) sync `permission_flags` to `main`; profile redeem carries `realm_id: main`; `dev` map access checks that row even though the map id is `dev`.

### TFMCWeb config

```yaml
player-meta:
  sync-permissions:
    - rulequiz.completed
    - tfmc.map.staff
```

No Java changes — `EntitlementResolver` already snapshots listed LP nodes on join.

### Operator flow

1. Grant `tfmc.map.staff` via LuckPerms (staff group or direct node).
2. Deploy TFMCWeb with updated `sync-permissions` on **lobby + survival**.
3. Staff joins once (or `/web syncmeta` while online).
4. Staff redeems profile character code on website.
5. Verify `GET /characters/player-meta` → `permission_flags.tfmc.map.staff: true`.
6. `GET /dev/data/nation` with Bearer → 200; anonymous → 403.

## Verify

```bash
cd backend/src
python -m unittest characters.test_rpc_player_meta api.test_map_access -v
```

- [x] `has_map_staff_access` unit tests pass
- [x] Main-realm session grants `dev` map when flag present
- [x] TFMCWeb `config.yml` includes `tfmc.map.staff`
- [ ] Staging: staff join + redeem → `GET /dev/data/nation` 200 with Bearer

## Out of scope

- Frontend nav + Bearer on map fetches ([04-frontend-gate](./04-frontend-gate.md))
- STAGING batch sign-off ([05-docs-verify](./05-docs-verify.md))

## Status

**Done.**

## Next

[04-frontend-gate](./04-frontend-gate.md).
