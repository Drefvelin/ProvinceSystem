/**
 * Extracts the ItemsAdder item sprites referenced by the MMOItems
 * crafting-station configs into `public/wiki/textures/itemsadder/`, and writes
 * `app/wiki/data/generated/itemsadderItems.json` mapping each referenced
 * ItemsAdder id to its display name and (when one exists) its sprite.
 *
 * Both sources live OUTSIDE this repository (they are the server's plugin
 * configs), so this script is deliberately not part of `npm run build`. Run it
 * by hand when the server's ItemsAdder packs or crafting stations change:
 *
 *   node scripts/extract-itemsadder-textures.mjs [path/to/ItemsAdder/contents] [path/to/MMOItems/crafting-stations]
 *
 * The manifest it writes is checked in, so `build-station-recipes.mjs` stays
 * runnable without an ItemsAdder install present.
 *
 * Only ids actually referenced by a crafting station are extracted: the packs
 * hold 14k+ textures, almost none of which any recipe slot will ever show.
 * Existing files are never overwritten -- a name collision is reported and
 * skipped, so a hand-curated sprite always wins.
 */

import { copyFileSync, existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { mkdir, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FRONTEND_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DEFAULT_CONTENTS_DIR = "C:/Users/MSI/Desktop/plugins/ItemsAdder/contents";
const DEFAULT_STATIONS_DIR = "C:/Users/MSI/Desktop/plugins/MMOItems/crafting-stations";

/** Where extracted sprites land, relative to `public/wiki/textures`. */
export const ITEMSADDER_TEXTURE_DIR = "itemsadder";
const OUTPUT_TEXTURE_DIR = path.join(FRONTEND_ROOT, "public", "wiki", "textures", ITEMSADDER_TEXTURE_DIR);
const OUTPUT_MANIFEST = path.join(FRONTEND_ROOT, "app", "wiki", "data", "generated", "itemsadderItems.json");

// ---------------------------------------------------------------------------
// YAML subset parser
// ---------------------------------------------------------------------------

/**
 * Parses an ItemsAdder pack config into plain objects. This is not a general
 * YAML parser; it handles exactly the shape these files use: nested maps by
 * indentation, scalars, and block sequences.
 *
 * The one non-obvious rule: a block sequence may sit at the SAME indent as the
 * key that owns it --
 *
 *     textures:
 *     - item/cards/deck
 *
 * -- as well as indented under it, and both spellings appear across the packs.
 * Popping the stack on `indent <= top` (correct for maps) would detach the
 * first spelling's items from their key and silently lose the texture.
 */
export function parseYamlSubset(text) {
  const root = {};
  const stack = [{ indent: -1, node: root, key: null, parent: null }];
  for (const raw of text.split(/\r?\n/)) {
    if (!raw.trim() || raw.trim().startsWith("#")) continue;
    const indent = raw.length - raw.trimStart().length;
    const body = raw.trim();
    const isListItem = body.startsWith("- ");
    while (
      stack.length > 1 &&
      (isListItem ? indent < stack[stack.length - 1].indent : indent <= stack[stack.length - 1].indent)
    ) {
      stack.pop();
    }
    const top = stack[stack.length - 1];
    if (isListItem) {
      if (!top.parent || top.key == null) continue;
      const existing = top.parent[top.key];
      const list = Array.isArray(existing) ? existing : [];
      list.push(unquote(body.slice(2)));
      top.parent[top.key] = list;
      continue;
    }
    const m = body.match(/^([^:]+):\s*(.*)$/);
    if (!m || !top.node || Array.isArray(top.node)) continue;
    const key = unquote(m[1]);
    const value = m[2].trim();
    if (value === "") {
      const child = {};
      top.node[key] = child;
      stack.push({ indent, node: child, key, parent: top.node });
    } else {
      top.node[key] = unquote(value);
      stack.push({ indent, node: null, key, parent: top.node });
    }
  }
  return root;
}

function unquote(value) {
  const v = value.trim();
  if (v.length >= 2 && ((v[0] === "'" && v.at(-1) === "'") || (v[0] === '"' && v.at(-1) === '"'))) {
    return v.slice(1, -1);
  }
  return v;
}

function isMap(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

/** Strips Minecraft colour/format codes in both the section-sign and `&x` spellings. */
export function stripColours(value) {
  return value
    .replace(/<\/?[^<>]+>/g, "")
    .replace(/[\u00a7&][0-9a-fk-orA-FK-OR]/g, "")
    .trim();
}

// ---------------------------------------------------------------------------
// Pack index
// ---------------------------------------------------------------------------

function yamlFilesIn(dir, out = []) {
  const entries = readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name));
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) yamlFilesIn(full, out);
    else if (entry.name.endsWith(".yml") || entry.name.endsWith(".yaml")) out.push(full);
  }
  return out;
}

