# Staff review-sheet 3D renderer

Headless Chromium (Playwright) + Three.js. Python `review_sheet.py` calls `cli.mjs`.

```bash
cd backend/render
npm install
npx playwright install chromium
```

Disable with `SHEET_RENDER_DISABLE=1`. Override Node with `SHEET_RENDER_NODE`.
