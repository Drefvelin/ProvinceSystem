# Batch 16.02 — Reliable JSON model render

**Repo:** `ProvinceSystem` frontend

Spike + module: load one Java item model `File` (JSON) + one texture `File` (PNG) into a WebGL canvas. Show cubes with correct per-face UVs and nearest-neighbour filtering. Auto-frame; dispose on unmount. Fixture smoke with a known good model.

Prefer a Minecraft JSON renderer (or thin Three.js) over bbmodel-only tools.

Upload form shows the preview when both a model JSON and texture PNG are selected (`item_3d` / `shield` / `helmet_3d`, armor 3D helmet per tier, gun texture + first of aim/carry/reload).

**Non-goals (later batches):** `display` transforms; kind variant UI; player mannequin.

**Done when:** A local fixture (or picked files) renders the textured model alone without broken UVs or leaks.

**Status:** Done — `lib/skins/javaModel.ts` + `ModelPreview` wired into `UploadForm` (Three.js).
