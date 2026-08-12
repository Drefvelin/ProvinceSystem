# Batch 26.01 — Plugin kit-skin sync

**Repos:** RPC · ProvinceSystem backend  

## Locked

| Piece | Choice |
|-------|--------|
| Route | `PUT /characters/plugin/kit-skins/{name}` |
| Body | Raw PNG |
| Disk | `assets/kit_skins/{name}.png` |

## Done

- PS `store_plugin_kit_skin` + plugin PUT route (sanitize stem; PNG magic; atomic write)
- RPC `ProvinceSystemClient.putKitSkin` + post-catalog sync of distinct editable `skin_png` stems from `getDataFolder()/assets/`
- Fail-soft missing/HTTP failures; monorepo path remains local-only fallback

## Status

**Done.**
