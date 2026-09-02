from PIL import Image
import os
import sys
import time

from ..util.border_paint import (
    apply_occupation_seam_dashes,
    apply_opaque_union_borders,
    border_color_for_fill,
    border_thickness as default_border_thickness,
)
from ..util.colour_mapping import build_color_mapping, get_color_overrides
from ..util.display_colour import display_rgb, hover_rgb, occupation_display_rgb
from ..util.overlay_metadata import (
    rgb_tuple_to_str,
    save_cropped,
    write_overlay_metadata,
)
from ..util.queue import load_queue, compile_queue, clear_mode
from ..util.dirs import input_file, validate_map
from .geometry_cache import MapGeometryCache


def log_progress(message: str):
    sys.stdout.write("\r" + message)
    sys.stdout.flush()


def sanitize_filename(color):
    return "_".join(map(str, color))


def build_overlord_chains(overrides):
    """
    overrides: vassal_rgb -> direct_overlord_rgb
    returns:   vassal_rgb -> [overlord, grand_overlord, ...]
    """
    chains = {}
    for vassal in overrides:
        cur = vassal
        seen = {vassal}
        chain = []

        while cur in overrides:
            nxt = overrides[cur]
            if nxt in seen:
                break
            chain.append(nxt)
            seen.add(nxt)
            cur = nxt

        chains[vassal] = chain

    return chains


