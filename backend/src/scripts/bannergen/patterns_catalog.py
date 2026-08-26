"""Banner pattern catalog: vanilla (minecraft:) vs tfmc custom patterns and layout pools."""

import os

from ..util.dirs import INPUT_DIR

# Registry patterns under minecraft: namespace (excluding BASE).
VANILLA_PATTERNS = frozenset({
    "SQUARE_BOTTOM_LEFT", "SQUARE_BOTTOM_RIGHT", "SQUARE_TOP_LEFT", "SQUARE_TOP_RIGHT",
    "STRIPE_BOTTOM", "STRIPE_TOP", "STRIPE_LEFT", "STRIPE_RIGHT",
    "STRIPE_CENTER", "STRIPE_MIDDLE", "STRIPE_DOWNRIGHT", "STRIPE_DOWNLEFT",
    "SMALL_STRIPES",
    "CROSS", "STRAIGHT_CROSS",
    "TRIANGLE_BOTTOM", "TRIANGLE_TOP", "TRIANGLES_BOTTOM", "TRIANGLES_TOP",
    "DIAGONAL_LEFT", "DIAGONAL_RIGHT", "DIAGONAL_UP_LEFT", "DIAGONAL_UP_RIGHT",
    "CIRCLE", "RHOMBUS",
    "HALF_VERTICAL", "HALF_HORIZONTAL", "HALF_VERTICAL_RIGHT", "HALF_HORIZONTAL_BOTTOM",
    "BORDER", "CURLY_BORDER",
    "GRADIENT", "GRADIENT_UP",
    "BRICKS", "CREEPER", "SKULL", "FLOWER", "MOJANG", "GLOBE", "PIGLIN",
})

# Custom tfmc patterns (PNG assets + in-game tfmc: namespace).
TFMC_PATTERNS = frozenset({
    "ARCS", "ARROW_DOWN", "ARROW_UP", "ARROWS_DOWN", "ARROWS_UP",
    "BLAM", "BOLTS", "BURN", "CASTLE", "CHECKER", "CHEQUERED",
    "CIRCLE_TILES", "CLOVER", "CLUB", "CLUBS", "COGS", "COMPANION",
    "CRESCENT", "CROWN", "CROWNS", "CURTAINS", "DIAGONAL_BORDER",
    "DIAMOND", "DIAMONDS", "DOVETAIL", "EARTH", "FANCY", "FIRE", "FLOW",
    "FORK_BOTTOM", "FORK_TOP", "GONFALON", "GUSTER", "HAMMER", "HEART", "HEARTS",
    "MOON", "PALACE", "PEACE", "PUMPKIN",
    "QUARTER_BOTTOM_LEFT", "QUARTER_BOTTOM_RIGHT",
    "QUARTER_TOP_LEFT", "QUARTER_TOP_RIGHT",
    "REVOLUTION", "RIBS", "RIBS_BORDER", "RING", "SHIELD",
    "SMALL_STRIPE_LEFT", "SMALL_STRIPE_RIGHT",
    "SMALL_STRIPES_DOWNLEFT", "SMALL_STRIPES_DOWNRIGHT", "SMALL_STRIPES_HORIZONTAL",
    "SPADE", "SPADES", "STAR", "SUN", "SUNBURST", "SWORD",
    "TATTER", "TATTERED", "TRIDENT", "WATER", "WIND", "YIN_YANG",
})

ALL_PATTERNS = VANILLA_PATTERNS | TFMC_PATTERNS

VANILLA_PARTITION = [
    "HALF_VERTICAL", "HALF_HORIZONTAL", "HALF_VERTICAL_RIGHT", "HALF_HORIZONTAL_BOTTOM",
    "STRIPE_BOTTOM", "STRIPE_TOP", "STRIPE_LEFT", "STRIPE_RIGHT",
    "STRIPE_CENTER", "STRIPE_MIDDLE", "STRIPE_DOWNRIGHT", "STRIPE_DOWNLEFT",
    "DIAGONAL_LEFT", "DIAGONAL_RIGHT", "DIAGONAL_UP_LEFT", "DIAGONAL_UP_RIGHT",
    "TRIANGLE_BOTTOM", "TRIANGLE_TOP", "TRIANGLES_BOTTOM", "TRIANGLES_TOP",
    "GRADIENT", "GRADIENT_UP",
    "SQUARE_BOTTOM_LEFT", "SQUARE_BOTTOM_RIGHT", "SQUARE_TOP_LEFT", "SQUARE_TOP_RIGHT",
]

