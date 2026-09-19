"""Guards for route parameters that end up in a filesystem path.

Two layers, used together by every route that joins a path or query parameter
into a path:

1. The parameter itself must match a strict pattern *before* any path is built.
   Nothing is stripped or rewritten: a value that does not match is rejected.
   This matters on Windows in particular, where Starlette decodes `%5C` to `\\`
   and the OS treats it as a separator, so `..%5C..%5C.env` is a single path
   segment to the router but a traversal to the filesystem.
2. The built path is resolved and must still sit inside the root it was built
   under. This is the backstop for anything the pattern did not anticipate
   (symlinks, a future pattern that is looser than intended).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

# One path segment: no dots, no separators, nothing Windows would reinterpret.
_SAFE_SEGMENT_RE = re.compile(r"[A-Za-z0-9_\-]+")

# A file name: safe segments joined by single dots ("x.png", "a_b.json").
# No leading dot, no empty segment, so "." / ".." / ".env" can never match.
_SAFE_FILENAME_RE = re.compile(r"[A-Za-z0-9_\-]+(?:\.[A-Za-z0-9_\-]+)*")


def is_safe_segment(value: object) -> bool:
    return isinstance(value, str) and _SAFE_SEGMENT_RE.fullmatch(value) is not None


def is_safe_filename(value: object) -> bool:
    return isinstance(value, str) and _SAFE_FILENAME_RE.fullmatch(value) is not None


def resolve_within(root: str | os.PathLike[str], path: str | os.PathLike[str]) -> Path | None:
    """`path` resolved, or None when it does not resolve to inside `root`."""
    try:
        resolved_root = Path(root).resolve()
        resolved = Path(path).resolve()
    except (OSError, RuntimeError, ValueError):
        return None
    if resolved == resolved_root or not resolved.is_relative_to(resolved_root):
        return None
    return resolved
