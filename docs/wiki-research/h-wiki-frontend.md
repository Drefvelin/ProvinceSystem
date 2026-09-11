# Gameplay Guide ("Wiki") — Frontend Research Dossier

Scope: `C:\Users\MSI\Desktop\ProvinceSystem\frontend`. Read-only survey, no code changed.

---

## 1. `frontend\app\wiki\` structure, `data.ts` shape, and page consumption

### File inventory

```
app/wiki/data.ts                                  # all content + types, no JSX
app/wiki/layout.tsx                                # shared sidebar shell, wraps everything in WikiStaffGate
app/wiki/page.tsx                                  # "/wiki" overview — static, hand-written blurbs
app/wiki/arcane-trace-detector/page.tsx            # static leaf page (no dynamic segment)
app/wiki/mount-whistle/page.tsx                    # static leaf page
app/wiki/musical-instruments/page.tsx              # static index page (grid of instrument links)
app/wiki/musical-instruments/[slug]/page.tsx       # dynamic detail page, generateStaticParams from data.ts
app/wiki/materials/page.tsx                        # static index page (grouped by station + drop-only grid)
app/wiki/materials/[slug]/page.tsx                 # dynamic detail page, generateStaticParams
app/wiki/stations/page.tsx                         # static index page (grid of station links)
app/wiki/stations/[slug]/page.tsx                  # dynamic detail page, generateStaticParams
```

So today there are two route shapes in play:
- **Static single-topic pages** (`arcane-trace-detector`, `mount-whistle`) — one topic per file, own hand-authored prose plus tables/JSX built directly against arrays from `data.ts`. No `[slug]` route; these are the "3 of the 5 sections."
- **Index + `[slug]` detail pairs** (`musical-instruments`, `materials`, `stations`) — an index page listing all items from a data array, and a `[slug]/page.tsx` that calls `generateStaticParams()` off that same array and a `getXBySlug()` lookup helper from `data.ts` for `notFound()` handling.

`app/wiki/layout.tsx` is the single shared layout for the whole `/wiki/*` subtree (Next.js App Router route-group-less layout — it applies to every page under `app/wiki/`).

### `data.ts` — every exported type/interface

(`app/wiki/data.ts`, line numbers from `grep -n "^export "`)

| Line | Export | Kind |
|---|---|---|
| 1 | `Slot` | type — `{ name, qty, texture?, model?: { url, texture } }` |
| 9 | `Recipe` | type — `{ key, title, station, time?, requirement?, ingredients: Slot[], output: Slot, note? }` |
| 22 | `navItems` | const array (sidebar nav, `as const`) |
| 33 | `detectorRecipes` | `Recipe[]` |
| 78 | `signalTable` | array of `{ signal, meaning }` (inline, untyped) |
| 89 | `lootTable` | array of `{ rarity, chance, rewards }` (inline, untyped) |
| 128 | `instrumentRecipes` | `Recipe[]` |
| 248 | `InstrumentKey` | type — `{ num, note, sound }` |
| 250 | `InstrumentInfo` | type — `{ slug, name, icon, mode: "chord"\|"octave", row1, row2 }` |
| 299 | `instruments` | `InstrumentInfo[]` (built from a private `instrumentDefs` array via `.map`) |
| 307 | `getInstrumentBySlug(slug)` | lookup fn over `instruments` |
| 313 | `whistleRecipe` | single `Recipe` |
| 325 | `whistleMessages` | array of `{ message, meaning }` |
| 333 | `materialRecipes` | `Recipe[]` (grouped by comments per station: Ingot/Alchemy/Magic/Engineer/Medicine Station) |
| 715 | `leatherInlineRecipe` | ad-hoc note object, not a `Recipe` (special-cased 1-slot recipe) |
| 719 | `DropOnlyMaterial` | type — `{ name, texture?, lore? }` |
| 725 | `dropOnlyMaterials` | `DropOnlyMaterial[]` |
| 822 | `slugify(name)` | pure fn: lowercases, replaces non-alnum with `-`, trims dashes |
| 838 | `StationInfo` | type — see below |
| 886 | `stations` | `StationInfo[]` |
| 1020 | `getStationBySlug(slug)` | lookup over `stations` |
| 1024 | `getRecipesForStation(name)` | filters `allRecipeCollections.flat()` by `r.station === name` |
| 1030 | `MaterialCatalogEntry` | type — `{ slug, name, texture?, lore?, recipe?, usedIn: Recipe[] }` |
| 1078 | `materialCatalog` | `Map<string, MaterialCatalogEntry>`, built by `buildMaterialCatalog()` |
| 1081 | `catalogNames` | `Set<string>` of `materialCatalog.keys()` — "is this ingredient name a linkable material" |
| 1083 | `getMaterialBySlug(slug)` | scans `materialCatalog.values()` for matching slug |

