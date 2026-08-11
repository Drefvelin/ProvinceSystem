# Batch 20.02 — Kit cooldown sync + create warnings (web + in-game)

**Plan + build:** Push kit cooldown / eligibility with roster (or player meta) so ProvinceSystem and both create UIs share one truth. Warn before create when the player would not receive a kit.

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `frontend`  
**Depends on:** [01-kit-yml-and-grant](./01-kit-yml-and-grant.md)

## Locked UX

Copy intent (no em dash punctuation in player-facing strings):

> You have to wait X hours to create a character otherwise you will not receive a kit.

- Show **remaining hours** (ceil to whole hours is fine; or hours+minutes if already easy).
- Surfaces: **in-game** create flow (before confirm / on open create) and **website** `/character` create entry (list CTA and/or wizard start).
- Same rule both sides: if `cooldown_remaining_seconds > 0`, creating now marks the new character **kit-ineligible**.

## Plan

1. **RPC → API** — Extend roster (or `character_player_meta`) push with e.g.:
   - `kit_cooldown_seconds_remaining` (int, 0 if clear)
   - `kit_cooldown_hours` (config echo, optional)
   - Per character on roster rows: `kit_status`: `granted` | `eligible` | `ineligible` | `pending` (pick a small enum; document in API)
2. **ProvinceSystem** — Store meta on existing roster/meta tables; expose on `GET /characters` (and/or session-scoped meta endpoint already used for slots).
3. **Frontend** — If remaining > 0, show the wait warning on create entry + wizard; do **not** block create (player may still create; they just will not get a kit). Optional: secondary confirm “Create anyway”.
4. **In-game** — Same warning when opening / confirming create while cooling down.
5. **Refresh** — Cooldown meta updates on roster push (join, grant, create, periodic if already present). Web Refresh / existing poll should pick it up.

## Verify

- [x] After a kit grant, web list/create shows remaining ~48h warning *(roster push + list meta; operator smoke after deploy)*  
- [x] In-game create shows the same remaining window *(initiateCreation + summary confirm)*  
- [x] Create anyway → character `kit_ineligible`; join does not grant *(20.01 stamp)*  
- [x] When remaining hits 0, warning disappears both sides after next sync  
- [x] Character that received kit shows granted status (list optional; meta must be correct)  

## Implemented

- Roster push: `kit_cooldown_seconds_remaining`, `kit_cooldown_hours`, per-row `kit_status`; push after grant
- API meta + `GET /characters` kit fields; roster `kit_status` column
- Web list + wizard non-blocking wait-X-hours banner
- In-game open create + summary confirm warnings

## Out of scope

Lore-item editor; changing kit contents; staff approve flows.
