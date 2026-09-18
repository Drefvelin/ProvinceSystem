"""Stamp every /wiki page with the date its content last changed.

For each app/wiki/**/page.tsx this collects the page's own folder plus every wiki data file it
imports (followed recursively, including generated JSON), asks git for the newest commit that
touched any of them, and writes that date as the page's `lastModified` prop. Files with
uncommitted changes count as modified today.

Shared plumbing (data/index.ts, registry.ts, types.ts, helpers.ts) is skipped, otherwise one
edit there would mark the whole wiki as changed. The recipe database (station-recipes.ts,
items.ts, generated/) is shared too: it only counts for the pages that are built from it
(stations, items, materials), not for a page that happens to show a couple of recipes.

Run from frontend/:  python scripts/update-wiki-last-modified.py [--check]
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[1]
WIKI = FRONTEND / "app" / "wiki"
DATA = WIKI / "data"
SHARED = {DATA / n for n in ("index.ts", "registry.ts", "types.ts", "helpers.ts")}

RECIPE_DB = (DATA / "station-recipes.ts", DATA / "items.ts", DATA / "generated")
RECIPE_PAGES = ("stations", "items", "materials")


def is_recipe_db(f: Path) -> bool:
    return any(f == r or r in f.parents for r in RECIPE_DB)


IMPORT_RE = re.compile(r"""(?:import|export)\s+(?:type\s+)?(?:([^'";]*?)\s+from\s+)?["']([^"']+)["']""")
PROP_RE = re.compile(r"""\s+last(?:Modified|Verified)=(?:"[^"]*"|\{[^}]*\})""")
TAG_RE = re.compile(r"<WikiPage\b")


def resolve(spec: str, importer: Path) -> Path | None:
    if spec.startswith("@/"):
        base = FRONTEND / spec[2:]
    elif spec.startswith("."):
        base = (importer.parent / spec).resolve()
    else:
        return None
    for cand in (base, *(base.with_name(base.name + ext) for ext in (".ts", ".tsx", ".json")),
                 base / "index.ts"):
        if cand.is_file():
            return cand
    return None


def barrel_targets(names: str, barrel: Path) -> list[Path]:
    """Map `{ a, b }` imported from the data barrel to the modules that define them."""
    wanted = {n.strip().split(" as ")[0].replace("type ", "").strip()
              for n in names.strip("{} \n").split(",") if n.strip()}
    out: list[Path] = []
    for spec in re.findall(r"""export\s+\*\s+from\s+["']([^"']+)["']""", barrel.read_text("utf-8")):
        mod = resolve(spec, barrel)
        if not mod or mod in SHARED:
            continue
        text = mod.read_text("utf-8")
        if any(re.search(rf"export\s+(?:const|function|type|interface|enum)\s+{re.escape(n)}\b", text)
               for n in wanted):
            out.append(mod)
    return out


def dependencies(page: Path) -> set[Path]:
    seen: set[Path] = set()
    uses_recipe_db = page.relative_to(WIKI).parts[0] in RECIPE_PAGES
    if page.parent == WIKI:
        # The guide's front page is its own file plus the page list it renders.
        seen.add(DATA / "registry.ts")
        todo = [page]
    else:
        todo = [p for p in page.parent.rglob("*") if p.is_file() and "test" not in p.name]
    while todo:
        f = todo.pop()
        if f in seen or f in SHARED or WIKI not in f.parents:
            continue
        if is_recipe_db(f) and not uses_recipe_db:
            continue
        seen.add(f)
        if f.suffix not in (".ts", ".tsx"):
            continue
        for names, spec in IMPORT_RE.findall(f.read_text("utf-8")):
            target = resolve(spec, f)
            if target is None:
                continue
            if target == DATA / "index.ts":
                todo.extend(barrel_targets(names or "", target))
            else:
                todo.append(target)
    return seen


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=FRONTEND, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def without_stamp(text: str) -> str:
    return PROP_RE.sub("", text.replace("\r\n", "\n"))


def really_changed(rel: str) -> bool:
    """Uncommitted change that is more than this script's own date stamp."""
    try:
        committed = git("show", f"HEAD:frontend/{rel}")
    except subprocess.CalledProcessError:
        return True  # new, untracked file
    current = (FRONTEND / rel).read_text("utf-8")
    return without_stamp(committed) != without_stamp(current)


def last_changed(files: set[Path]) -> str:
    rel = sorted(str(f.relative_to(FRONTEND)).replace("\\", "/") for f in files)
    dirty = [line[3:].strip().strip('"') for line in
             git("status", "--porcelain", "--", *rel).splitlines()]
    # git prints paths relative to the repo root; ours are relative to frontend/.
    if any(really_changed(d.removeprefix("frontend/")) for d in dirty):
        return date.today().isoformat()
    return git("log", "-1", "--format=%ad", "--date=short", "--", *rel).strip()


def main() -> int:
    check = "--check" in sys.argv
    stale = 0
    for page in sorted(WIKI.rglob("page.tsx")):
        text = open(page, encoding="utf-8", newline="").read()
        tags = list(TAG_RE.finditer(text))
        if len(tags) != 1:
            print(f"skip  {page.relative_to(WIKI)} ({len(tags)} <WikiPage> tags)")
            continue
        stamp = last_changed(dependencies(page))
        if not stamp:
            print(f"skip  {page.relative_to(WIKI)} (no git history)")
            continue
        start = tags[0].end()
        # Only touch props inside the opening tag: stop at the first ">" that ends a line or
        # is followed by a child, which is safe because props never contain a bare "\n>" pair.
        end = re.compile(r">\r?\n").search(text, start)
        head_end = end.start() if end else len(text)
        head = PROP_RE.sub("", text[start:head_end])
        # Multi-line tag: give the prop its own line, indented like its neighbours.
        multiline = re.match(r"(\r?\n)([ \t]*)", head)
        prop = f'lastModified="{stamp}"'
        insert = f"{multiline.group(1)}{multiline.group(2)}{prop}" if multiline else f" {prop}"
        updated = text[:start] + insert + head + text[head_end:]
        state = "ok   " if updated == text else "stale" if check else "write"
        print(f"{state} {stamp}  {page.relative_to(WIKI)}")
        if updated != text:
            stale += 1
            if not check:
                open(page, "w", encoding="utf-8", newline="").write(updated)
    return 1 if check and stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