`StationInfo` (line 838):
```ts
// app/wiki/data.ts:838-856
export type StationInfo = {
  slug: string;
  name: string;
  blurb: string;
  icon: string;
  model?: { url: string; texture: string };
  fallbackTexture?: string;
  craftRecipe?: Recipe;
  noPlaceableBlock?: boolean;
  vanillaBlock?: { name: string; accessNote: string };
  cubeFaces?: { up: string; down: string; north: string; south: string; east: string; west: string };
};
```

Private (non-exported) helpers worth noting because a new author will want the same pattern: `T()` (texture path, line 20), `M()` (model path, ~line 863), `V()` (vanilla texture shorthand, ~line 864), `empty: Slot` placeholder for blank crafting-grid cells, `instrumentDefs`/`instrumentKeys()` (data-driven generation of the 9 instruments' keyboard layout), `allRecipeCollections: Recipe[][]` (line ~816, the fixed list of every recipe array — **this is manually maintained and any new plugin's recipe array must be added here or `getRecipesForStation` / the material "used in" reverse index silently misses it**).

### `navItems` — structure and consumption

```ts
// app/wiki/data.ts:22-29
export const navItems = [
  { href: "/wiki", label: "Overview" },
  { href: "/wiki/arcane-trace-detector", label: "Arcane Trace Detector" },
  { href: "/wiki/musical-instruments", label: "Musical Instruments" },
  { href: "/wiki/mount-whistle", label: "Mount Whistle" },
  { href: "/wiki/materials", label: "Materials" },
  { href: "/wiki/stations", label: "Stations" },
] as const;
```

