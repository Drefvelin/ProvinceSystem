# Step 42.01 — Planning lock

> **Superseded for settlement territory rules by [step-53/01-planning-lock](../step-53/01-planning-lock.md)** (2026-08-18). Step 42 remains valid for map export, markers, and package conventions.

**Plan + docs only.** Lock capitals/settlements scope before SF export (42.02) and PS/FE batches.

**Repos:** `Workspace/simplefactions` · `ProvinceSystem`  
**Depends on:** [00-index](./00-index.md) · [map-export-schema.json](../../assets/map-export-schema.json) · [step-41/01-planning-lock](../step-41/01-planning-lock.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 8

## Authoritative spec

Full settlement gameplay and implementation rules:

**`Workspace/simplefactions/Documentation/Settlements.md`**

Summary below; if this file disagrees with `Settlements.md`, the SF doc wins.

## Locked — summary

Settlement **territory, founding, join, claim growth, and hop-distance** rules are superseded by [step-53/01-planning-lock](../step-53/01-planning-lock.md). One settlement is exactly one province.

| Area | Rule |
|------|------|
| Entity | `Settlement` on faction — `id`, `name`, `centerProvince`, `centerX/Z`, `provinces` |
| Territory | **Step 53:** `provinces = { centerProvince }` only — see Settlements.md |
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
