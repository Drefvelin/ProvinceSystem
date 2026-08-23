# Step 74.02 — Precomputed grid only

**Build:** ProvinceSystem backend + frontend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

`GET /{map}/editor/province-index` reads only `defines/{map}/province_id_grid.bin.gz`. No on-demand numpy rebuild. Editor hook has no image-scan fallback.

## Deliverables

### Backend

[`editor_routes.py`](../../../backend/src/api/editor_routes.py): file-only read; 404 with `build_province_id_grid` script hint if missing.

### Frontend

[`useEditorProvinceIndex.ts`](../../../frontend/app/hooks/useEditorProvinceIndex.ts): grid-only path; surfaces API `detail` on failure.

### Admin script (when provinces change)

```bash
cd ProvinceSystem/backend
python -m scripts.tools.build_province_id_grid --map main
```

Copy to SF `Input/province_id_grid.bin.gz` only when provinces change ([step-54](../step-54/03-sf-province-grid.md)).

## Done when

- Endpoint never calls `build_province_id_map` on request.
- Hook has no image fallback.
- Tests pass.

## Status

**Done.**
