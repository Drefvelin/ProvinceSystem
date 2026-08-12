/** Inline Minecraft/TLibs-style colour runs for lore / name preview. */

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

/** Prepend §7 when the line has no leading colour (matches API / in-game apply).

 * Format codes alone (§l / &l) are not colours — still prepend §7.
 */
export function ensureLoreGray(line: string): string {
  const s = line.trim();
  if (!s) return s;
  if (hasLeadingLoreColour(s)) return s;
  return `§7${s}`;
}

function hasLeadingLoreColour(line: string): boolean {
  if (!line) return false;
  if ((line[0] === "§" || line[0] === "&") && line.length >= 2) {
    const code = line[1]!.toLowerCase();
    return "0123456789abcdef".includes(code);
  }
  if (line[0] === "#" && line.length >= 7) {
    return /^#[0-9A-Fa-f]{6}/.test(line);
  }
  return false;
}

export function hasInlineFormatCodes(raw: string): boolean {
  const s = String(raw || "");
  if (/[§&][0-9a-fk-or]/i.test(s)) return true;
  if (/#[0-9A-Fa-f]{6}/.test(s)) return true;
  return false;
}

/**
 * Parse a lore line into coloured runs (inline codes mid-line).
 * Supports §x / &x, §l/§o/§n/§m/§r, and #RRGGBB.
 */
export function parseLoreRuns(raw: string): LoreRun[] {
  return parseInlineRuns(ensureLoreGray(raw), "#aaaaaa");
}

/**
 * Parse item name with the same §/&/# codes as lore.
 * Does not force gray — default is white for names.
 */
export function parseNameRuns(raw: string): LoreRun[] {
  return parseInlineRuns(String(raw || ""), "#ffffff");
}

function parseInlineRuns(line: string, defaultColor: string): LoreRun[] {
  const runs: LoreRun[] = [];
  let color = defaultColor;
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
        color = defaultColor;
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