It is a **flat array of `{ href, label }`**, one entry per top-level section (index pages only — instrument/material/station detail pages are *not* individually listed here, they're reached by clicking through the section index page). No `category`, `order`, or grouping field exists.

Consumers:
- `app/wiki/layout.tsx:5,16` — imports `navItems`, `.map()`s it straight into a flat/wrapped row of `<Link>`s in the sidebar (`lg:flex-col` on large screens, `flex-row flex-wrap` on small). No grouping logic — with 6 items today it reads as one list; with ~40 it would be one very long unstructured column.
- `app/wiki/page.tsx:2,29-30` — imports `navItems`, filters out the `/wiki` self-link, and renders each as a card. The **card blurb text is a second, hand-maintained map keyed by `href`** (`blurbs: Record<string,string>`, `app/wiki/page.tsx:4-15`) that is NOT part of `data.ts` — a real duplication/drift risk once every plugin page needs a card blurb, since `navItems` and `blurbs` must be kept in lockstep by hand and nothing enforces it (a missing key just renders blank).

Page → data.ts import map:
- `layout.tsx` → `navItems`
- `wiki/page.tsx` → `navItems` (+ local `blurbs` map)
- `arcane-trace-detector/page.tsx` → `detectorRecipes`, `lootTable`, `signalTable`
- `mount-whistle/page.tsx` → `whistleMessages`, `whistleRecipe`
- `musical-instruments/page.tsx` → `instruments`
- `musical-instruments/[slug]/page.tsx` → `getInstrumentBySlug`, `instrumentRecipes`, `instruments` (for `generateStaticParams`)
- `materials/page.tsx` → `dropOnlyMaterials`, `materialRecipes`, `slugify`
- `materials/[slug]/page.tsx` → `getMaterialBySlug`, `materialCatalog` (for `generateStaticParams`)
- `stations/page.tsx` → `stations`
- `stations/[slug]/page.tsx` → `getRecipesForStation`, `getStationBySlug`, `stations` (for `generateStaticParams`)

All detail pages follow the same idiom:
```ts
// e.g. app/wiki/stations/[slug]/page.tsx:8-19
export function generateStaticParams() {
  return stations.map((s) => ({ slug: s.slug }));
}
export default async function StationDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const station = getStationBySlug(slug);
  if (!station) notFound();
  ...
}
```
This is Next.js 15/16 App Router's async-`params` convention (`params: Promise<...>`), and all detail routes are statically generated via `generateStaticParams`, i.e. fully SSG at build time, not on-demand.

---

## 2. Components

### `frontend\app\components\wiki\`

| File | Purpose |
|---|---|
| `CraftingGrid.tsx` | Renders a 3×3 crafting grid + arrow + output slot from a `Recipe`. Looks up `catalogNames` to decide whether an ingredient name should be a clickable `<Link>` to `/wiki/materials/{slugify(name)}` (`app/components/wiki/CraftingGrid.tsx:6,46-52`). Looks up the recipe's station in `stations` to render a clickable station badge (`:58,66-78`). Delegates to `StationModelViewer` when a slot has a `model` instead of a flat `texture` (`:17-18`). |
| `InstrumentKeyboard.tsx` | Client component (`"use client"`). Renders the 2-row, 8-key virtual keyboard for an `InstrumentInfo`; preloads an `HTMLAudioElement` pool from `instrument.row1/row2[].sound` URLs, persists a volume slider to `localStorage` under key `"tfmc-wiki-instrument-volume"` (`:33,41,76`). |
| `SimpleCubeViewer.tsx` | Client component. Renders a plain 6-textured-face vanilla-block cube preview using three.js (see §4). |
| `StationModelViewer.tsx` | Client component. Renders a Blockbench-style JSON block model with a single shared texture using three.js (see §4). |
| `WikiStaffGate.tsx` | Access gate — see §2 detail below. |

### Other components imported by wiki pages, outside that folder

- `next/link` (framework) — used everywhere for internal navigation.
- `next/navigation` (`notFound`, `useRouter`) — framework, used in `[slug]` pages and `WikiStaffGate`.
- `app/hooks/useSiteStaffAccess.ts` — imported by `WikiStaffGate` (not itself a component but the core gating hook).
- `lib/characters/uiDev.ts` (`isCharacterUiDev`) and `lib/site/staffAccess.ts` (`hasSiteStaffAccess`) — imported transitively via the hook.
- `app/layout.tsx` wraps the *entire app* (not wiki-specific) in `SiteDevGate` (`app/components/site/SiteDevGate.tsx`), which is a second, independent gate — see below.

No non-wiki visual components (e.g. shared card/table primitives) are reused by the wiki; all markup is written inline per page with repeated Tailwind class strings (see §3).

### `WikiStaffGate` — exact gating behaviour

File: `app/components/wiki/WikiStaffGate.tsx` (35 lines, full text below).

```tsx
// app/components/wiki/WikiStaffGate.tsx
"use client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useSiteStaffAccess } from "@/app/hooks/useSiteStaffAccess";

export default function WikiStaffGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { state } = useSiteStaffAccess({ enabled: true });   // <-- always enabled, no bypass prop

  useEffect(() => {
    if (state === "unauthenticated" || state === "denied") {
      router.replace("/");
    }
  }, [state, router]);

  if (state === "loading") return (<main>...</main>);
  if (state !== "staff") return null;
  return children;
}
```

**What it gates:** the *entire* `/wiki` subtree, unconditionally. It is wired in at the very top of `app/wiki/layout.tsx` (line 9: `<WikiStaffGate>` wraps the whole sidebar+content shell), so every route under `/wiki/*` — index and every future plugin page — is behind it. There is no per-page opt-out and no `enabled` flag threaded through from the caller (`WikiStaffGate` hardcodes `{ enabled: true }`, unlike `SiteDevGate` which computes `gateEnabled` dynamically).

**What condition it checks:** `useSiteStaffAccess` (`app/hooks/useSiteStaffAccess.ts:19-74`):
1. If `!enabled` (never true here) or `isCharacterUiDev()` is true → state is immediately `"staff"`, no network call. `isCharacterUiDev()` (`lib/characters/uiDev.ts:3-5`) is `process.env.NEXT_PUBLIC_CHARACTER_UI_DEV === "1"`.
2. Otherwise it reads a client-side session via `getSession()`/`isSessionValid()` (`lib/characters/session.ts`). No valid session → `"unauthenticated"`.
3. If a session exists, it calls `hasSiteStaffAccess(token)` (`lib/site/staffAccess.ts:12-24`), which hits `getPlayerMeta(token)` (a backend API call) and checks `permission_flags["tfmc.map.staff"] === true` (`lib/site/staffAccess.ts:3,5-9`). Staff → `"staff"`, otherwise `"denied"`; a 401 from the API is treated as `"denied"`, other errors are re-thrown then caught by the caller as `"denied"`.

So the gate is: **local env var bypass, OR a valid session token belonging to a player with the `tfmc.map.staff` permission flag from the backend**. There is no separate "wiki-only" role — it reuses the same staff flag as the map editor.

**Can a developer with no auth session running `npm run dev` locally open `/wiki` and see content?**

**No — by default they are redirected away.** Trace:
- `.env.example` (`.env.example:4-5`) ships `NEXT_PUBLIC_CHARACTER_UI_DEV` **commented out**, so unless a developer creates a local `.env.local` and explicitly sets `NEXT_PUBLIC_CHARACTER_UI_DEV=1`, `isCharacterUiDev()` is `false`.
- With no session in `localStorage`/wherever `getSession()` reads from, `isSessionValid(session)` is `false`, so `state` becomes `"unauthenticated"`.
- `WikiStaffGate`'s `useEffect` immediately calls `router.replace("/")` for `"unauthenticated"` (and `"denied"`), and while state is not `"staff"` it renders `null` — i.e. a blank page, then an instant client-side redirect to the site root.
- This is independent of, and in addition to, the app-wide `SiteDevGate` (`app/components/site/SiteDevGate.tsx`, wired in `app/layout.tsx:36`), which is gated by `NEXT_PUBLIC_SITE_DEV_GATE` (also commented out by default in `.env.example:2-3`) — so that outer gate is *off* by default and not the blocker. **`WikiStaffGate` is the actual blocker**, and it has no env-var-driven "off" switch of its own; the only way around it locally is the same `NEXT_PUBLIC_CHARACTER_UI_DEV=1` flag used for the character-wizard dev flow.

**Practical implication for the extending engineer:** to view/iterate on the wiki locally, set `NEXT_PUBLIC_CHARACTER_UI_DEV=1` in `frontend/.env.local` before `npm run dev`. Worth flagging to the team since this flag's name ("Character UI dev") doesn't obviously suggest "also unlocks the wiki" — someone unaware of this coupling would reasonably conclude the wiki is broken.

---

## 3. Styling conventions

### `--tfmc-*` custom properties

Defined once, in `app/internal/globals.css:3-11` (imported by the root layout, `app/layout.tsx:4`, as `"./internal/globals.css"` — note this file lives under an `internal/` folder despite being the app-wide stylesheet):

```css
/* app/internal/globals.css:3-14 */
:root {
  --tfmc-forest: #1a2e24;
  --tfmc-forest-deep: #0f1c16;
  --tfmc-moss: #2d4a3a;
  --tfmc-stone: #c8c2b4;
  --tfmc-cream: #e8e4d9;
  --tfmc-mist: #a8b5a8;
  --tfmc-accent: #7a9e6a;
  --tfmc-header-h: 3.5rem;

  --background: var(--tfmc-forest-deep);
  --foreground: var(--tfmc-cream);
}
```

Then re-exposed as Tailwind v4 theme tokens via `@theme inline` (`app/internal/globals.css:16-27`):
```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-tfmc-forest: var(--tfmc-forest);
  --color-tfmc-forest-deep: var(--tfmc-forest-deep);
  --color-tfmc-moss: var(--tfmc-moss);
  --color-tfmc-stone: var(--tfmc-stone);
  --color-tfmc-cream: var(--tfmc-cream);
  --color-tfmc-mist: var(--tfmc-mist);
  --color-tfmc-accent: var(--tfmc-accent);
  --font-sans: var(--font-source-sans);
  --font-display: var(--font-fraunces);
}
```
This means Tailwind v4 utility classes like `bg-tfmc-forest` are theoretically available, but **every wiki component instead uses raw `var(--tfmc-*)` inside arbitrary-value Tailwind syntax** (e.g. `text-[var(--tfmc-cream)]`, `border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)]`) rather than the `@theme`-registered utility classes. That's the actual repo convention to follow, not the theoretical `bg-tfmc-*` classes.

Consumed extensively throughout `app/wiki/**` and `app/components/wiki/**` (every page/component file references at least `--tfmc-cream`, `--tfmc-mist`, `--tfmc-accent`, `--tfmc-forest`, `--tfmc-forest-deep`).

### Repeated Tailwind idioms in wiki code

- Headings: `font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl` for `<h1>`, `text-xl` variant for `<h2>` — used identically in every page file (e.g. `app/wiki/mount-whistle/page.tsx:7-9`, `app/wiki/stations/[slug]/page.tsx:29`).
- Body copy: `text-sm text-[var(--tfmc-mist)]`.
- Card/panel background: `rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_45%,transparent)]` (index-page link cards) or `..._forest-deep)_55%...` (crafting grid / keyboard panels).
- Tables: identical `overflow-x-auto rounded-md border ...` wrapper + `<thead className="bg-[color-mix(in_srgb,var(--tfmc-forest)_60%,transparent)] text-[var(--tfmc-cream)]">` on every signal/loot/message table.
- Pixel-art icons: `[image-rendering:pixelated]` on every `<img>` of a game texture.
- `color-mix(in_srgb, var(--tfmc-X) N%, transparent)` is the standard way opacity/tinting is done everywhere instead of Tailwind's `/opacity` suffix — this is a hard convention to preserve for consistency across ~40 new pages.
- No shared `<Card>`/`<Table>`/`<PageHeading>` React component exists — all of the above is copy-pasted className strings per file. At 40 pages this duplication will become the main styling-consistency risk (a typo'd `color-mix` string on page 30 won't be caught by types).

### Fonts

Declared with `next/font/google` in the **root** layout, not the wiki layout: `app/layout.tsx:2,6-16`:
```ts
const fraunces = Fraunces({ variable: "--font-fraunces", subsets: ["latin"], display: "swap" });
const sourceSans = Source_Sans_3({ variable: "--font-source-sans", subsets: ["latin"], display: "swap" });
```
Applied as CSS variable classes on `<body>` (`app/layout.tsx:34`). Fraunces (`--font-fraunces`) is used for all headings/display text; Source Sans 3 is the implicit body font via `--font-sans`/`font-family: var(--font-source-sans)` in `app/internal/globals.css:27,34`. No wiki-specific font.

### Tailwind config

`tailwind.config.js` (root of `frontend/`) is minimal and does **not** contain the `--tfmc-*`/font theme extensions — those live in `app/internal/globals.css`'s Tailwind v4 `@theme inline` block instead (Tailwind v4's CSS-first config style):
```js
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
```
So there's nothing to extend in `tailwind.config.js` for new wiki pages — new tokens, if ever needed, would go into `app/internal/globals.css`.

