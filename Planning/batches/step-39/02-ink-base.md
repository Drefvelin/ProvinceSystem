# Step 39.02 — Ink parchment base



**Repos:** `ProvinceSystem` backend  

**Depends on:** [01-planning-lock](./01-planning-lock.md)



## Goal



Rewrite `parchmentgen.py` grade pipeline: **luminance → parchment tones + ink edge overlay**, replacing Step 38 desaturate/wash/vignette stack.



## Plan



1. **Remove / replace 38 constants** — drop aggressive `DESATURATE_FACTOR`, heavy `VIGNETTE_STRENGTH`, multiply-only texture path as primary look.

2. **Luminance remap** — greyscale from source RGB (luma `0.299R+0.587G+0.114B`); map 0–255 through `PAPER_SHADOW` → `PAPER_MID` → `PAPER_HIGH` gradient ([01-planning-lock](./01-planning-lock.md)).

3. **Contrast pass** — `ImageEnhance.Contrast` ~1.15–1.25 after remap so terrain mass reads on paper.

4. **Edge ink overlay** — edge detect on luma → threshold → composite `INK_DARK` at tunable opacity on remapped base.

5. **Paper grain** — keep `paper_texture.png`; blend mode **soft-light** or **overlay** at low opacity (~0.12–0.18), not multiply-at-0.25.

6. **Vignette** — optional edge stain only; cap `VIGNETTE_STRENGTH` at **0.12–0.15** or remove if edges still read foggy.

7. **Validation** — same `map.png` / `provinces.png` size checks as 38.02; still never write to `input/`.



## Build



| File | Action |

|------|--------|

| `backend/src/scripts/mapgen/parchmentgen.py` | rewrite `_grade_parchment` + helpers (`_luminance`, `_remap_levels`, `_ink_edges`, `_apply_grain`) |

| `backend/src/scripts/mapgen/test_parchmentgen.py` | create — unit tests for remap endpoints + output mode RGB |

| `backend/src/assets/map/paper_texture.png` | keep; optional tune if grain too strong on cream base |



## Tunables (shipped in 39.02)



```python

EDGE_OPACITY = 0.55

EDGE_THRESHOLD = 28

CONTRAST_FACTOR = 1.28   # bumped in 39.03 revision (was 1.2)

GRAIN_BLEND = 0.15

VIGNETTE_STRENGTH = 0.12

```



Grain uses neutralized multiply (texture blended 50% toward mid-gray before low-opacity multiply-blend).



## Visual acceptance



| Check | Pass when |

|-------|-----------|

| No green cast | `/map/main` base reads cream/brown, not Minecraft biome green |

| Coastlines | Visible brown/black lines without hover |

| Interior | Forest/hill mass distinguishable as darker brown washes |

| Not foggy | Midtones not milky grey; compare side-by-side with 38 v1 screenshot |

| Performance | `create_parchment_base('main')` completes in similar time to 38 (~seconds on 4096²) |



## Verify



- [x] `create_parchment_base('main')` overwrites `output/main/maps/parchment_base.png` (~21.9 MB)

- [x] Output hash/size differs from 38 wash (~25.7 MB prior)

- [x] `map.png` on disk unchanged

- [x] Missing `map.png` skip behaviour preserved (38 validation path)

- [x] Unit tests: `python -m unittest src.scripts.mapgen.test_parchmentgen` (4 tests)

- [ ] Operator spot-check: Calavorn coasts, rivers, Nimbus island edges readable



## Operator workflow



1. No new input files — same `input/{map}/map.png`.

2. Run `create_parchment_base('{map}')` or **fullregen** for `main` (and `dev` if used).

3. Restart backend if running without `--reload`; hard-refresh `/map/main`.



## Status



**Done** (39.02 code). Operator visual pass recommended before 39.03.



## Out of scope



Earth-tone nation fills ([03-earth-tone-fills](./03-earth-tone-fills.md)); borders ([04-adaptive-borders](./04-adaptive-borders.md)).


