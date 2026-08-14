# Step 39 — Paradox curved labels

**Repos:** `ProvinceSystem` backend  
**Depends on:** [step-38](../step-38/00-index.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 4

## Goal

Backend-generated curved nation names across each contiguous territory blob (Paradox / GSG style), composited as a label layer with zoom-tier visibility.

## Locked rules

| Piece | Choice |
|-------|--------|
| Components | One label per connected province component per nation |
| Placement | Curve along medial axis / longest internal chord of blob |
| Renderer | Spike Cairo/Skia or SVG→raster (Pillow alone insufficient) |
| Collisions | Tier priority (Kingdom > Duchy > …); hide small blobs at low zoom |
| Output | `labels_{mode}.png` or per-blob crops with bbox metadata |

## Batches (when step starts)

1. **01-planning-lock**  
2. **02-label-spike** — Single nation proof of curved text  
3. **03-component-graph** — Connected components per nation  
4. **04-full-pipeline** — All nations + collision rules  
5. **05-frontend-layer** — Label layer + zoom thresholds  
6. **06-docs-verify** — STAGING Step 39  

## Status

**Planned.**
