import os

from PIL import Image, ImageChops, ImageEnhance, ImageFilter

from ..util.dirs import (
    input_file,
    paper_texture_asset,
    parchment_image,
    validate_map,
)

# Step 39.02 ink cartography — tune in visual pass if needed.
PAPER_HIGH = (240, 230, 210)  # #f0e6d2
PAPER_MID = (212, 196, 168)  # #d4c4a8
PAPER_SHADOW = (139, 115, 85)  # #8b7355
INK_DARK = (42, 31, 20)  # #2a1f14

EDGE_OPACITY = 0.55
EDGE_THRESHOLD = 28
CONTRAST_FACTOR = 1.28
GRAIN_BLEND = 0.15
VIGNETTE_STRENGTH = 0.12
VIGNETTE_MASK_SIZE = 512


def _validate_map_background(map_name: str) -> str | None:
    map_path = input_file(map_name, "map.png")
    provinces_path = input_file(map_name, "provinces.png")

    if not os.path.exists(map_path):
        return "map.png missing"
    if not os.path.exists(provinces_path):
        return "provinces.png missing"

    with Image.open(map_path) as map_img, Image.open(provinces_path) as provinces_img:
        if map_img.size != provinces_img.size:
            return (
                f"size mismatch: map.png {map_img.size} "
                f"vs provinces.png {provinces_img.size}"
            )

    return None


def _remove_stale_parchment(map_name: str) -> None:
    out_path = parchment_image(map_name)
    if os.path.exists(out_path):
        os.remove(out_path)


def _tile_texture(size: tuple[int, int], texture: Image.Image) -> Image.Image:
    tiled = Image.new("RGB", size)
    tw, th = texture.size
    for y in range(0, size[1], th):
        for x in range(0, size[0], tw):
            tiled.paste(texture, (x, y))
    return tiled


def _lerp_rgb(
    a: tuple[int, int, int], b: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _remap_luminance_value(v: int) -> tuple[int, int, int]:
    v = max(0, min(255, v))
    if v <= 128:
        t = v / 128.0 if v > 0 else 0.0
        return _lerp_rgb(PAPER_SHADOW, PAPER_MID, t)
    t = (v - 128) / 127.0
    return _lerp_rgb(PAPER_MID, PAPER_HIGH, t)


def _build_remap_luts() -> tuple[list[int], list[int], list[int]]:
    r_lut: list[int] = []
    g_lut: list[int] = []
    b_lut: list[int] = []
    for v in range(256):
        r, g, b = _remap_luminance_value(v)
        r_lut.append(r)
        g_lut.append(g)
        b_lut.append(b)
    return r_lut, g_lut, b_lut


_REMAP_LUT_R, _REMAP_LUT_G, _REMAP_LUT_B = _build_remap_luts()


def _luminance(img: Image.Image) -> Image.Image:
    return img.convert("L", (0.299, 0.587, 0.114, 0))


def _remap_luminance(gray: Image.Image) -> Image.Image:
    return Image.merge(
        "RGB",
        (
            gray.point(_REMAP_LUT_R),
            gray.point(_REMAP_LUT_G),
            gray.point(_REMAP_LUT_B),
        ),
    )


def _apply_ink_edges(base: Image.Image, luma: Image.Image) -> Image.Image:
    edges = luma.filter(ImageFilter.FIND_EDGES)
    edge_mask = edges.point(lambda p: 255 if p >= EDGE_THRESHOLD else 0)
    ink_layer = Image.new("RGB", base.size, INK_DARK)
    ink_on_edges = Image.composite(ink_layer, base, edge_mask)
    return Image.blend(base, ink_on_edges, EDGE_OPACITY)


def _apply_grain(img: Image.Image) -> Image.Image:
    texture_path = paper_texture_asset()
    if not os.path.exists(texture_path):
        print(f"⚠️ Paper texture missing at {texture_path}; skipping texture step")
        return img

    with Image.open(texture_path) as texture_img:
        texture = texture_img.convert("RGB")
    tiled = _tile_texture(img.size, texture)
    # Neutralize toward mid-gray so multiply adds grain without crushing midtones.
    neutral = Image.new("RGB", img.size, (128, 128, 128))
    grain = ImageChops.multiply(img.convert("RGB"), Image.blend(neutral, tiled, 0.5))
    return Image.blend(img.convert("RGB"), grain, GRAIN_BLEND)


def _radial_vignette_mask(size: tuple[int, int]) -> Image.Image:
    mask_size = VIGNETTE_MASK_SIZE
    cx = cy = mask_size // 2
    max_dist = (cx ** 2 + cy ** 2) ** 0.5

    small = Image.new("L", (mask_size, mask_size))
    pixels = small.load()
    for y in range(mask_size):
        for x in range(mask_size):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / max_dist
            edge = min(1.0, dist ** 1.5)
            pixels[x, y] = int(255 * (1.0 - VIGNETTE_STRENGTH * edge))

    return small.resize(size, Image.Resampling.LANCZOS)


def _apply_vignette(img: Image.Image) -> Image.Image:
    mask = _radial_vignette_mask(img.size)
    darkened = ImageChops.multiply(
        img.convert("RGB"), Image.merge("RGB", (mask, mask, mask))
    )
    return Image.blend(img.convert("RGB"), darkened, VIGNETTE_STRENGTH)


def _grade_parchment(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    luma = _luminance(rgb)
    graded = _remap_luminance(luma)
    graded = ImageEnhance.Contrast(graded).enhance(CONTRAST_FACTOR)
    graded = _apply_ink_edges(graded, luma)
    graded = _apply_grain(graded)
    graded = _apply_vignette(graded)
    return graded.convert("RGBA")


def create_parchment_base(map_name: str) -> bool:
    """Grade map.png into parchment_base.png. Returns True when output was written."""
    validate_map(map_name)

    reason = _validate_map_background(map_name)
    if reason:
        print(f"⚠️ Skipping parchment: {reason}")
        _remove_stale_parchment(map_name)
        return False

    map_path = input_file(map_name, "map.png")
    out_path = parchment_image(map_name)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with Image.open(map_path) as source:
        parchment = _grade_parchment(source)
        parchment.save(out_path, "PNG")

    print(f"📜 [{map_name}] Parchment base generated → {out_path}")
    return True
