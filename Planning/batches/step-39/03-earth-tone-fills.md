# Step 39.03 — Faithful hue + parchment wash nation fills



**Repos:** `ProvinceSystem` backend  

**Depends on:** [02-ink-base](./02-ink-base.md) (visual pass on ink base; can develop in parallel after 39.01)



## Goal



Nation hover overlays and drill-visible region PNGs use **muted faithful washes** — server RGB hues preserved (blue stays blue, red stays red) while desaturating and lightness-mapping for ink parchment. Political layers read as **watercolour on parchment**, not ochre-band fog.



**Revision (operator feedback):** v1 earth-band remap (`EARTH_HUE_PULL` + 25–55° clamp) made most nations yellow; Nimbus `(59,53,211)` read yellow, Drakhanate `(111,0,0)` read orange. Replaced with `parchment_wash_rgb` — hue kept, optional warm pull for greens only.



## Plan



1. **Rewrite `display_colour.py`**:

   - `parchment_wash_rgb(rgb)` — keep original hue; desaturate + lightness-map + optional parchment blend

   - `display_rgb(rgb)` → `parchment_wash_rgb(rgb)`

   - `hover_rgb(rgb)` — same hue family, +lightness / slight saturation for hover PNGs

2. **Hue mapping** — convert to HSL; **keep hue** (no earth-band clamp). Optional `WARM_HUE_PULL` for greens (~80°–160°) only.

3. **`regiongen.py`** — no structural change; continues calling `display_rgb` / `hover_rgb` for all painted pixels

4. **Pick safety audit** — re-run / extend `test_display_colour.py`; confirm `create_map` pick path untouched

5. **Full regen** — required for all region PNGs after deploy



## Build



| File | Action |

|------|--------|

| `backend/src/scripts/util/display_colour.py` | parchment-wash transform + updated constants |

| `backend/src/scripts/util/test_display_colour.py` | hue-fidelity assertions (Nimbus, Drakhanate); remove earth-band tests |

| `backend/src/scripts/mapgen/regiongen.py` | verify imports only (unless parchment sample blend lands) |



## Shipped constants (39.03 revision)



```python

PAPER_HIGH = (240, 230, 210)

WARM_HUE_PULL = 0.12          # greens only; blues/reds untouched

SATURATION_SCALE = 0.50

FILL_SATURATION_MAX = 0.48

FILL_LIGHTNESS_MIN = 0.42

FILL_LIGHTNESS_MAX = 0.58

PARCHMENT_BLEND = 0.08

```



## Optional (defer if slow)



- `blend_toward_parchment(rgb, parchment_sample)` — 10–15% blend toward bbox median from `parchment_base.png` during regiongen paint



## Visual acceptance



| Check | Pass when |

|-------|-----------|

| On ink base | Nations read as translucent washes, not green/red blobs |

| Nimbus `(59,53,211)` | Hover reads **blue/purple**, not yellow (`B > R`, `B > G`) |

| Drakhanate `(111,0,0)` | Reads **dark red**, not orange (`R > G`, `R > B`) |

| Adjacent nations | Side-by-side hues distinct by hue family |

| Hover | Clearly brighter than base fill, same family |

| Pick | Tooltip + drill unchanged at province edges |



## Verify



- [x] `parchment_wash_rgb` + `display_rgb` / `hover_rgb` in `display_colour.py`

- [x] Unit tests: `python -m unittest src.scripts.util.test_display_colour` (9 tests)

- [x] `fullregen` for `main` completes (~6–8 min on 4096²)

- [x] `regiongen.py` unchanged (imports `display_rgb` / `hover_rgb` only)

- [x] Pick path unchanged (`mapgen.py` does not call `display_colour`)

- [ ] Operator spot-check: faithful washes on `/map/main` hover + drill (re-verify after revision)



## Status



**Done** (39.03 revision code). Operator visual pass required after fullregen.



## Out of scope



Adaptive borders ([04-adaptive-borders](./04-adaptive-borders.md) — done); frontend opacity ([05-frontend-opacity](./05-frontend-opacity.md)).

