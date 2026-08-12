/** Inline Minecraft/TLibs-style colour runs for lore preview. */

import { LEGACY_PALETTE } from "../skins/namePreview";

export type LoreRun = {
  text: string;
  color: string;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  strike?: boolean;
};

const LEGACY = new Map(LEGACY_PALETTE.map((p) => [p.code, p.hex]));

function normalizeHex(raw: string): string | null {
  const t = raw.trim();
  if (/^#[0-9A-Fa-f]{6}$/.test(t)) return t.toLowerCase();
  if (/^[0-9A-Fa-f]{6}$/.test(t)) return `#${t.toLowerCase()}`;
  return null;
}

/** Prepend §7 when the line has no leading colour (matches API normalize). */
export function ensureLoreGray(line: string): string {
  const s = line.trim();
  if (!s) return s;
  if (s[0] === "§" || s[0] === "&") return s;
  if (s[0] === "#" && /^#[0-9A-Fa-f]{6}/.test(s)) return s;
  return `§7${s}`;
}

/**
 * Parse a lore line into coloured runs (inline codes mid-line).
 * Supports §x / &x, §l/§o/§n/§m/§r, and #RRGGBB.
 */
export function parseLoreRuns(raw: string): LoreRun[] {
  const line = ensureLoreGray(raw);
  const runs: LoreRun[] = [];
  let color = "#aaaaaa";
  let bold = false;
  let italic = false;
  let underline = false;
  let strike = false;
  let buf = "";

  const flush = () => {
    if (!buf) return;
    runs.push({ text: buf, color, bold, italic, underline, strike });
    buf = "";
  };

  let i = 0;
  while (i < line.length) {
    const ch = line[i]!;
    if ((ch === "§" || ch === "&") && i + 1 < line.length) {
      const code = line[i + 1]!.toLowerCase();
      flush();
      if (code === "l") bold = true;
      else if (code === "o") italic = true;
      else if (code === "n") underline = true;
      else if (code === "m") strike = true;
      else if (code === "r") {
        color = "#aaaaaa";
        bold = italic = underline = strike = false;
      } else if (LEGACY.has(code)) {
        color = LEGACY.get(code)!;
        bold = italic = underline = strike = false;
      }
      i += 2;
      continue;
    }
    if (ch === "#" && i + 6 < line.length) {
      const hex = normalizeHex(line.slice(i, i + 7));
      if (hex) {
        flush();
        color = hex;
        bold = italic = underline = strike = false;
        i += 7;
        continue;
      }
    }
    buf += ch;
    i += 1;
  }
  flush();
  return runs;
}
