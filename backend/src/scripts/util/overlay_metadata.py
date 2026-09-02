import json
import os
from typing import Any

from PIL import Image

from .atomic import _write_atomic
from .dirs import region_overlay_file


def rgb_tuple_to_str(color: tuple[int, ...]) -> str:
    return ",".join(str(c) for c in color[:3])


def crop_to_content(
    img: Image.Image, pad: int = 2
) -> tuple[Image.Image, dict[str, int] | None]:
    alpha = img.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return img, None

    left, top, right, bottom = bbox
    width, height = img.size

    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(width, right + pad)
    bottom = min(height, bottom + pad)

    cropped = img.crop((left, top, right, bottom))
    return cropped, {
        "x": left,
        "y": top,
        "w": right - left,
        "h": bottom - top,
    }


def save_cropped(img: Image.Image, path: str, pad: int = 2) -> dict[str, int] | None:
    cropped, meta = crop_to_content(img, pad=pad)
    cropped.save(path, "PNG")
    cropped.close()
    return meta


def load_overlay_metadata(map_name: str, mode: str) -> dict[str, dict[str, Any]]:
    """This mode's crop boxes, keyed by `"r,g,b"`.

    Empty when the sidecar is absent or unreadable, which is the honest answer
    for a mode whose regions have never been generated: the map then draws no
    overlay rather than positioning a PNG that does not exist.
    """
    path = region_overlay_file(map_name, mode)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}

    if not isinstance(data, dict):
        return {}

    return {
        rgb: entry
        for rgb, entry in data.items()
        if isinstance(rgb, str) and isinstance(entry, dict)
    }


def write_overlay_metadata(
    map_name: str,
    mode: str,
    metadata_by_rgb: dict[str, dict[str, Any]],
    merge: bool,
) -> None:
    """Record where this mode's cropped region PNGs sit on the full map.

    `merge` follows the regen that produced the boxes. A queued regen only
    repaints the regions in the queue, so replacing the file would drop every
    box it did not touch and blank those overlays on the map. A full regen
    repaints everything, so replacing is what prunes the boxes of regions that
    no longer exist.
    """
    path = region_overlay_file(map_name, mode)

    data = load_overlay_metadata(map_name, mode) if merge else {}
    if not data and not metadata_by_rgb and not os.path.exists(path):
        # Nothing to record and nothing recorded before: leave the tree alone
        # rather than planting an empty sidecar. An existing file is still
        # rewritten, so a full regen that paints nothing prunes it.
        return
    data.update(metadata_by_rgb)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)
    _write_atomic(path, body.encode("utf-8"), prefix=".overlays-")

    print(f"✅ Wrote overlay metadata for {len(metadata_by_rgb)} regions in '{mode}'")
