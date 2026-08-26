import random

# Heraldic tinctures (Minecraft dyes). Metals sit on colors and vice versa.
METALS = ["WHITE", "YELLOW", "LIGHT_GRAY"]
COLORS = [
    "RED", "BLUE", "GREEN", "BLACK", "BROWN", "ORANGE", "CYAN",
    "PURPLE", "MAGENTA", "PINK", "LIME", "LIGHT_BLUE", "GRAY",
]
ALL_TINCTURES = METALS + COLORS

# Pairs that read as one muddy color when used as the two main tinctures.
MUDDY_PAIRS = {
    frozenset({"GRAY", "BLACK"}),
    frozenset({"WHITE", "LIGHT_GRAY"}),
}

CHARGES = [
    "STAR", "CIRCLE", "RHOMBUS", "CRESCENT", "CROWN", "MOON",
    "HEART", "FLOWER", "SUN", "SHIELD", "SWORD", "HAMMER", "GLOBE",
]

# Prefer colored fields with metal ordinaries/charges, like CK3.
FIELD_COLOR_WEIGHT = 3
FIELD_METAL_WEIGHT = 1

# Each template: BASE + optional ordinary + optional extra field + optional charge.
# Max 3 layers total (tricolor uses extra instead of a charge).
TEMPLATES = [
    {"weight": 18, "ordinary": None, "extra": None, "charge": True},
    {"weight": 10, "ordinary": "HALF_VERTICAL", "extra": None, "charge": True},
    {"weight": 6, "ordinary": "HALF_VERTICAL", "extra": None, "charge": False},
    {"weight": 8, "ordinary": "HALF_HORIZONTAL", "extra": None, "charge": True},
    {"weight": 5, "ordinary": "HALF_HORIZONTAL", "extra": None, "charge": False},
    {"weight": 6, "ordinary": "HALF_VERTICAL_RIGHT", "extra": None, "charge": True},
    {"weight": 4, "ordinary": "HALF_HORIZONTAL_BOTTOM", "extra": None, "charge": True},
    {"weight": 8, "ordinary": "STRIPE_TOP", "extra": None, "charge": True},
    {"weight": 8, "ordinary": "STRIPE_CENTER", "extra": None, "charge": True},
    {"weight": 8, "ordinary": "STRIPE_MIDDLE", "extra": None, "charge": True},
    {"weight": 4, "ordinary": "STRIPE_BOTTOM", "extra": None, "charge": True},
    {"weight": 4, "ordinary": "STRIPE_LEFT", "extra": None, "charge": True},
    {"weight": 4, "ordinary": "STRIPE_RIGHT", "extra": None, "charge": True},
    {"weight": 10, "ordinary": "CROSS", "extra": None, "charge": False},
    {"weight": 6, "ordinary": "CROSS", "extra": None, "charge": True},
    {"weight": 8, "ordinary": "STRAIGHT_CROSS", "extra": None, "charge": False},
    {"weight": 5, "ordinary": "STRAIGHT_CROSS", "extra": None, "charge": True},
    {"weight": 6, "ordinary": "STRIPE_DOWNLEFT", "extra": None, "charge": True},
    {"weight": 6, "ordinary": "STRIPE_DOWNRIGHT", "extra": None, "charge": True},
    {"weight": 6, "ordinary": "TRIANGLE_BOTTOM", "extra": None, "charge": True},
    {"weight": 6, "ordinary": "TRIANGLE_TOP", "extra": None, "charge": True},
    {"weight": 3, "ordinary": "TRIANGLE_BOTTOM", "extra": None, "charge": False},
    {"weight": 3, "ordinary": "TRIANGLE_TOP", "extra": None, "charge": False},
    {"weight": 8, "ordinary": "BORDER", "extra": None, "charge": True},
    {"weight": 4, "ordinary": "CURLY_BORDER", "extra": None, "charge": True},
    {"weight": 7, "ordinary": "HALF_VERTICAL", "extra": "HALF_VERTICAL_RIGHT", "charge": False},
    {"weight": 5, "ordinary": "STRIPE_TOP", "extra": "STRIPE_BOTTOM", "charge": False},
    {"weight": 6, "ordinary": "DIAGONAL_LEFT", "extra": None, "charge": True},
    {"weight": 6, "ordinary": "DIAGONAL_RIGHT", "extra": None, "charge": True},
    {"weight": 3, "ordinary": "DIAGONAL_UP_LEFT", "extra": None, "charge": True},
    {"weight": 3, "ordinary": "DIAGONAL_UP_RIGHT", "extra": None, "charge": True},
]

minecraft_dye_colors = {
    "white": (255, 255, 255),
    "orange": (216, 127, 51),
    "magenta": (178, 76, 216),
    "light_blue": (102, 153, 216),
    "yellow": (229, 229, 51),
    "lime": (127, 204, 25),
    "pink": (242, 127, 165),
    "gray": (76, 76, 76),
    "light_gray": (153, 153, 153),
    "cyan": (76, 127, 153),
    "purple": (127, 63, 178),
    "blue": (51, 76, 178),
    "brown": (102, 76, 51),
    "green": (102, 127, 51),
    "red": (153, 51, 51),
    "black": (25, 25, 25),
}


def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5


def _is_metal(tincture):
    return tincture in METALS


def _other_class(tincture):
    return METALS if tincture in COLORS else COLORS


def _is_muddy(a, b):
    return frozenset({a, b}) in MUDDY_PAIRS


def _pick_field():
    pool = COLORS * FIELD_COLOR_WEIGHT + METALS * FIELD_METAL_WEIGHT
    return random.choice(pool)


def _pick_tincture(pool, used, adjacent):
    """Pick from pool: unused first, never muddy vs adjacent layers, else contrast fallback."""
    candidates = [
        c for c in pool
        if c not in used and not any(_is_muddy(c, other) for other in adjacent)
    ]
    if candidates:
        return random.choice(candidates)

    unused = [c for c in pool if c not in used]
    if unused:
        return random.choice(unused)

    rgb = minecraft_dye_colors
    threshold = 100
    contrasting = [
        c for c in ALL_TINCTURES
        if all(
            color_distance(rgb[c.lower()], rgb[u.lower()]) > threshold
            for u in used
        )
    ]
    if contrasting:
        return random.choice(contrasting)
    leftover = [c for c in ALL_TINCTURES if c not in used]
    return random.choice(leftover) if leftover else random.choice(ALL_TINCTURES)


def generate_random_banner():
    template = random.choices(
        TEMPLATES,
        weights=[t["weight"] for t in TEMPLATES],
        k=1,
    )[0]

    field = _pick_field()
    used = [field]
    layers = [f"{field}.BASE"]

    ordinary_color = None
    if template["ordinary"]:
        ordinary_color = _pick_tincture(_other_class(field), used, [field])
        used.append(ordinary_color)
        layers.append(f"{ordinary_color}.{template['ordinary']}")

    if template["extra"]:
        extra_bg = ordinary_color or field
        extra_color = _pick_tincture(_other_class(extra_bg), used, [extra_bg, field])
        used.append(extra_color)
        layers.append(f"{extra_color}.{template['extra']}")

    if template["charge"] and len(layers) < 3:
        sits_on = ordinary_color or field
        charge_color = _pick_tincture(_other_class(sits_on), used, [sits_on])
        charge = random.choice(CHARGES)
        layers.append(f"{charge_color}.{charge}")

    return layers
