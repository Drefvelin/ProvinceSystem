# Step 72.03 — Title RGB picker

**Build:** ProvinceSystem frontend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Single-colour picker for map title `rgb` strings, visually consistent with [`NameColourPicker`](../../../frontend/app/components/shared/NameColourPicker.tsx) (chips, native color input, TFMC theme) but storing `"R,G,B"` not hex gradient arrays.

## Deliverables

### 1. `lib/map/titleRgb.ts`

| Function | Purpose |
|----------|---------|
| `rgbStringToHex("180,80,80")` → `#b45050` | Picker display |
| `hexToRgbString("#b45050")` → `"180,80,80"` | On change |
| `parseRgbString(s)` | Validate; return `[r,g,b]` or null |
| `tweakRgbNear(base, usedSet)` | Port `county_editor.py` algorithm to TS |

### 2. `TitleRgbPicker` component

Path: [`frontend/app/components/map/editor/TitleRgbPicker.tsx`](../../../frontend/app/components/map/editor/TitleRgbPicker.tsx)

Props:

```ts
type TitleRgbPickerProps = {
  rgb: string;           // "R,G,B"
  onChange: (rgb: string) => void;
  usedRgbs?: string[];   // collision warn
  suggestFromRgb?: string; // first member province/county colour
  disabled?: boolean;
  onError?: (msg: string | null) => void;
};
```

UI:

- Large colour chip showing current colour.
- `<input type="color">` bound to hex.
- Optional hex text field (`#RRGGBB`).
- Warning banner if `rgb` in `usedRgbs` (another title at same tier).
- **Suggest** button when `suggestFromRgb` set and current collides.

Reuse `inputClass` / layout patterns from `NameColourPicker` (no multi-stop drag; no MC preview).

### 3. Unit tests

[`titleRgb.test.ts`](../../../frontend/app/lib/map/titleRgb.test.ts):

- Round-trip hex ↔ rgb string.
- `tweakRgbNear` avoids used set.
- Invalid strings rejected.

## Files touched

| File | Change |
|------|--------|
| `frontend/app/lib/map/titleRgb.ts` | New |
| `frontend/app/lib/map/titleRgb.test.ts` | New |
| `frontend/app/components/map/editor/TitleRgbPicker.tsx` | New |

## Done when

- Story or dev page renders picker; changing colour updates `rgb` prop as `"R,G,B"`.
- Vitest green for `titleRgb.test.ts`.

## Status

**Done** (code + tests).

