import json
import os
from typing import Any

from PIL import Image

from .dirs import defines_file


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


def merge_overlay_metadata(
    map_name: str,
    mode: str,
    metadata_by_rgb: dict[str, dict[str, Any]],
) -> None:
    if not metadata_by_rgb:
        return

    path = defines_file(map_name, f"{mode}.json")
    if not os.path.exists(path):
        print(f"⚠️ No defines file for mode '{mode}', skipping overlay metadata merge.")
        return

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for region in data.values():
        if not isinstance(region, dict):
            continue
        rgb = region.get("rgb")
        if not rgb or rgb not in metadata_by_rgb:
            continue
        region.update(metadata_by_rgb[rgb])
        updated += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Merged overlay metadata for {updated} regions in '{mode}'")
