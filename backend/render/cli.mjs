import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const here = path.dirname(fileURLToPath(import.meta.url));

function readDataUrl(filePath, mime) {
  const buf = fs.readFileSync(filePath);
  return `data:${mime};base64,${buf.toString("base64")}`;
}

function fileToAsset(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".png") return readDataUrl(filePath, "image/png");
  return fs.readFileSync(filePath, "utf8");
}

async function main() {
  const jobPath = process.argv[2];
  if (!jobPath) {
    console.error("Usage: node cli.mjs <job.json>");
    process.exit(2);
  }
  const job = JSON.parse(fs.readFileSync(jobPath, "utf8").replace(/^\uFEFF/, ""));
  const outDir = job.outDir;
  if (!outDir) {
    console.error("job.outDir is required");
    process.exit(2);
  }
  const bundle = path.join(here, "dist", "browser.js");
  if (!fs.existsSync(bundle)) {
    console.error("render bundle missing; run npm install in backend/render");
    process.exit(3);
  }

  const assets = {};
  for (const [key, filePath] of Object.entries(job.files || {})) {
    if (!filePath || !fs.existsSync(filePath)) continue;
    assets[key] = fileToAsset(filePath);
  }

  const browser = await chromium.launch({
    headless: true,
    args: ["--disable-gpu-sandbox"],
  });
  try {
    const page = await browser.newPage({
      viewport: { width: 256, height: 256 },
    });
    await page.setContent(
      `<!DOCTYPE html><html><body><div id="host"></div></body></html>`,
      { waitUntil: "load" }
    );
    await page.addScriptTag({ path: bundle });
    const pngs = await page.evaluate(
      async (payload) => {
        if (typeof window.renderPreviewJob !== "function") {
          throw new Error("renderPreviewJob not loaded");
        }
        return window.renderPreviewJob(payload);
      },
      {
        kind: job.kind,
        views: job.views || ["model"],
        assets,
        width: job.width || 256,
        height: job.height || 256,
      }
    );
    fs.mkdirSync(outDir, { recursive: true });
    for (const [view, dataUrl] of Object.entries(pngs || {})) {
      if (typeof dataUrl !== "string" || !dataUrl.startsWith("data:image/png")) {
        continue;
      }
      const b64 = dataUrl.split(",", 2)[1];
      fs.writeFileSync(
        path.join(outDir, `preview_${view}.png`),
        Buffer.from(b64, "base64")
      );
    }
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
