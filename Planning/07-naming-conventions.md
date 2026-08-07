# 07 — Naming conventions

Players enter an **Item name** (ArmourShop label). The technical skin id comes from **PNG file names** (and later matching JSON). The site and API enforce conventions and show clear errors when names are wrong.

Style locked: **`lowercase_snake_case`** (same family as `tfmc_armor` ids like `forestman_chain_helmet`).

## Two names per submission

| Field | Used for | Who sets it |
|-------|----------|-------------|
| **Item name** (`display_name`) | ArmourShop label, IA `display_name`, Discord embed | Player types it (spaces/capitals OK) |
| **Skin id** (`slug`, internal) | Files on disk, IA item ids, ArmourShop set key, LP | Taken from PNG basename(s) — **not** a form field for players |

Do not ask players for a “slug”. Staff Discord embeds may still show the technical id.

## Skin id rules (from file names)

- Regex: `^[a-z][a-z0-9_]{1,47}$` (2–48 chars total)
- Must start with a letter
- Only `a-z`, `0-9`, `_`
- No spaces, hyphens, capitals, dots, unicode, or leading/trailing `_`
- No double underscores `__`
- Must be unique among submissions that are `pending`, `approved`, or `applied` (denied ids may be reused)

Reserved ids: `test`, `texture`, `null`, `undefined`, `admin`, `tfmc`.

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

### `item` / `handheld` / `large_handheld`

```text
{id}.png
```

Example: `blue_knight.png`.  
Sizes: `item` / `handheld` **16×16**; `large_handheld` **32×32**.  
`large_handheld` also requires `grip_preset` (`bottom` \| `middle` \| `top`) — not in the filename.

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

Embeds show **Item name**, technical **id**, **kind**, **grip_preset** when set, plus raw PNG attachments (MVP).
