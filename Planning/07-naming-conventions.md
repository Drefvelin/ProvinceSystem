# 07 — Naming conventions

Players do not know (or follow) pack conventions. The site and API **enforce** technical names. Display names can be friendly; file names and ItemsAdder ids cannot.

Style locked: **`lowercase_snake_case`** (same family as existing `tfmc_armor` ids like `forestman_chain_helmet`).

## Two names per submission

| Field | Used for | Allowed |
|-------|----------|---------|
| **display_name** | ArmourShop label, IA `display_name`, Discord embed | Spaces, punctuation; length-capped. Not used as path/id. |
| **slug** | Files, IA item ids, ArmourShop set key, LP node | Strict regex only |

Players may type a display name; UI auto-slugifies then **shows the slug for confirmation**. They may edit the slug, but it must pass validation before submit.

## Slug rules

- Regex: `^[a-z][a-z0-9_]{1,47}$` (2–48 chars total)
- Must start with a letter
- Only `a-z`, `0-9`, `_`
- No spaces, hyphens, capitals, dots, unicode, or leading/trailing `_`
- Must be unique among submissions that are `pending`, `approved`, or `applied` (denied slugs may be reused)

### Reject examples

| Input | Why |
|-------|-----|
| `texture` / relying on upload name `texture.png` | Generic; upload names are ignored anyway |
| `My Skin` | Spaces, capitals |
| `BlueKnight` | Capitals |
| `blue-knight` | Hyphen |
| `blue knight` | Space |
| `1cool_armor` | Must start with a letter |
| `_blue` | Leading underscore / must start with letter |
| `blue__knight` | Allowed by regex but **discourage**; prefer single `_` — reject double underscore in UI |
| Empty / one character | Too short |

Also reject reserved slugs: `test`, `texture`, `null`, `undefined`, `admin`, `tfmc`, and any slug already used by curated packs if you maintain a blocklist.

## Upload filenames

**Ignored completely.** Clients may send `blob` or `IMG_1234.PNG`. Server writes only fixed stems:

### `armor_set`

```text
{slug}_helmet.png
{slug}_chestplate.png
{slug}_leggings.png
{slug}_boots.png
{slug}_layer_1.png
{slug}_layer_2.png
```

Form fields (suggested names): `helmet`, `chestplate`, `leggings`, `boots`, `layer_1`, `layer_2`.

Exact sizes (API reject otherwise): icons **16×16**; layers **64×32**.

### `item` / `handheld` / `large_handheld`

```text
{slug}.png
```

Field: `texture`.  
Sizes: `item` and `handheld` **16×16**; `large_handheld` **32×32**.  
`large_handheld` also requires form/body field `grip_preset` (`bottom` \| `middle` \| `top`) — stored in DB/`meta.json`, **not** in the filename.

(`item_2d` is retired; use the three kinds above.)

### `item_3d` (later)

```text
{slug}.png
{slug}.json
```

Fields: `texture`, `model`. JSON must include required `display` keys (see [05](./05-skins-system.md) / [10](./10-armourshop-itemsadder.md)).

### `shield` (later)

Model + texture stems TBD with ArmourShop; one mesh; blocking display is **generated at apply**, not a second upload filename.

## Derived identifiers

| Surface | Pattern |
|---------|---------|
| IA namespace | `tfmc_submissions` |
| IA armor piece ids | `{slug}_helmet`, `{slug}_chestplate`, `{slug}_leggings`, `{slug}_boots` |
| IA `armors_rendering` key | `{slug}` |
| IA item id (all non-armor kinds) | `{slug}` |
| Full item ref | `ia.tfmc_submissions:{id}` |
| ArmourShop set key | `{slug}` |
| LP permission | `armourshop.submission.{slug}` |
| Texture path (armor icons) | `armor_icons/{slug}_helmet` (etc.) |
| Layer paths | `armor_layers/{slug}_layer_1`, `armor_layers/{slug}_layer_2` |

## Auto-slugify (UI helper)

Pseudocode for suggesting a slug from display name:

```text
s = display_name.lower()
s = replace non [a-z0-9] with _
s = collapse multiple _ to one
s = strip leading/trailing _
if s empty or starts with digit: prefix "skin_"
if len < 2: reject
if len > 48: truncate to 48, strip trailing _
if not match regex: show error, do not submit
```

Always show the result and require explicit confirm if the user did not type the slug themselves.

## API validation (server must re-check)

```text
function assertSlug(slug):
  if not regex.fullmatch(r"[a-z][a-z0-9_]{1,47}", slug): raise 400
  if "__" in slug: raise 400
  if slug in RESERVED: raise 400
  if slugTaken(slug): raise 409
```

Never trust client-provided destination filenames. Build paths only from `submission_id` + validated `slug` + fixed suffixes.

## Staff / Discord

Embeds show **display_name**, **slug**, **kind**, and **grip_preset** when set, plus the **review PNG sheet**. Deny reason can mention art / hold / display issues; naming and wrong pixel sizes should not reach staff — blocked at upload.

## Player-facing copy (suggested)

> Technical name (slug): lowercase letters, numbers, and underscores only. Example: `blue_knight`. No spaces or capitals. Your uploaded file names do not matter — use the labeled slots for helmet, chestplate, layers, etc.
