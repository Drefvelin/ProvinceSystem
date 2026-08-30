"""Lossy WebP copies of large map images, cached on disk.

The satellite base map is a 6400x6400 PNG of dense terrain — ~34 MB, and it is
the single biggest thing the map page downloads. WebP cuts that substantially,
but encoding it takes ~25s, so it is never done inside a request: a request
either finds a ready copy or serves the original PNG and kicks off the encode in
the background for next time.

Only offered to clients that advertise WebP support, and only for images that
are purely displayed. Never use this for `provinces.png` or anything else read
back pixel-by-pixel — lossy encoding changes RGB values and would corrupt
province id lookups.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import threading
from pathlib import Path

# Measured on the 6400x6400 main map (34.5 MB PNG):
#   q=75 method=4 -> 9.8 MB in 26s;  q=75 method=6 -> 9.7 MB in 54s
# method 6 buys almost nothing for double the time, and quality above 75
# grows fast (q=90 -> 16.7 MB) with little visible gain on terrain.
_QUALITY = 75
_METHOD = 4

_ROUTER_DIR = Path(__file__).resolve().parent
_CACHE_DIR = _ROUTER_DIR.parent / "output" / "_derived" / "webp"

_encoding: set[str] = set()
_encoding_lock = threading.Lock()


def cache_path_for(source: os.PathLike[str] | str) -> Path:
    """Stable cache location for a source image.

    Keyed by absolute source path; freshness is decided by mtime at read time,
    so a regenerated map simply invalidates itself.
    """
    key = hashlib.sha1(
        str(Path(source).resolve()).encode("utf-8"), usedforsecurity=False
    ).hexdigest()
    return _CACHE_DIR / f"{key}.webp"


def _is_fresh(source: Path, cached: Path) -> bool:
    try:
        return cached.stat().st_mtime >= source.stat().st_mtime
    except OSError:
        return False


def _encode(source: Path, target: Path) -> None:
    from PIL import Image

    target.parent.mkdir(parents=True, exist_ok=True)
    # Encode to a unique temp name and rename, so a reader never sees a partial
    # file. The name has to be unique per encode, not just per process: two
    # threads sharing one name race, and on Windows the rename then fails with
    # "file is being used by another process".
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, suffix=".tmp")
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        with Image.open(source) as image:
            image.load()
            image.save(tmp, "WEBP", quality=_QUALITY, method=_METHOD)
        os.replace(tmp, target)
    except BaseException:
        # Only clean up on failure; on success the temp file has been renamed
        # away and unlinking would delete the finished cache entry.
        tmp.unlink(missing_ok=True)
        raise


def _encode_in_background(source: Path, target: Path) -> None:
    key = str(target)
    with _encoding_lock:
        if key in _encoding:
            return
        _encoding.add(key)

    def run() -> None:
        try:
            _encode(source, target)
        except Exception as exc:  # pragma: no cover - background best effort
            print(f"[webp] encode failed for {source}: {exc}")
        finally:
            with _encoding_lock:
                _encoding.discard(key)

    threading.Thread(target=run, name="webp-encode", daemon=True).start()


def client_accepts_webp(accept: str | None) -> bool:
    return isinstance(accept, str) and "image/webp" in accept.lower()


def webp_variant(
    source: os.PathLike[str] | str,
    *,
    accept: str | None,
    background: bool = True,
) -> Path | None:
    """Return a ready WebP copy of `source`, or None to serve the original.

    Returns None when the client cannot display WebP, or when no fresh copy
    exists yet — in the latter case an encode is started so the next request can
    be served the smaller file.
    """
    if not client_accepts_webp(accept):
        return None

    source_path = Path(source)
    cached = cache_path_for(source_path)
    if _is_fresh(source_path, cached):
        return cached

    if background:
        _encode_in_background(source_path, cached)
    else:
        _encode(source_path, cached)
        return cached
    return None
