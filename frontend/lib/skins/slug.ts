const SLUG_RE = /^[a-z][a-z0-9_]{1,47}$/;

const RESERVED = new Set([
  "test",
  "texture",
  "null",
  "undefined",
  "admin",
  "tfmc",
]);

export function slugifyDisplayName(displayName: string): string {
  let s = displayName.toLowerCase();
  s = s.replace(/[^a-z0-9]+/g, "_");
  s = s.replace(/_+/g, "_");
  s = s.replace(/^_+|_+$/g, "");
  if (!s || /^\d/.test(s)) {
    s = `skin_${s}`;
  }
  if (s.length > 48) {
    s = s.slice(0, 48).replace(/_+$/g, "");
  }
  return s;
}

export function assertSlugClient(slug: string): void {
  const s = (slug || "").trim();
  if (!SLUG_RE.test(s)) {
    throw new Error(
      "Slug must be 2–48 chars: start with a letter, then lowercase letters, numbers, underscores"
    );
  }
  if (s.includes("__")) {
    throw new Error("Slug cannot contain double underscores");
  }
  if (RESERVED.has(s)) {
    throw new Error(`Slug '${s}' is reserved`);
  }
}