---

## 4. Texture/model serving, `T()` helper, 3D preview rendering

### Static asset layout

`frontend/public/wiki/`:
```
public/wiki/models/     4 files   (Blockbench-exported JSON block models)
public/wiki/sounds/     144 files (instrument note .ogg files, under sounds/instruments/<folder>/)
public/wiki/textures/   141 files (png icons, subfoldered: herbs, instruments, magic_crafting, materials, pets, stations, tools, vanilla)
```
Next.js serves everything under `public/` at the site root, so `public/wiki/textures/materials/mythril_fragment.png` is reachable at `/wiki/textures/materials/mythril_fragment.png` — exactly the convention the data.ts helpers build.

### `T()` helper — exact signature

```ts
// app/wiki/data.ts:20
const T = (path: string) => `/wiki/textures/${path}`;
```
Not exported; used throughout `data.ts` to build every `texture:` field, e.g. `T("vanilla/iron_block.png")` → `/wiki/textures/vanilla/iron_block.png`. Two sibling helpers exist near the stations section (not exported either):
```ts
// app/wiki/data.ts (near line 863, inside/just above `stations`)
const M = (path: string) => `/wiki/models/${path}`;          // model JSON path
const V = (file: string) => T(`vanilla/${file}`);              // shorthand for T("vanilla/"+file)
```
`instrumentKeys()` (`app/wiki/data.ts:~261`) builds sound URLs the same way inline: `` `/wiki/sounds/instruments/${folder}/${folder}_${num}${letter}_${suffix}.ogg` ``.

