import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const renderRoot = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceDir = path.join(renderRoot, "../../frontend/lib/skins");
const destDir = path.join(renderRoot, "src/skins");

const files = [
  "displayTransform.ts",
  "extrudeItem.ts",
  "javaModel.ts",
  "steveMannequin.ts",
];

function destReady() {
  return files.every((name) => fs.existsSync(path.join(destDir, name)));
}

if (!fs.existsSync(sourceDir)) {
  if (destReady()) {
    process.exit(0);
  }
  console.error(
    "sync-skins: frontend/lib/skins is missing and backend/render/src/skins is not populated"
  );
  process.exit(1);
}

fs.mkdirSync(destDir, { recursive: true });
for (const name of files) {
  fs.copyFileSync(path.join(sourceDir, name), path.join(destDir, name));
}
