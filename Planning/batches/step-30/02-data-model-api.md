# Batch 30.02 — Data model + wardrobe API

**Plan + build:** Persist wardrobe per character; Bearer session CRUD like kits.

**Repos:** `ProvinceSystem/backend`  
**Depends on:** [01-planning-lock](./01-planning-lock.md) · character session auth (Step 19)

## Schema

Table `character_wardrobe_slots`:

| Column | Notes |
|--------|--------|
| `player_uuid`, `character_id`, `slot` | PK; slot = `base` \| `extra_1` \| `extra_2` \| `masked` |
| `png_relpath` | Under `data/wardrobe/` |
| `texture_value` / `texture_signature` | MineSkin (nullable until [03](./03-mineskin-sign.md)) |
| `model` | `classic` \| `slim` |
| `updated_at` | |

`character_roster.wardrobe_active_slot`: `base` \| `extra_1` \| `extra_2` \| null.

## API (session Bearer, character owner)

| Method | Path | Behaviour |
|--------|------|-----------|
| `GET` | `/characters/{id}/wardrobe` | Slots + active + `swappable_slots` |
| `POST` | `/characters/{id}/wardrobe/{slot}` | Multipart `texture`/`file` → 64×64 validate → upsert (sign stub) |
| `DELETE` | `/characters/{id}/wardrobe/{slot}` | Clear slot + PNG; fix active |
| `PATCH` | `/characters/{id}/wardrobe/active` | `{ "slot": "base"\|"extra_1"\|"extra_2"\|null }` |
| `GET` | `/characters/{id}/wardrobe/{slot}/texture` | Owner PNG preview |

### Rules (this batch)

- Unlock default: `swappable_slots = 1` until [04](./04-ranks-platform-catalog.md) (extras rejected).
- `masked` upload OK; cannot be set active.
- POST calls `sign_wardrobe_skin` stub → `signed: false` until [03](./03-mineskin-sign.md).

## Verify

- [x] Owner can CRUD own wardrobe; stranger 403  
- [x] Active cannot be `masked`  
- [x] Empty character returns empty slots + default unlocks (`swappable_slots: 1`)  

## Status

**Done** (schema + domain + routes; textures unsigned until 30.03; unlocks default until 30.04). Next: [03-mineskin-sign](./03-mineskin-sign.md).