### 3D model preview component

Library: **three.js** directly (`import * as THREE from "three"`), plus `OrbitControls` from `three/examples/jsm/controls/OrbitControls.js`. Not react-three-fiber, not `<model-viewer>` — a hand-rolled imperative three.js scene inside a `useEffect`.

Two variants:
- `StationModelViewer.tsx` (`app/components/wiki/StationModelViewer.tsx`) takes `{ modelUrl, textureUrl, variant }`. It `fetch()`es `modelUrl` as JSON — a small custom Blockbench-style schema (`BlockModel = { texture_size, elements: Element[] }`, each `Element` a box with `from/to` in a 0–16 grid, optional pivot `rotation`, and per-face `{ uv, texture }`), builds a `THREE.BoxGeometry` per element with UV coordinates remapped from Minecraft's 16-unit grid (`:21-60`), and applies a **single shared texture** (`textureUrl`, loaded via `THREE.TextureLoader`, `NearestFilter` for pixel-art look, `alphaTest: 0.3` for cutout transparency) to all elements via one `MeshLambertMaterial` (`:108-125`). Auto-rotating `OrbitControls`; `variant="thumb"` disables user interaction and speeds up auto-rotate for use inside a `CraftingGrid` slot (`app/components/wiki/CraftingGrid.tsx:17-18`).
- `SimpleCubeViewer.tsx` (`app/components/wiki/SimpleCubeViewer.tsx`) takes `{ faces: { up, down, north, south, east, west }, variant }` — six independent texture URLs, one per cube face, mapped onto a `THREE.BoxGeometry(1,1,1)` via a 6-element material array matching Minecraft's axis convention (`+x=east, -x=west, +y=up, -y=down, +z=south, -z=north`, `:69-84`). Used for stations that are just re-skinned vanilla blocks (`StationInfo.cubeFaces`).