/**
 * Every ItemsAdder item declared by every pack, keyed by its bare id.
 *
 * A config declares `info.namespace` once, then item ids under a section (most
 * packs use `items:`; `tfmc_armor` uses its own armour section, so sections are
 * not filtered by name). An item's sprite paths in `resource.textures` are
 * relative to `<pack>/resourcepack/assets/<namespace>/textures/`, with the
 * `.png` extension optional -- both spellings occur. Note the namespace is NOT
 * the pack directory name (`marauder_pack` declares namespace `lzfurniture`),
 * so the declared value is the only correct thing to build a path from.
 *
 * An id can be declared by more than one pack (`pot` appears in three); every
 * declaration is kept so the caller can detect a genuine conflict rather than
 * letting directory order pick a winner.
 */
export function buildPackIndex(contentsDir) {
  const byId = new Map();
  const packs = readdirSync(contentsDir)
    .filter((d) => statSync(path.join(contentsDir, d)).isDirectory())
    .sort();
  for (const pack of packs) {
    for (const file of yamlFilesIn(path.join(contentsDir, pack))) {
      let doc;
      try {
        doc = parseYamlSubset(readFileSync(file, "utf8"));
      } catch {
        continue;
      }
      const namespace = doc?.info?.namespace;
      if (typeof namespace !== "string" || !namespace) continue;
      for (const section of Object.values(doc)) {
        if (!isMap(section)) continue;
        for (const [id, item] of Object.entries(section)) {
          if (!isMap(item)) continue;
          if (item.display_name === undefined && item.resource === undefined) continue;
          const resource = isMap(item.resource) ? item.resource : {};
          let textures = [];
          if (typeof resource.texture === "string") textures = [resource.texture];
          else if (typeof resource.textures === "string") textures = [resource.textures];
          else if (Array.isArray(resource.textures)) {
            textures = resource.textures.filter((t) => typeof t === "string");
          }
          if (!byId.has(id)) byId.set(id, []);
          byId.get(id).push({
            pack,
            namespace,
            id,
            source: path.relative(contentsDir, file).split(path.sep).join("/"),
            name: typeof item.display_name === "string" ? stripColours(item.display_name) : undefined,
            textures,
            modelPath: typeof resource.model_path === "string" ? resource.model_path : undefined,
          });
        }
      }
    }
  }
  return byId;
}

// ---------------------------------------------------------------------------
// Texture resolution
// ---------------------------------------------------------------------------

function texturePath(contentsDir, entry, relative) {
  const rel = relative.endsWith(".png") ? relative : `${relative}.png`;
  const full = path.join(contentsDir, entry.pack, "resourcepack", "assets", entry.namespace, "textures", rel);
  return existsSync(full) ? full : null;
}

/**
 * A per-face texture set resolves to a single icon ONLY when it is provably a
 * vanilla-style log: six faces that reduce, by file CONTENT (not filename --
 * a differently-authored pack could name faces anything), to exactly two
 * distinct images split 4-and-2. Four identical faces are the sides, two
 * identical faces are the end grain -- there is no other block shape that
 * produces that exact split. Vanilla Minecraft draws its own log item icons
 * (`oak_log.png`) from the SIDE texture, never the end (`oak_log_top.png`),
 * so using the 4-face image here is not a substitution, it is the same
 * resolution vanilla already makes for the same shape.
 *
 * Any other split (3/3, 2/2/2, 6 unique, etc.) is a different shape --
 * plausibly a real multi-texture block or, more likely here, a Blockbench
 * furniture UV atlas -- and stays rejected rather than falling back to
 * "pick the most common face".
 */
function resolveLogStyleIcon(contentsDir, entry) {
  if (entry.textures.length !== 6) return null;
  const files = entry.textures.map((t) => texturePath(contentsDir, entry, t));
  if (files.some((f) => !f)) return null;
  const byHash = new Map();
  for (const file of files) {
    const hash = sha256(file);
    if (!byHash.has(hash)) byHash.set(hash, []);
    byHash.get(hash).push(file);
  }
  if (byHash.size !== 2) return null;
  const groups = [...byHash.values()].sort((a, b) => b.length - a.length);
  if (groups[0].length !== 4 || groups[1].length !== 2) return null;
  return groups[0][0];
}

