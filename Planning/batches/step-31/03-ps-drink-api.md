# Step 31.03 — ProvinceSystem drink API

**Repos:** `ProvinceSystem` backend (+ session types)

## Goal

Redeem `drink` codes; store drink submissions; texture assets + reuse; staff pending/approve/deny; entitlement flags for texture.

## Plan

1. Allow `drink` in code scopes / redeem → session (`scope=drink`, not skins upload session unless unified carefully).
2. Schema:
   - Drink submission: player UUID, slug/id, recipe JSON, status, optional `texture_id` / new upload, Discord notify fields.
   - `drink_textures`: id, owner UUID, cmd, ia_item_id, png path, refcount, created_at.
3. Submit validation: ingredients ⊆ catalog allowlist; effect blacklist; color xor texture; Noble cannot set texture; no servercommands.
4. Entitlements: `allow_drink_texture` via `drink_player_meta` (plugin PUT stub for DrinkBuilder 31.04).
5. Staff routes parallel to skins: pending list, file GET, approve, deny, notifications.
6. After approve: status `approved` or `pending_pack` if new texture needed.

## Verify

- [x] Redeem drink code → session.
- [x] Noble submit with texture → 400.
- [x] Gilded upload PNG → pending.
- [x] Reuse `existing_texture_id` → no pack wait if already applied (`approved`).

## Done when

- [x] API supports full submit → approve path without MC write yet.