Both manage their own WebGLRenderer lifecycle (create/dispose on mount/unmount, `requestAnimationFrame` loop, window-resize listener) with no shared abstraction between them — a candidate for extraction if many more model-preview stations are added, but not required for scaling *data*.

`StationDetailPage` (`app/wiki/stations/[slug]/page.tsx:35-38`) picks the renderer based on which optional field is populated on `StationInfo`: `model` → `StationModelViewer`, else `cubeFaces` → `SimpleCubeViewer`, else a static fallback texture/"not documented" block.

---

## 5. Project tooling

`frontend/package.json` (full):
```json
{
  "name": "servermap",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev --turbopack",
    "prebuild": "node scripts/assert-prod-build-env.mjs",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "vitest run"
  },
  "dependencies": {
    "fflate": "^0.8.3",
    "next": "^16.0.7",
    "react": "^19.2.1",
    "react-dom": "^19.2.1",
    "three": "^0.185.1"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@testing-library/dom": "^10.4.1",
    "@testing-library/react": "^16.3.3",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "@types/three": "^0.185.4",
    "autoprefixer": "^10.4.21",
    "jsdom": "^30.0.1",
    "postcss": "^8.5.3",
    "tailwindcss": "^4.0.14",
    "typescript": "^5.9.3",
    "vitest": "^3.2.4"
  }
}
```