/**
 * The single flat sprite for one pack declaration, or a reason it has none.
 *
 * Three shapes occur:
 *  - exactly one entry in `resource.textures` -- that file IS the item icon;
 *  - several entries -- a per-face block texture set (`*_north`, `*_up`, ...).
 *    Usually a block like this has no single icon among its faces, so picking
 *    one and presenting it as the item sprite would be a guess. Rejected --
 *    EXCEPT the exact 4-sides/2-ends log shape identified by
 *    `resolveLogStyleIcon`, which has a real, unambiguous icon (see there).
 *  - `resource.model_path` and no textures -- a custom model. Read it: a model
 *    whose parent is vanilla `item/generated` (or `item/handheld`) is a flat
 *    sprite wearing a model file, and its single `layer0` IS the icon. A
 *    Blockbench furniture model instead paints a UV atlas across dozens of 3D
 *    faces; that atlas is not an icon and renders as a blob at slot size.
 *    Rejected.
 */
export function resolveEntryTexture(contentsDir, entry) {
  if (entry.textures.length > 1) {
    const logIcon = resolveLogStyleIcon(contentsDir, entry);
    if (logIcon) return { file: logIcon };
    return { reason: `per-face texture set (${entry.textures.length} faces), no single item icon` };
  }
  if (entry.textures.length === 1) {
    const file = texturePath(contentsDir, entry, entry.textures[0]);
    return file ? { file } : { reason: `declared texture not on disk: ${entry.textures[0]}` };
  }
  if (!entry.modelPath) return { reason: "declares neither a texture nor a model" };

  const modelFile = path.join(
    contentsDir,
    entry.pack,
    "resourcepack",
    "assets",
    entry.namespace,
    "models",
    `${entry.modelPath}.json`
  );
  if (!existsSync(modelFile)) return { reason: `model not on disk: ${entry.modelPath}` };
  let model;
  try {
    model = JSON.parse(readFileSync(modelFile, "utf8"));
  } catch {
    return { reason: `model is not valid JSON: ${entry.modelPath}` };
  }
  const parent = typeof model.parent === "string" ? model.parent.replace(/^minecraft:/, "") : "";
  if (parent !== "item/generated" && parent !== "item/handheld") {
    return { reason: `3D model (${entry.modelPath}), no flat item sprite` };
  }
  const layer0 = model.textures?.layer0;
  if (typeof layer0 !== "string") return { reason: `model ${entry.modelPath} has no layer0 texture` };
  const namespaced = layer0.includes(":");
  const ns = namespaced ? layer0.slice(0, layer0.indexOf(":")) : entry.namespace;
  const rel = namespaced ? layer0.slice(layer0.indexOf(":") + 1) : layer0;
  if (ns !== entry.namespace) return { reason: `model texture in another namespace: ${layer0}` };
  const file = texturePath(contentsDir, entry, rel);
  return file ? { file } : { reason: `model texture not on disk: ${layer0}` };
}

function sha256(file) {
  return createHash("sha256").update(readFileSync(file)).digest("hex");
}

/**
 * Collapses every pack declaration of one id into a single name + sprite.
 *
 * Duplicate declarations of the same id are normal (three packs ship `pot`) and
 * are usually identical, so agreement is resolved silently; a genuine
 * disagreement -- two different names, or two byte-different sprites -- is
 * reported and the conflicting field dropped rather than guessed.
 */
export function resolveId(contentsDir, entries) {
  const names = [...new Set(entries.map((e) => e.name).filter(Boolean))].sort();
  const conflicts = [];
  if (names.length > 1) conflicts.push(`conflicting display names: ${names.join(" / ")}`);

  const files = [];
  const reasons = [];
  for (const entry of entries) {
    const result = resolveEntryTexture(contentsDir, entry);
    if (result.file) files.push({ entry, file: result.file, hash: sha256(result.file) });
    else reasons.push(`${entry.pack}: ${result.reason}`);
  }
  const name = names.length === 1 ? names[0] : undefined;
  if (new Set(files.map((f) => f.hash)).size > 1) {
    conflicts.push(`byte-different sprites in ${files.map((f) => f.entry.pack).join(", ")}`);
    return { name, reasons, conflicts };
  }
  return { name, texture: files[0], reasons, conflicts };
}

// ---------------------------------------------------------------------------
// Referenced ids
// ---------------------------------------------------------------------------

