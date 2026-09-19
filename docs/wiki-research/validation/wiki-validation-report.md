# Gameplay guide validation report

Validated: 2026-09-11 (Europe/Berlin)

## Final outcome

- The public registry contains all 41 top-level guide sections exactly once. Navigation, overview cards, recipes, and the player command index derive from that registry.
- Essentials, Help Menu, Excellent Crates, and Trial Rooms were removed from the public guide. Each retired URL returns HTTP 404.
- Public pages are practical player instructions. Rendered command tables show ordinary player commands and omit restricted or staff commands and raw permission nodes.
- Every visible research date is labelled `Last modified`.
- The desktop navigation sidebar is sticky below the site header and scrolls independently with bounded height, `overflow-y: auto`, and overscroll containment. The responsive mobile flow remains unchanged.
- Guide cards use a uniform neutral border with no coloured left edge.
- Persistent search appears under the Gameplay Guide heading and indexes 674 unique page and anchored-section entries across static and dynamic guide pages.

## Exact validation

### TypeScript

Command: `cd frontend; npx tsc --noEmit --pretty false`

Outcome: exit 2 with exactly 21 pre-existing errors in unrelated map editor, map label, and character lore tests. No guide or search source error. Exact output: [wiki-tsc-final.txt](./wiki-tsc-final.txt).

### Targeted regression suite

Command: `cd frontend; npm test -- --run app/wiki/wikiRoutes.test.tsx app/wiki/data/registry.test.ts app/components/wiki/wikiComponents.test.tsx app/wiki/vehicles/vehicleSource.test.ts app/wiki/vehicles/vehicles.test.ts lib/wikiSearch.test.ts app/components/wiki/WikiSearch.test.tsx scripts/build-wiki-search-index.test.mjs`

Outcome: exit 0, 8 files passed and 99 tests passed. This covers route and registry parity, shared rendering, player-command filtering, search extraction and keyboard behavior, neutral card borders, and all vehicle source, hierarchy, texture, UV, and geometry checks.

### Guarded production build (historical)

Command: `cd frontend; npm run build`

Outcome: exit 0. The production safety guard ran normally, Next compiled and generated 186 of 186 application pages, and the postbuild search generator printed `Generated 692 guide search entries.` Exact output: [wiki-build-final.txt](./wiki-build-final.txt). This build predates the final copy, recipe, command, anchor, and search-extractor edits. It was not repeated because the configured build writes to the shared `.next` directory used by the active port 3000 development server; the project has no isolated build output setting.

### Exhaustive rendered sweep

The final sweep requested all 167 current guide routes represented by the route manifest, including the overview, all indexes, and every generated material, instrument, station, and vehicle detail page, from the active development server.

Outcome: every route returned HTTP 200. Every internal guide link resolved to a current route and every fragment resolved to an element ID. Rendered public content contained zero literal em dashes, em dash entities, `Last verified`, draft labels, known-bug labels, staff-only labels, raw `permission node` wording, `unverified` wording, or mojibake. The four retired routes returned HTTP 404. Fresh extraction produced 678 unique entries and was written to `public/wiki/search-index.json`; the final write included the last four changed Sitting records.

After that exhaustive pass, the only later content changes were isolated to Bird Mail and Advanced Crafting. Bird Mail was included in a second clean 167-route sweep with zero failures. Advanced Crafting was then refreshed directly from its HTTP 200 live render after the final compact ingredient grids: 8 entries were replaced in place and the final index contains 675 entries. Its 68 unique rendered texture URLs all returned HTTP 200, all three station model and texture pairs existed, and the removed diagnostics and stat cards were absent. `npx vitest run app/wiki/wikiRoutes.test.tsx` passed all 44 route and rendered-asset tests against this final source state.

The later Furniture gallery update was validated from its HTTP 200 live render: all 22 authentic model JSONs and 17 required/shared texture files returned HTTP 200, the page rendered 22 selectors backed by one selected model viewer, and the focused 44-test route and asset suite passed. Four Furniture search entries replaced the prior five after the Commands section was removed, leaving 674 entries in the final public index.

