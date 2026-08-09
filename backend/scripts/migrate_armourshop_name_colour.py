"""Migrate ArmourShop YAML: peel leading colour from name into colour field."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOTS = [
    Path(r"D:\Documents\TFMC\Workspace\plugins\ArmourShop"),
    Path(r"D:\Documents\TFMC\Workspace\armourshop\src\main\resources"),
]

# name: "#aabbccText" or "§aText" or "§#aabbccText" or '#aabbccText'
NAME_LINE = re.compile(
    r'^(\s*)name:\s*(["\']?)(.+?)\2\s*$'
)


def peel(raw: str) -> tuple[str, str | None]:
    s = raw.strip()
    # Unquote if whole string still quoted oddly
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]

    # §#RRGGBBrest
    m = re.match(r"^§#([0-9A-Fa-f]{6})(.*)$", s)
    if m:
        return (m.group(2).strip() or s, "#" + m.group(1).lower())

    # #RRGGBBrest
    m = re.match(r"^#([0-9A-Fa-f]{6})(.*)$", s)
    if m:
        return (m.group(2).strip() or s, "#" + m.group(1).lower())

    # §Xrest or &Xrest (single legacy code)
    m = re.match(r"^[§&]([0-9A-Fa-fk-or])(.*)$", s, re.IGNORECASE)
    if m:
        return (m.group(2).strip() or s, "§" + m.group(1).lower())

    return s, None


def migrate_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    changed = False
    i = 0
    while i < len(lines):
        line = lines[i]
        m = NAME_LINE.match(line.rstrip("\n\r"))
        if not m:
            out.append(line)
            i += 1
            continue

        indent, _q, value = m.group(1), m.group(2), m.group(3)
        plain, colour = peel(value)

        # Skip if already has colour on next non-empty lines in same block? check following lines
        look = i + 1
        has_colour = False
        while look < len(lines):
            nxt = lines[look]
            if not nxt.strip():
                look += 1
                continue
            if re.match(r"^\s+colour\s*:", nxt) or re.match(r"^\s+color\s*:", nxt):
                has_colour = True
            break

        if colour and not has_colour:
            out.append(f'{indent}name: "{plain}"\n')
            out.append(f'{indent}colour: "{colour}"\n')
            changed = True
        elif colour and has_colour:
            # still clean name if needed
            if plain != value.strip().strip("\"'"):
                out.append(f'{indent}name: "{plain}"\n')
                changed = True
            else:
                out.append(line)
        else:
            # ensure quoted plain name
            if line.rstrip("\n\r") != f'{indent}name: "{plain}"':
                out.append(f'{indent}name: "{plain}"\n')
                if f'{indent}name: "{plain}"\n' != line:
                    changed = True
            else:
                out.append(line)
        i += 1

    if changed:
        path.write_text("".join(out), encoding="utf-8", newline="\n")
    return changed


def main() -> None:
    n = 0
    for root in ROOTS:
        if not root.exists():
            print("missing", root)
            continue
        for path in list(root.glob("*.yml")) + list(root.glob("Categories/*.yml")):
            if migrate_file(path):
                print("migrated", path)
                n += 1
    print(f"done, {n} files changed")


if __name__ == "__main__":
    main()