VANILLA_CROSS = ["CROSS", "STRAIGHT_CROSS"]

VANILLA_BORDER = ["BORDER", "CURLY_BORDER"]

TFMC_BORDER = ["RIBS_BORDER", "DIAGONAL_BORDER"]

TFMC_FIELD = [
    "CHEQUERED", "CHECKER", "CASTLE", "CURTAINS", "GONFALON",
    "FORK_TOP", "FORK_BOTTOM", "FLOW", "GUSTER",
    "QUARTER_BOTTOM_LEFT", "QUARTER_BOTTOM_RIGHT",
    "QUARTER_TOP_LEFT", "QUARTER_TOP_RIGHT",
    "RIBS", "REVOLUTION", "SUNBURST",
]

TFMC_CHARGE = [
    "ARCS", "ARROW_DOWN", "ARROW_UP", "ARROWS_DOWN", "ARROWS_UP",
    "BOLTS", "BURN", "CIRCLE_TILES", "CLOVER", "CLUB", "CLUBS", "COGS",
    "COMPANION", "CRESCENT", "CROWN", "CROWNS", "DIAMOND", "DIAMONDS",
    "DOVETAIL", "EARTH", "FANCY", "FIRE", "HAMMER", "HEART", "HEARTS",
    "MOON", "PALACE", "PEACE", "PUMPKIN", "RING", "SHIELD",
    "SMALL_STRIPE_LEFT", "SMALL_STRIPE_RIGHT",
    "SMALL_STRIPES_DOWNLEFT", "SMALL_STRIPES_DOWNRIGHT", "SMALL_STRIPES_HORIZONTAL",
    "SPADE", "SPADES", "STAR", "SUN", "SWORD", "TRIDENT", "WATER", "WIND", "YIN_YANG",
]

VANILLA_SMALL_CHARGES = [
    "CIRCLE", "RHOMBUS",
    "SQUARE_TOP_LEFT", "SQUARE_TOP_RIGHT", "SQUARE_BOTTOM_LEFT", "SQUARE_BOTTOM_RIGHT",
    "TRIANGLES_BOTTOM", "TRIANGLES_TOP", "SMALL_STRIPES", "FLOWER", "GLOBE",
]

NOISY = ["BLAM", "TATTER", "TATTERED", "CREEPER", "SKULL", "MOJANG", "PIGLIN", "BRICKS"]

POOLS = {
    "vanilla_partition": VANILLA_PARTITION,
    "vanilla_cross": VANILLA_CROSS,
    "vanilla_border": VANILLA_BORDER,
    "tfmc_border": TFMC_BORDER,
    "tfmc_field": TFMC_FIELD,
    "tfmc_charge": TFMC_CHARGE,
    "vanilla_small_charge": VANILLA_SMALL_CHARGES,
    "noisy": NOISY,
}


def is_tfmc(pattern: str) -> bool:
    return pattern.upper() in TFMC_PATTERNS


def is_vanilla(pattern: str) -> bool:
    return pattern.upper() in VANILLA_PATTERNS


def all_patterns() -> frozenset[str]:
    return ALL_PATTERNS


def banner_png_dir(map_name: str = "dev") -> str:
    return os.path.join(INPUT_DIR, map_name, "banner")


def png_pattern_names(map_name: str = "dev") -> frozenset[str]:
    folder = banner_png_dir(map_name)
    names = set()
    if not os.path.isdir(folder):
        return frozenset()
    for name in os.listdir(folder):
        if name.endswith(".png") and name != "base.png":
            names.add(name[:-4].upper())
    return frozenset(names)


def catalog_png_mismatches(map_name: str = "dev") -> tuple[list[str], list[str]]:
    """Return (missing_png, orphan_png) vs ALL_PATTERNS."""
    pngs = png_pattern_names(map_name)
    missing = sorted(ALL_PATTERNS - pngs)
    orphan = sorted(pngs - ALL_PATTERNS)
    return missing, orphan
