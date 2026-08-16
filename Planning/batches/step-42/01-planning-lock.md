# Step 42.01 — Planning lock

**Plan + docs only.** Lock capitals/settlements scope before SF export (42.02) and PS/FE batches.

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** [00-index](./00-index.md) · [map-export-schema.json](../../assets/map-export-schema.json) · [step-41/01-planning-lock](../step-41/01-planning-lock.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 8

## Authoritative spec

Full settlement gameplay and implementation rules:

**`Workspace/simplefactions/Documentation/Settlements.md`**

Summary below; if this file disagrees with `Settlements.md`, the SF doc wins.

## Locked — summary

| Area | Rule |
|------|------|
| Entity | `Settlement` on faction — `id`, `name`, `centerProvince`, `centerX/Z`, explicit `provinces` list |
| Found | `/setcapital "name"` when ≥2 land hops from any settlement centre; initial provinces = centre + eligible land neighbours |
| Join | 1 hop from centre → join existing settlement, no name; add capital province to list if missing |
| Faction capital | On existing city must be **centre province** only |
| Claim growth | New province adjacent to settlement territory → add; **random** tie-break if multiple |
| Loss | Non-centre → remove from list; centre lost → dissolve settlement |
| Dissolve | Clear all guild + faction capitals in that settlement’s provinces |
| Hygiene | `validate()` from `Faction.tick()` — strip non–directly-owned provinces; dissolve if centre invalid |
| Relocate | Last guild leaves settlement → disband; destination uses same setcapital rules |
| Export | One map marker per settlement (`centerX/Z`, name, `faction_id`) |
| SF packages | Lowercase `settlement` domain; see Settlements.md |

## Locked — SF package conventions

| Rule | Choice |
|------|--------|
| Legacy caps | May touch `Guild`, `Map`, `Faction`, `Managers` — minimal edits only |
| **New subpackages** | **Lowercase** only (`settlement`, `Map.export`) |
| Structure | Domain-first, deep tree; no flat Utils |
| New classes | Rare; `Settlement` + per-faction `Handler` |

## Locked — export contract

Sidecar `map_markers.json` per [map-export-schema.json](../../assets/map-export-schema.json). Details in Settlements.md.

## Status

**Done.**

## Next

[02-sf-settlement-core](./02-sf-settlement-core.md) → [10-docs-verify](./10-docs-verify.md) — see [00-index](./00-index.md).
