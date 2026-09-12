# Recipe icon alignment

The reported Steel Magical Core output used the exact sprite
`frontend/public/wiki/textures/magic_crafting/basic_magical_core.png`.
Its canvas is 16 by 16 pixels, but the nontransparent bounds are
`[left=3, top=2, right=14, bottom=13]` (exclusive right/bottom).
The visible centre is `(8.5, 7.5)` instead of the canvas centre `(8, 8)`.
At a 40px icon size this puts the gold artwork 1.25px right and 1.25px above centre.

The recipe layout and output square were already centred correctly. The fix
translates only the image inside its existing 32px/40px footprint. It measures
actual PNG alpha bounds rather than adding item-specific offsets. For this sprite
the correction is `translate(-3.125%, 3.125%)`. Already-centred sprites receive
no correction. Non-square PNGs use `object-contain` to preserve their aspect ratio.
Hover enlargement stays on an outer wrapper, so scaling does not replace the
inner centring transform. Source PNG bytes are unchanged.

Other examples confirm the same padding issue: Enchanted Dust has bounds
`[2,3,14,14]` on a 16px canvas (0.5px below centre); Abyssalite Magical Core
(`petty_magical_core.png`) has bounds `[0,0,16,15]` (0.5px above centre).

Regenerate metadata after extracting or replacing wiki sprites:

```powershell
python frontend/scripts/build-recipe-icon-bounds.py
```

The generator requires Pillow, excludes vehicle model atlases and records only
asymmetric nonempty images in `data/generated/recipeIconBounds.json`.

Verification from `frontend`:

```powershell
npx vitest run app/components/wiki/recipeIconAlignment.test.tsx app/components/wiki/wikiComponents.test.tsx app/wiki/materials/materials.test.tsx
```

Result: 29 passed. The actual Steel Magical Core recipe integration test failed
before the renderer was wired to the new component and passed afterward.
The live `/wiki/materials/steel-ingot` response returned HTTP 200 and contained
the expected `translate(-3.125%, 3.125%)` on the Steel Magical Core image.
