# Step 73.05 — Province index build performance

**Build:** ProvinceSystem frontend (+ optional backend)  
**Depends on:** [04-layout-overflow](./04-layout-overflow.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Speed up one-time province pick index construction so county / child-tier modes become interactive quickly on full Calavorn pick maps.

## Current cost

[`useEditorProvinceIndex.ts`](../../../frontend/app/hooks/useEditorProvinceIndex.ts):

1. `GET /{map}/editor/provinces` (catalog rows).
2. Fetch full `provinces.png` blob.
3. `getImageData` on full resolution canvas.
4. [`buildProvinceIndexFromImageData`](../../../frontend/app/lib/map/editor/buildProvinceIndex.ts) scans **every pixel** (`width × height`).

For large maps (e.g. 4096² or 6400²), this blocks the main thread for seconds.

## Options (pick one primary + optional secondary)

| Option | Pros | Cons |
|--------|------|------|
| **A. Web Worker** | Keeps UI responsive during scan | Still O(pixels); ship worker bundle |
| **B. Backend grid endpoint** | Reuse `province_id_grid.bin.gz` or JSON sparse map; O(provinces) not O(pixels) | New API + auth |
| **C. Downscaled pick image** | Smaller fetch + scan | Must preserve RGB hit-test parity |
| **D. Chunked scan + progress** | Simple; shows loading % | Still slow total time |

**Recommended:** **B** if grid exists for `main`; else **A + D** for v1, **B** as follow-up.

### B detail (if chosen)

New staff endpoint e.g. `GET /{map}/editor/province-index` returning:

- `width`, `height`, `provinceMap` as compact encoding **or** server-built `rgbToProvinceId` map only.

Auth: same as `ensure_map_staff_write`.

Frontend: skip client ImageData loop when endpoint available.

### A detail

- Move `buildProvinceIndexFromImageData` to worker module.
- `useEditorProvinceIndex` posts ImageData or raw buffer; resolves `ProvinceIndex`.
- Show "Building province index…" with optional percent.

## Deliverables

1. Document actual `provinces.png` dimensions for `main` and `dev` in batch close-out note.
2. Implement chosen approach.
3. Vitest: index build on small fixture completes; rgb lookup spot-check unchanged.
4. Remove duplicate index fetch if `MapEditorCanvas` internal hook still enabled when parent provides index (verify `pickProvidedByParent`).

## Files touched (typical)

| File | Change |
|------|--------|
| `buildProvinceIndex.ts` | Worker entry or slimmer API |
| `useEditorProvinceIndex.ts` | Async worker / new endpoint |
| `editor_routes.py` | Optional index endpoint |
| `test_*` | Regression |

## Done when

- County mode on `main`: index ready within target from 73.01 lock (< 2s on dev laptop) **or** UI shows progress and remains responsive during build.
- Province click hit-test matches pre-change behaviour on sample provinces.

## Status

**Done.** Backend `GET /{map}/editor/province-index` returns gzip `province_id_grid` bytes; frontend deserializes via `deserializeProvinceIdGrid` + `buildProvinceIndexFromGrid` with image fallback.

**Map dimensions note:** `MAP_BOUNDS` logical size is 6400×6400 ([`types.ts`](../../../frontend/app/components/map/types.ts)). Test fixture `provinces.png` is 2×2; production `main`/`dev` pick maps use full input resolution (same as `provinces.png` natural size).