- **Dev server:** `npm run dev` → `next dev --turbopack`. No `-p`/`--port` flag in the script and no port override in `next.config.ts`, so it runs on Next's **default port 3000**.
- **Build:** `npm run build` → `next build`, preceded automatically by `prebuild` → `node scripts/assert-prod-build-env.mjs` (an env-var assertion script gating production builds — not wiki-specific).
- **Typecheck:** **no dedicated `tsc`/`typecheck` script exists.** TypeScript is a devDependency and `next build`/`next dev` type-check as part of their own pipeline, but there is no standalone `npm run typecheck` for the engineer to run quickly while iterating.
- **Lint:** `npm run lint` → `next lint`.
- **Tests:** `npm run test` → `vitest run`. Config at `frontend/vitest.config.ts`:
  ```ts
  // frontend/vitest.config.ts
  export default defineConfig({
    resolve: { alias: { "@": path.resolve(__dirname, ".") } },
    test: {
      environment: "node",   // default; jsdom opt-in per-file via `@vitest-environment jsdom` docblock
      include: ["app/**/*.test.ts", "app/**/*.test.tsx", "lib/**/*.test.ts"],
    },
  });
  ```
  Node is the default test environment (fast, for pure-logic tests); component tests must opt into `jsdom` per-file. No `*.test.ts(x)` files currently exist under `app/wiki/` or `app/components/wiki/` (none found in this survey) — the wiki has **no existing test coverage** to learn conventions from beyond this global config.
- `next.config.ts` also sets `turbopack: { root: ".." }` (so the Next app can resolve `../shared/skins` outside `frontend/`) and `devIndicators: false`.

---

## 6. Cross-linking conventions

There is no generic "related links" or "See also" component/section anywhere in the wiki. Cross-linking is implicit and derived entirely from shared identity in `data.ts`:

1. **Ingredient → material page.** `CraftingGrid`'s `Slot` sub-component checks `catalogNames.has(name)` (`app/components/wiki/CraftingGrid.tsx:6`) — `catalogNames` is a `Set` of every name that exists as a key in `materialCatalog` (`app/wiki/data.ts:1081`). If the ingredient/output name matches, the slot becomes a `<Link href={`/wiki/materials/${slugify(name)}`}>` (`CraftingGrid.tsx:46-52`); otherwise it's an inert div. This means **any recipe anywhere that references a material by its exact string name automatically gets a live cross-link**, with zero explicit "related slug" authoring — but it also means a typo'd or renamed ingredient name silently loses its link.
2. **Recipe → station page.** `CraftingGrid` also looks up `stations.find((s) => s.name === recipe.station)` (`CraftingGrid.tsx:58`) and, if found, renders the station name+icon as a link to `/wiki/stations/{slug}` (`:66-78`); otherwise it falls back to plain text. Again matched purely by string equality on `station`/`name`, not an explicit foreign key.
3. **Material → "what can be crafted from it".** `buildMaterialCatalog()` (`app/wiki/data.ts:1043-1075`) does a reverse-index pass: for every recipe in `allRecipeCollections.flat()`, for every ingredient, if that ingredient name matches a catalog entry, push the recipe onto that entry's `usedIn: Recipe[]`. The material detail page (`app/wiki/materials/[slug]/page.tsx:60-70`) renders that `usedIn` list as "What can be crafted from it" — this is the closest thing to a "See also" section in the codebase, and it is fully derived, not hand-authored.
4. **Index ↔ detail "back" links.** Every `[slug]/page.tsx` hand-writes a "&larr; Back to X" `<Link>` to its parent index page (e.g. `app/wiki/materials/[slug]/page.tsx:21-23`) — a simple, repeated (not centralised) convention.
5. **`slugify()`** (`app/wiki/data.ts:822-828`) is the one shared primitive making all of the above possible — every cross-link URL is built by re-deriving a slug from a plain-text name at render time (`slugify(m.name)`, `slugify(name!)`), rather than storing a persisted slug field on ingredient references.

No page currently links "sideways" between unrelated top-level sections (e.g. nothing on the Mount Whistle page links to Materials), and `navItems`/the wiki overview page's `blurbs` map are the only place all top-level sections are enumerated together.

---

## Assessment

