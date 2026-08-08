# 07 — Naming conventions

Players enter an **Item name** (ArmourShop label). The technical submission id is derived by the **API** from the player's linked **Minecraft IGN** plus the item name — never from upload filenames and never a random UUID.

Style locked: **`lowercase_snake_case`** (same family as `tfmc_armor` ids like `forestman_chain_helmet`).

## Two names per submission

| Field | Used for | Who sets it |
|-------|----------|-------------|
| **Item name** (`display_name`) | ArmourShop label, IA display, Discord title | Player types it (spaces/capitals OK; may match another player) |
| **Submission id** (`id` == `slug`) | Disk / IA / shop / LP / delete / tab-complete | API builds it: `{sanitized_ign}_{slugify(display_name)}` |

Do not ask players for a "slug" or an id. Staff Discord embeds show the human id directly (e.g. `drefvelin_blue_knight`), plus Minecraft/Discord names — never a UUID.

## Submission id (was: player key + base id)

- **No `player_key`.** The old mint/backfill/`player_keys` system is gone; `discord_links.player_key` is no longer written. (A legacy `player_key` column may still exist on disk from old migrations — SQLite can't cleanly `DROP COLUMN`; it is simply unused.)
- **IGN source:** `discord_links.minecraft_name`, captured at submit time and sanitized to `[a-z0-9_]+` (lowercased, non-alnum runs collapsed to `_`, leading digit gets a `p_`/`skin_` guard, capped to 16 chars). Frozen into the id at creation — a later IGN change only affects **new** submissions, not existing ones.
- **Item name → slug fragment:** `slugify_display_name` lowercases, collapses separators to `_`, and caps length so the combined id fits the 48-char rule.
- **Full id:** `{sanitized_ign}_{slugify(display_name)}`, e.g. IGN `Drefvelin` + item name `Blue Knight` → `drefvelin_blue_knight`. This one string is the API `id`, the `slug` (identical — no separate field), the pack/shop family key, the delete/tab-complete token, and the Discord embed id.

## Skin id rules

- Regex: `^[a-z][a-z0-9_]{1,47}$` (2–48 chars total).
- Must start with a letter
- Only `a-z`, `0-9`, `_`
- No spaces, hyphens, capitals, dots, unicode, or leading/trailing `_`
- No double underscores `__`
- Must be unique among `pending` / `approved` / `applied` (`denied` / `revoked` may reuse)

Same player cannot submit another **active** skin with the same **display_name** slug (case-insensitive) — which also means the same resulting id, since the IGN prefix is fixed per player. Different IGNs naturally produce different ids even with the same item name. Website checks before submit; API enforces.

Reserved ids: `test`, `texture`, `null`, `undefined`, `admin`, `tfmc`.

## Upload filenames (ignored for identity)

Filenames are **freeform** — the API only validates PNG magic bytes, max size, and exact pixel dimensions per slot. It never reads the upload filename to derive an id; server-side stems always come from the submission id (and tier, for armor).

### `armor_set` (multi-tier)

One submission holds **1–6 tiers** from the allowlist `iron | steel | abyssalite | mythril | mage | infantry`. Each tier needs all six multipart fields:

```text
{tier}_helmet
{tier}_chestplate
{tier}_leggings
{tier}_boots
{tier}_layer_1
{tier}_layer_2
```

Plus a form field `tiers` — a JSON array, e.g. `["iron","steel"]`. The uploaded **filenames** can be anything (`foo.png`, `my_texture_final.png`, …); only the field name matters. Server writes fixed disk stems `{tier}_helmet.png`, …, under `data/skins/{id}/`.

Exact sizes: icons **16×16**; layers **64×32**.

**Unique textures:** every PNG in a submission must have distinct upload bytes (SHA-256 of the file). Re-uploading the same file for two slots or two tiers is rejected.

*Legacy single-tier path:* unprefixed fields (`helmet`, `chestplate`, …) plus `base_set` are still accepted and mapped onto a single tier (named by `base_set`, default `iron`) for backward compatibility. Prefer the multi-tier `tiers` + prefixed-field form for anything new.

### `handheld` / `large_handheld`

One `texture` field, freeform filename. Server writes `{id}.png`.

Sizes: `handheld` **16×16**; `large_handheld` **32×32**.
`large_handheld` also requires `grip_preset` (`bottom` \| `middle` \| `top`) — a form field, not derived from anything filename-related.

### `bow` / `large_bow`

Fields `texture`, `pull_0`, `pull_1`, `pull_2` (freeform filenames). Server writes:

```text
{id}.png
{id}_0.png
{id}_1.png
{id}_2.png
```

Sizes: `bow` **16×16**; `large_bow` **32×32**.

### `crossbow`

Bow four fields plus `charged`. Server writes:

```text
{id}.png
{id}_0.png
{id}_1.png
{id}_2.png
{id}_charged.png
{id}_arrow.png
```

Size: **16×16**.

All enabled non-armor kinds also require **`base_set`** (ArmourShop BaseSet id: type filtered by kind) — a form field, not derived from filenames; see [step-8](./batches/step-8/00-index.md). Kind `item` is not selectable. Armor uses `tiers` instead of `base_set` (`base_set` is null/unused for `armor_set`).

### `item_3d` (later)

```text
{id}.png
{id}.json
```

Same `{id}` stem on both; JSON must include required `display` keys.

### `shield` (later)

TBD with ArmourShop; one mesh; blocking display generated at apply.

## After validation (server storage)

Server writes under `data/skins/{submission_id}/` using fixed stems derived from the submission id (and tier, for armor) — never from the client's original filenames. `meta.json` in that folder records `id`, `slug`, `kind`, `tiers`, `base_set`, etc.

## ItemsAdder / ArmourShop mapping

| Use | Pattern |
|-----|---------|
| IA armor piece ids (per tier) | `{id}_{tier}_helmet`, … |
| IA `armors_rendering` key (per tier) | `{id}_{tier}` |
| IA item id (non-armor) | `{id}` |
| ArmourShop set key, non-armor | `{id}` |
| ArmourShop set key, armor (per tier) | `{id}_{tier}` |
| LP permission (shared across tiers) | `armourshop.submission.{id}` |

## Player-facing copy (examples)

> Item name: what ArmourShop shows (e.g. Blue Knight).
> Upload any PNG file — the name doesn't matter, just make sure it's the right size for that slot.

## Staff Discord

Embeds show the human **Submission id** prominently, **Item name**, **kind**, **Tiers** (armor) or **Base set** (non-armor), **grip_preset** when set, **Minecraft** and **Discord** names (never raw MC UUID or Discord snowflake as a field), **Colours** / **Apply name** when relevant, plus raw PNG attachments including a generated **`name_preview.png`** (coloured display name for staff).

## Name colours vs Apply name

- **`name_colours` / `name_styles`** — how the SkinSet display name looks in ArmourShop (shop YAML `colour` / `styles`). Independent of apply-name.
- **`add_name`** — when applying the skin in-game, keep the base item’s existing name on the skinned piece. Does **not** gate colours.
