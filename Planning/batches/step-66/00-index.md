# Step 66 — War campaign map (route + battles)

**Repos:** SF + PS (FE) · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [70](../step-70/00-index.md) (dual-leg schedules), [58](../step-58/00-index.md) (campaign axis), [42](../step-42/00-index.md) (map markers pipeline)  
**Next:** [71](../step-71/00-index.md) (inter-battle raids)

## Goal

Show active campaign wars on the **web map**: a **smooth dotted campaign line** (outlined stroke) along the full axis from attacker capital to defender objective, plus **`battle.png` pins** at every scheduled battle province with hover tooltips (battle kind + status).

| In scope | Out of scope |
|----------|--------------|
| SF `wars[]` export in `map_markers` upload (route + battle slots) | Occupation zone tint (step 68 + [44](../step-44/00-index.md)) |
| PS schema + API passthrough of `wars[]` | Chronicle `events[]` export |
| FE SVG smooth campaign line layer | Raid war route (step 67) |
| FE battle markers + hover (`battle.png`) | Inter-battle raids (step 71) |
| Active-leg "next battle" highlight on line/markers | Declare codes (step 69) |
| Docs + tests | Live-war migration tooling |

## Target UX

```text
[atk capital] ~~~smooth dotted line~~~ [border] ~~~ ... ~~~ [objective]
                    ⚔ battle pins at schedule provinces (both legs)
```

- Line follows `campaign_provinces[]` geography via **smoothed spline** through waypoints (not straight chord, not sharp centroid polyline).
- Stroke: **dotted fill** with **solid outline/border** (readable on parchment).
- Battle pin hover: display name (e.g. `Siege`, `Naval Invasion`), leg, province label, status (`upcoming` / `next` / `fought`).
- Occupation bulge tint deferred; players can still see **where** the war is and **where battles land**.

## Batches

| Batch | Doc | Repo | Status |
|-------|-----|------|--------|
| **66.01** | [01-planning-lock.md](./01-planning-lock.md) | Both | **done** (2026-08-23) |
| **66.02** | [02-sf-wars-export.md](./02-sf-wars-export.md) | SF | **done** (2026-08-23) |
| **66.03** | [03-ps-schema-passthrough.md](./03-ps-schema-passthrough.md) | PS | **done** (2026-08-23) |
| **66.04** | [04-fe-campaign-line.md](./04-fe-campaign-line.md) | PS FE | **done** (2026-08-23) |
| **66.05** | [05-fe-battle-markers.md](./05-fe-battle-markers.md) | PS FE | **done** (2026-08-23) |
| **66.06** | [06-docs-verify.md](./06-docs-verify.md) | Both | **done** (2026-08-23) |

## Status

**Step 66 complete** (2026-08-23). **Next:** [step 71 inter-battle raids](../step-71/00-index.md).

## Note on build order

This step **replaces** the old step 66 slot (inter-battle raids, now [71](../step-71/00-index.md)) and **front-loads** the campaign-route slice of old step 68 (war map export). Step **68** remains for occupation lists, chronicle hooks, and full `wars[]` completeness after route ships.
