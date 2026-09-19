# Vehicle preview audit

Internal implementation evidence, 2026-09-11. This document is not player guide content.

## Scope and result

The catalogue uses 21 canonical base geometries and 16 texture variants. Eleven optional skin previews have no corresponding files in the supplied ModelEngine or ItemsAdder trees and remain unavailable.

All 21 base models were visually inspected in the actual application at `http://127.0.0.1:3000/wiki/vehicles/<slug>`, using one collaborative browser tab. They have coherent vehicle silhouettes, complete visible textures and centered framing. All five major families were included: land vehicles, trains, ships, aircraft and artillery. Fifteen of the 16 optional texture variants were also captured. The final Monoplane Pirate capture timed out in the browser automation tool; its source texture, UV mapping and unchanged base geometry are covered by the automated catalogue audit.

- [All 21 base vehicles, browser captures](evidence/vehicle-models/base-catalogue.png)
- [15 texture variants, browser captures](evidence/vehicle-models/skin-variants.png)
- Individual unmodified canvas captures are saved as WebP files in the same evidence directory. The contact sheets crop transparent margins, scale the captures and place them on a light background for inspection.

The rendered catalogue contains 3,958 visible cubes and 23,320 textured faces. 2,057 cubes inherit nonzero parent rotations. Every supplied vehicle source contains cuboids; there are no omitted mesh elements. Hidden hitboxes, point-sized helpers and faces with no assigned texture are excluded deliberately.

## Confirmed causes and fixes

1. The converter retained parent rotations only for a group named `guncircle`. This flattened hull sections, wheel and barrel rings, rigging, suspension and other geometry throughout the catalogue. All static ancestors are now retained, with no group-name exceptions and no animation keyframes.
2. Blockbench 5 stores group properties separately in `groups[]`; Small Car's outliner contains UUID references rather than embedded transform properties. The converter now resolves this table as well as the earlier embedded format.
3. The viewer interpreted compound angles as XYZ. Blockbench uses ZYX for these free models. The converted rotation records explicitly declare ZYX; existing single-axis and default XYZ callers retain their behavior.
4. The old global project UV grid was incompatible with mixed texture slots. Every model has now been regenerated with each texture's `uv_width` and `uv_height`, including Wooden Cart's nonzero texture keys and Cruiser's reordered texture slots.
5. The viewer rotated face UVs in the opposite direction to Blockbench. Correcting the clockwise slot permutation fixes 595 quarter-turn Behemoth faces and 89 Cloudskimmer faces. Reversed UV endpoints remain mirrored.
6. Skin selection loaded separate model geometry. It now loads the base model URL with skin PNGs and, where required, texture-coordinate overrides keyed to canonical cube UUIDs. The biplane's unchanged turret texture is shared. Variant assets contain no vertices, rotations or bones.

## Source semantics

Primary reference implementation:

- [Blockbench 4.10.4 NodePreviewController](https://github.com/JannisX11/blockbench/blob/v4.10.4/js/outliner/outliner.js): ZYX rotations and a node's local translation of `origin - parent.origin`.
- [Blockbench 4.10.4 cube renderer](https://github.com/JannisX11/blockbench/blob/v4.10.4/js/outliner/cube.js): cube-local coordinates, per-texture UV grids and the quarter-turn UV permutation `[2, 0, 3, 1]`.
- [Blockbench current format definition](https://github.com/JannisX11/blockbench/blob/master/js/io/format.ts): default ZYX Euler order.

Local inputs, read only:

- `C:/Users/MSI/Desktop/plugins/VehicleFramework/vehicles/*.yml`: all 21 top-level model IDs match the converter catalogue.
- `C:/Users/MSI/Desktop/plugins/ModelEngine/blueprints/**/*.bbmodel`: source geometry, static hierarchy, embedded PNGs and texture grids.
- A recursive filename search in ModelEngine and ItemsAdder found no assets for the 11 unavailable skin names.

## Regression coverage

Command from `frontend/`:

```text
npx vitest run app/wiki/vehicles/vehicleSource.test.ts app/wiki/vehicles/vehicles.test.ts
```

Result: 12 tests pass. Coverage includes:

- A committed source-derived transform fixture from every base model family, so native scene-graph comparisons run without the external plugin tree.
- When the local source tree is available, every visible source cube, ancestor transform, face texture ID, normalized/rotated/mirrored UV and embedded PNG is compared with the generated catalogue.
- Reference geometry uses an independent Three.js Object3D hierarchy with native local pivots, not the converter's flattened rotation implementation.
- All 16 skin variants preserve base vertex and normal buffers exactly and use the corresponding source artwork coordinates.
- All 21 detail pages publish one viewer; the index publishes none. All 48 configured skin choices remain present, with 37 available previews and 11 unavailable choices.
- A live browser selection of unavailable Biplane Prism showed zero canvases and the text `Biplane (Prism): preview unavailable.` Available skin changes showed exactly one canvas.

The shared production build and server lifecycle were handled by the coordinating UI agent. `StationModelViewer.tsx` was not changed.

## Per-model generated coverage

| Base ID | Cubes | Textured faces | Cubes with parent rotations |
|---|---:|---:|---:|
| aa_turret | 16 | 96 | 2 |
| anti_air | 29 | 174 | 10 |
| behemoth | 498 | 2892 | 218 |
| biplane | 101 | 606 | 65 |
| bomber | 346 | 2072 | 212 |
| cloudskimmer | 248 | 1488 | 137 |
| coal_car | 112 | 672 | 40 |
| cruiser | 351 | 2042 | 142 |
| field_artillery | 40 | 240 | 23 |
| fixed_artillery | 26 | 156 | 26 |
| gunboat | 169 | 1014 | 87 |
| gyrobomber | 370 | 2112 | 212 |
| horse_cart | 98 | 588 | 59 |
| ironclad | 199 | 1146 | 86 |
| monoplane | 73 | 438 | 47 |
| passenger_car | 379 | 2274 | 114 |
| simple_locomotive | 137 | 820 | 73 |
| sloop | 361 | 2130 | 221 |
| small_car | 108 | 648 | 62 |
| torpedoboat | 137 | 804 | 106 |
| wooden_cart | 160 | 908 | 115 |
