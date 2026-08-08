# 07 — Naming conventions

Players enter an **Item name** (ArmourShop label). The technical skin id comes from **PNG file names** (base id), then the API prefixes a stable **player key**.

Style locked: **`lowercase_snake_case`** (same family as `tfmc_armor` ids like `forestman_chain_helmet`).

## Two names per submission

| Field | Used for | Who sets it |
|-------|----------|-------------|
| **Item name** (`display_name`) | ArmourShop label, IA display, Discord title | Player types it (spaces/capitals OK; may match another player) |
| **Base id** (from PNG basenames) | Player upload convention | Taken from PNG basename(s) — **not** a form field |
| **Skin id** (`slug`) | Disk / IA / shop / LP | `{player_key}_{base_id}` — API adds `player_key` |

Do not ask players for a “slug”. Staff Discord embeds show names; footer may include key/slug.

## Player key

- Minted on first Discord link (`discord_links` / durable `player_keys`): 8 chars `[a-z][a-z0-9]{7}`.
- Survives unlink/re-link for the same Minecraft UUID.
- API startup backfills any linked account missing a key.

## Skin id rules

**Base id** (from files) and **full slug** (after prefix):

- Regex: `^[a-z][a-z0-9_]{1,47}$` (2–48 chars total) — full slug must still match after `{player_key}_` is prepended (shorten base id if needed).
- Must start with a letter
- Only `a-z`, `0-9`, `_`
- No spaces, hyphens, capitals, dots, unicode, or leading/trailing `_`
- No double underscores `__`
- Full slug must be unique among `pending` / `approved` / `applied` (`denied` / `revoked` may reuse)

Same player cannot submit another **active** skin with the same **base id** or same **display_name** (case-insensitive). Website checks before submit; API enforces.

Reserved base ids: `test`, `texture`, `null`, `undefined`, `admin`, `tfmc`.

## Upload filenames (required)

### `armor_set`

Labeled slots; **each file name must match**, same id on all six:

```text
{id}_helmet.png
{id}_chestplate.png
{id}_leggings.png
{id}_boots.png
{id}_layer_1.png
{id}_layer_2.png
```

Example: `blue_knight_helmet.png`, …, `blue_knight_layer_2.png`.

Exact sizes: icons **16×16**; layers **64×32**.

### `handheld` / `large_handheld`

```text
{id}.png
```

Example: `blue_knight.png`.  
Sizes: `handheld` **16×16**; `large_handheld` **32×32**.  
`large_handheld` also requires `grip_preset` (`bottom` \| `middle` \| `top`) — not in the filename.

### `bow` / `large_bow`

Four PNGs; **same `{id}` prefix** on every file (reject mismatched names):

```text
{id}.png
{id}_0.png
{id}_1.png
{id}_2.png
```

Example: `blue_shortbow.png`, `blue_shortbow_0.png`, …  
Sizes: `bow` **16×16**; `large_bow` **32×32**.

### `crossbow`

Bow four frames plus charged; same `{id}` on all five:

```text
{id}.png
{id}_0.png
{id}_1.png
{id}_2.png
{id}_charged.png
```

Example: `blue_cross.png`, …, `blue_cross_charged.png`. Size: **16×16**.

All enabled kinds also require **`base_set`** (ArmourShop BaseSet id: armor tier or applicable type filtered by kind) — not in the filename; see [step-8](./batches/step-8/00-index.md). Kind `item` is not selectable.

### `item_3d` (later)

```text
{id}.png
{id}.json
```

Same `{id}` stem on both; JSON must include required `display` keys.

### `shield` (later)

TBD with ArmourShop; one mesh; blocking display generated at apply.

## After validation (server storage)

Server still writes under `data/skins/{submission_id}/` using the validated id stems above (content from the upload bytes). Original client paths are only used for **name checks**.

## ItemsAdder / ArmourShop mapping

| Use | Pattern |
|-----|---------|
| IA armor piece ids | `{id}_helmet`, … |
| IA `armors_rendering` key | `{id}` |
| IA item id (non-armor) | `{id}` |
| ArmourShop set key | `{id}` |
| LP permission | `armourshop.submission.{id}` |

## Player-facing copy (examples)

> Item name: what ArmourShop shows (e.g. Blue Knight).  
> File names: use lowercase with underscores, e.g. `blue_knight.png` or `blue_knight_helmet.png`. If the name is wrong, the site will tell you before staff ever sees it.

## Staff Discord

Embeds show **Item name**, technical **id**, **kind**, **`base_set`**, **grip_preset** when set, plus raw PNG attachments (MVP).