/**
 * Every distinct id in an `itemsadder{...}` reference across the station
 * configs, with how many references use it.
 *
 * Attributes are separated by `,` OR `;` -- both appear -- and ids may be
 * namespaced (`tfmc_blocks:mythril_block3`) or bare, so the namespace is
 * stripped here: the manifest is keyed by bare id, which is what the packs
 * themselves key on.
 */
export function collectReferencedIds(stationsDir) {
  const counts = new Map();
  for (const file of readdirSync(stationsDir).filter((f) => f.endsWith(".yml")).sort()) {
    const text = readFileSync(path.join(stationsDir, file), "utf8");
    for (const match of text.matchAll(/itemsadder\{([^}]*)\}/g)) {
      const id = match[1].match(/(?:^|[,;])\s*id=([^,;]+)/)?.[1]?.trim();
      if (!id) continue;
      const bare = id.includes(":") ? id.slice(id.indexOf(":") + 1) : id;
      counts.set(bare, (counts.get(bare) ?? 0) + 1);
    }
  }
  return counts;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const contentsDir = process.argv[2] ?? DEFAULT_CONTENTS_DIR;
  const stationsDir = process.argv[3] ?? DEFAULT_STATIONS_DIR;
  for (const [label, dir] of [["ItemsAdder contents", contentsDir], ["crafting stations", stationsDir]]) {
    if (!existsSync(dir) || !statSync(dir).isDirectory()) {
      console.error(
        `\nextract-itemsadder-textures: ${label} directory not found:\n  ${dir}\n\n` +
          "Both live outside this repository. Pass them explicitly:\n" +
          "  node scripts/extract-itemsadder-textures.mjs <ItemsAdder/contents> <MMOItems/crafting-stations>\n"
      );
      process.exit(1);
    }
  }

  const referenced = collectReferencedIds(stationsDir);
  const packIndex = buildPackIndex(contentsDir);
  await mkdir(OUTPUT_TEXTURE_DIR, { recursive: true });

  const manifest = {};
  const lines = [];
  let copied = 0;
  let kept = 0;
  for (const [id, count] of [...referenced].sort(([a], [b]) => a.localeCompare(b))) {
    const entries = packIndex.get(id);
    if (!entries?.length) {
      lines.push(`SKIP      ${id} (x${count}) -- declared by no pack`);
      continue;
    }
    const { name, texture, reasons, conflicts } = resolveId(contentsDir, entries);
    for (const conflict of conflicts) lines.push(`CONFLICT  ${id}: ${conflict}`);
    const record = {};
    if (name) record.name = name;

    if (texture) {
      const destName = `${id}.png`;
      const dest = path.join(OUTPUT_TEXTURE_DIR, destName);
      if (existsSync(dest)) {
        if (sha256(dest) === texture.hash) {
          kept += 1;
          lines.push(`UNCHANGED ${id} (x${count}) -> ${ITEMSADDER_TEXTURE_DIR}/${destName}`);
        } else {
          lines.push(`EXISTS    ${id} (x${count}) -- ${ITEMSADDER_TEXTURE_DIR}/${destName} differs, not overwritten`);
        }
      } else {
        copyFileSync(texture.file, dest);
        copied += 1;
        lines.push(
          `COPY      ${id} (x${count}) <- ${texture.entry.pack}:${texture.entry.source} ` +
            `-> ${ITEMSADDER_TEXTURE_DIR}/${destName}`
        );
      }
      record.texture = `${ITEMSADDER_TEXTURE_DIR}/${destName}`;
    } else {
      lines.push(`SKIP      ${id} (x${count}) -- ${reasons.join(" | ")}`);
    }
    if (Object.keys(record).length) manifest[id] = record;
  }

  const ordered = {};
  for (const id of Object.keys(manifest).sort()) ordered[id] = manifest[id];
  await mkdir(path.dirname(OUTPUT_MANIFEST), { recursive: true });
  await writeFile(OUTPUT_MANIFEST, `${JSON.stringify(ordered, null, 2)}\n`, "utf8");

  for (const line of lines) console.log(line);
  const withTexture = Object.values(ordered).filter((r) => r.texture).length;
  console.log(
    `\n${referenced.size} referenced ItemsAdder ids; ${withTexture} with a sprite ` +
      `(${copied} copied, ${kept} already present); ` +
      `manifest: ${path.relative(FRONTEND_ROOT, OUTPUT_MANIFEST).split(path.sep).join("/")}`
  );
}