def generate_regions(
    map_name: str,
    mode: str,
    borders: bool,
    queued_regen: bool = False,
    border_thickness: int = default_border_thickness,
    border_color: tuple[int, int, int, int] = (0, 0, 0, 255),
    cache: MapGeometryCache | None = None,
):
    if cache is not None:
        from .regiongen_numpy import generate_regions_numpy

        return generate_regions_numpy(
            map_name,
            mode,
            borders,
            cache,
            queued_regen=queued_regen,
            border_thickness=border_thickness,
            border_color=border_color,
        )

    start_time = time.perf_counter()
    validate_map(map_name)

    img_path = input_file(map_name, "provinces.png")
    if cache is not None:
        provinces_rgba = cache.provinces_rgba
        width, height = cache.width, cache.height
    else:
        src_img = Image.open(img_path).convert("RGBA")
        provinces_rgba = None
        src = src_img.load()
        width, height = src_img.size

    province_to_color = build_color_mapping(map_name, mode)
    if not province_to_color:
        print(f"No mapping for mode '{mode}', skipping.")
        return

    overrides = get_color_overrides(map_name, mode)
    has_nesting = bool(overrides)
    overlord_chains = build_overlord_chains(overrides)
    overlord_colors = set(overrides.values())

    trade_mixed = getattr(build_color_mapping, "trade_mixed", None)
    occupation_provinces = getattr(build_color_mapping, "occupation_provinces", None) or set()

    output_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(img_path),
            "..", "..", "output", map_name, "regions", mode
        )
    )
    os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------
    # Queue handling
    # ------------------------------------------------------------
    queued = None
    if queued_regen:
        compile_queue(map_name)
        queued = set(load_queue(map_name, mode))

        for fn in os.listdir(output_dir):
            base = (
                fn.replace("_hover", "")
                  .replace("_nested", "")
                  .replace(".png", "")
            )
            if base in queued:
                os.remove(os.path.join(output_dir, fn))
    else:
        for fn in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, fn))

    # ------------------------------------------------------------
    # Scan province pixels
    # ------------------------------------------------------------
    province_pixels = {}
    total_pixels = width * height
    processed = 0
    last_update = time.time()

    for y in range(height):
        for x in range(width):
            if cache is not None:
                rgb = tuple(int(v) for v in provinces_rgba[y, x, :3])
            else:
                rgb = src[x, y][:3]
            if rgb in province_to_color:
                province_pixels.setdefault(rgb, []).append((x, y))

            processed += 1
            if time.time() - last_update > 0.1:
                log_progress(
                    f"Scanning pixels: {processed:,}/{total_pixels:,} "
                    f"({processed / total_pixels * 100:5.1f}%)"
                )
                last_update = time.time()

    print()

    # ------------------------------------------------------------
    # Region buffers
    # ------------------------------------------------------------
    region_imgs = {}
    region_px = {}
    light_cache = {}

    def ensure_region(color):
        if color in region_imgs:
            return

        base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        hover = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        nested = nested_hover = None
        if color in overlord_colors:
            nested = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            nested_hover = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        region_imgs[color] = (base, hover, nested, nested_hover)
        region_px[color] = (
            base.load(),
            hover.load(),
            nested.load() if nested else None,
            nested_hover.load() if nested_hover else None,
        )

    # ------------------------------------------------------------
    # Paint regions
    # ------------------------------------------------------------
    total_regions = len(province_pixels)
    current = 0

    for prov_rgb, pixels in province_pixels.items():
        owner = province_to_color[prov_rgb]
        name = sanitize_filename(owner)

        if queued and name not in queued:
            continue

        current += 1
        log_progress(
            f"Building regions: {current}/{total_regions} "
            f"({current / total_regions * 100:5.1f}%) → {name}"
        )

        ensure_region(owner)

        if owner not in light_cache:
            light_cache[owner] = hover_rgb(owner)

        if occupation_provinces and prov_rgb in occupation_provinces:
            pr, pg, pb = occupation_display_rgb(owner)
        else:
            paint_rgb = trade_mixed.get(prov_rgb, owner) if trade_mixed else owner
            pr, pg, pb = display_rgb(paint_rgb)
        lr, lg, lb = light_cache[owner]

        base_px, hover_px, nested_px, nested_hover_px = region_px[owner]

        for x, y in pixels:
            base_px[x, y] = (pr, pg, pb, 255)
            hover_px[x, y] = (lr, lg, lb, 255)
            if nested_px:
                nested_px[x, y] = (pr, pg, pb, 255)
                nested_hover_px[x, y] = (lr, lg, lb, 255)

        # Paint into all ancestors
        for anc in overlord_chains.get(owner, []):
            ensure_region(anc)
            if anc not in light_cache:
                light_cache[anc] = hover_rgb(anc)

            ar, ag, ab = display_rgb(anc)
            alr, alg, alb = light_cache[anc]
            anc_base, anc_hover, _, _ = region_px[anc]

            for x, y in pixels:
                anc_base[x, y] = (ar, ag, ab, 255)
                anc_hover[x, y] = (alr, alg, alb, 255)

    print()

    # ------------------------------------------------------------
    # Borders
    # ------------------------------------------------------------
    if borders and region_imgs:

        total = len(region_imgs)
        for i, (color, (base, hover, nested, nested_hover)) in enumerate(region_imgs.items(), start=1):
            kind = "nested" if has_nesting else "fast"
            log_progress(
                f"Painting borders ({kind}): {i}/{total} "
                f"({i / total * 100:5.1f}%)"
            )

            display_color = display_rgb(color)
            base_stroke = border_color_for_fill(display_color)
            hover_stroke = border_color_for_fill(hover_rgb(color))
            apply_opaque_union_borders(
                base.load(), width, height, base_stroke, border_thickness
            )
            apply_opaque_union_borders(
                hover.load(), width, height, hover_stroke, border_thickness
            )
            if occupation_provinces:
                occ_color = occupation_display_rgb(color)
                apply_occupation_seam_dashes(
                    base.load(),
                    [base.load(), hover.load()],
                    width,
                    height,
                    display_color,
                    occ_color,
                )
            if nested:
                apply_opaque_union_borders(
                    nested.load(), width, height, base_stroke, border_thickness
                )
                apply_opaque_union_borders(
                    nested_hover.load(), width, height, hover_stroke, border_thickness
                )
                if occupation_provinces:
                    occ_color = occupation_display_rgb(color)
                    apply_occupation_seam_dashes(
                        nested.load(),
                        [nested.load(), nested_hover.load()],
                        width,
                        height,
                        display_color,
                        occ_color,
                    )

    print()

    # ------------------------------------------------------------
    # Save outputs (cropped) + collect bbox metadata
    # ------------------------------------------------------------
    metadata_by_rgb: dict[str, dict] = {}
    total_outputs = len(region_imgs)
    for i, (color, (base, hover, nested, nested_hover)) in enumerate(region_imgs.items(), start=1):
        name = sanitize_filename(color)
        if queued and name not in queued:
            continue

        log_progress(
            f"Saving images: {i}/{total_outputs} "
            f"({i / total_outputs * 100:5.1f}%) → {name}"
        )

        overlay_meta = save_cropped(base, os.path.join(output_dir, f"{name}.png"))
        save_cropped(hover, os.path.join(output_dir, f"{name}_hover.png"))

        region_meta: dict = {}
        if overlay_meta:
            region_meta["overlay"] = overlay_meta

        if nested:
            nested_meta = save_cropped(
                nested, os.path.join(output_dir, f"{name}_nested.png")
            )
            save_cropped(
                nested_hover,
                os.path.join(output_dir, f"{name}_nested_hover.png"),
            )
            if nested_meta:
                region_meta["overlay_nested"] = nested_meta

        if region_meta:
            metadata_by_rgb[rgb_tuple_to_str(color)] = region_meta

        base.close()
        hover.close()
        if nested:
            nested.close()
            nested_hover.close()

    print()

    write_overlay_metadata(map_name, mode, metadata_by_rgb, merge=queued_regen)

    if queued_regen:
        clear_mode(map_name, mode)

    elapsed = time.perf_counter() - start_time
    print(
        f"Region generation for mode '{mode}' "
        f"took {elapsed:.2f} seconds "
        f"(nesting={'yes' if has_nesting else 'no'})"
    )