**Does `navItems`/`data.ts` scale cleanly from 5 sections to ~40 plugin pages? No — not as currently shaped, though the underlying `Recipe`/`Slot`/catalog machinery is sound and worth keeping.**

What already scales fine: the `Recipe`/`Slot` types, the `T()`/`M()`/`V()` path helpers, `slugify()`, and the `materialCatalog` reverse-index pattern are all generic and data-driven — they don't care how many recipes or materials exist. Adding a 40th plugin's `Recipe[]` array is mechanically identical to adding the 5th's.

What breaks (or degrades badly) at ~40 pages, all rooted in the same fact — **`data.ts` is one 1,088-line flat file with no `category`/grouping concept and no per-section boundary**:

1. **`navItems` has no `category` field**, so `layout.tsx`'s sidebar (`app/wiki/layout.tsx:16-24`) renders it as one flat, unordered list. At 6 items this is a sidebar; at ~40 it becomes an unreadable, unsectioned wall of links with no visual grouping by plugin family (e.g. "Detectors", "Instruments", "Crafting", "Stations").
2. **`navItems` and the overview page's `blurbs: Record<string,string>` (`app/wiki/page.tsx:4-15`) are two hand-synced parallel structures.** Every new page needs an entry in both, keyed by matching `href` strings, with nothing enforcing the pairing — a missing blurb just silently renders blank. This duplication scales linearly in *risk* with page count.
3. **`allRecipeCollections: Recipe[][]` (`app/wiki/data.ts:~816`) is a manually maintained master list** that `getRecipesForStation()` and `buildMaterialCatalog()`'s reverse index both depend on. Every new plugin's recipe array must be remembered and appended here, or that plugin's recipes silently vanish from station pages and from materials' "used in" lists — an easy, silent omission at 40 sections that today (5 sections) is trivial to keep in sync by eye.
4. **One 1,000+ line file is a poor unit of collaboration** at 40 sections/plugins — merge conflicts multiply when every contributor edits the same file, and the file becomes hard to navigate even with editor search (there is no filename-level signal for "where is plugin X's data").
5. Mixed page shapes (static single-topic vs. index+`[slug]`) is fine as a *pattern* but currently has zero shared layout/component beyond copy-pasted className strings (§3) — 40 pages authored this way will drift stylistically without a shared `<PageHeading>`/`<InfoCard>`/`<DataTable>` primitive.

**Recommendation:** keep the current type system and cross-link machinery, but restructure the data layer along two axes:

- **Split `data.ts` by plugin/category into `app/wiki/data/<category>.ts` files** (e.g. `data/detector.ts`, `data/instruments.ts`, `data/materials.ts`, `data/stations.ts`, one file per new plugin going forward), each exporting its own `Recipe[]`/entity arrays using the same `T()/M()/V()` helpers (move those three plus `Slot`/`Recipe`/`slugify` into a small shared `data/shared.ts`). Keep a thin `data/index.ts` (or the existing `data.ts` re-purposed) that imports every category file and re-exports/aggregates: this is what replaces the manually-maintained `allRecipeCollections` — instead of remembering to append to a list, a category's array is included the moment its file exists in the aggregator's import list (still one line to add, but colocated with a self-contained file per plugin instead of a diff deep inside a 1000-line file).
- **Add a `category: string` (and optionally `order: number`) field to `navItems` entries**, and change `navItems` itself to be *generated* from each category file's own metadata (e.g. each `data/<category>.ts` exports a `sectionMeta: { href, label, category, blurb }`) rather than hand-duplicated between `data.ts` and `wiki/page.tsx`'s `blurbs` map. That single change removes finding #2 above and lets `layout.tsx`'s sidebar group by `category` (`<h3>{category}</h3>` + its items) instead of rendering one flat list — the natural fix for finding #1 as sections grow past ~10.
- Filesystem-based content (MDX/CMS) is **not** warranted here: the wiki isn't prose-heavy free-form content, it's structured game data (recipes, slots, stations) driving typed, interactive React (crafting grids, 3D previews, keyboards) — the current typed-object-array approach is the right shape for that, it just needs to be split by file and given an explicit `category` field before it reaches 40 entries.