### Source copy scan

An exhaustive UTF-8 scan of `frontend/app/wiki` and `frontend/app/components/wiki` found zero literal U+2014 characters, `&mdash;`, `&#8212;`, `&#x2014;`, or escaped `\\u2014` representations. A style scan found no `border-l`, `border-left`, or `borderLeft` use in guide source; the only matching strings are negative assertions in the shared component test.

## Browser evidence

- Desktop sidebar: client height 664 px, scroll height 1840 px. Scrolling over the sidebar moved its `scrollTop` to 500.25 while the document remained at `window.scrollY = 0`; article position did not change.
- Rank table: Commoner renders grey. Noble and Gilded render exact per-letter gradients without bold. Ascended and Legacy render exact per-letter gradients in bold, using the user-provided TAB values. Perks are 14/10/7/5/5-day switch cooldowns, 3/3/4/5/5 alive characters, 0/1/2/20/20 name-colour stops, and 1/1/2/3/3 wardrobe slots.
- Rank source evidence: the values match `C:\Users\MSI\Desktop\plugins\RPCharacters\permission-groups.yml`; rank colours were superseded by the user's exact TAB configuration supplied on 2026-09-11.
- Vehicle QA visually verified all 21 base silhouettes and 15 of 16 texture variants across all five families. The Monoplane Pirate capture timed out, while its PNG, UV, source hierarchy, and identical-base-geometry checks passed. Each available selection rendered one canvas; the unavailable Biplane Prism selection rendered its unavailable note and zero canvases.
- Native Chrome integration was unavailable. Dedicated Chromium preview supplied the desktop checks. Mobile resize remained blocked by preview infrastructure timeouts.

## Running preview

The preview is intentionally left in normal Next development mode so subsequent copy edits appear immediately: `http://127.0.0.1:3000`.

- Launcher PID: 17764
- Listener PID: 22396
- Logs: [stdout](./wiki-dev-resume.stdout.log), [stderr](./wiki-dev-resume.stderr.log)

## Follow-up live copy verification

- `/wiki/characters` omits the Aliases command column while all other command tables retain it.
- Donor rank mentions use the shared exact per-letter `RankName` rendering. The only plain `Legacy` match is the unrelated armour collection named `Legacy Sets`.
- Search extraction inserts boundaries between block, table, list, form-label, select, option, and button text while preserving adjacent per-letter rank spans. The focused component/search suite passed 24/24, followed by the extraction and keyboard subset at 6/6.
- The Classes source and live search records contain zero suspicious mojibake sequences. The public index now contains 674 unique live-rendered entries after anchored detail sections were made addressable and duplicate hrefs were folded together.
- The Profile client UI was verified after mount: it displays `Create a profile token with /token create profile, then log in to see your characters, submissions, and kit custom items.` The command renders in accent green, computed `rgb(122, 158, 106)`.
## Dependency audit retained from the earlier integration run

Command: `cd frontend; npm audit --omit=dev`

Outcome: exit 1 with pre-existing advisories in Next 16.0.10, nanoid 3.3.11, postcss 8.4.31, and sharp 0.34.5. No dependency versions or lockfiles changed. `package.json` changed only to add the wiki search postbuild hook. Exact output: [wiki-npm-audit.txt](./wiki-npm-audit.txt).

## User-run git commands

These commands are suggestions only. No commit, push, staging, or other git mutation was performed.

```bash
git add CLAUDE.md docs/wiki-research frontend/app/components/shell/SiteHeader.tsx frontend/app/components/wiki frontend/app/wiki frontend/lib/wikiSearch.ts frontend/public/wiki frontend/scripts/build-wiki-search-index.mjs frontend/scripts/convert-vehicle-bbmodels.mjs frontend/package.json frontend/vitest.config.mjs
git commit -m "Publish the player gameplay guide"
git push
```

