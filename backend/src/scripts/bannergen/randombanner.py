import random

from .patterns_catalog import POOLS

# Heraldic tinctures (Minecraft dyes). Metals sit on colors and vice versa.
METALS = ["WHITE", "YELLOW", "LIGHT_GRAY"]
COLORS = [
    "RED", "BLUE", "GREEN", "BLACK", "BROWN", "ORANGE", "CYAN",
    "PURPLE", "MAGENTA", "PINK", "LIME", "LIGHT_BLUE", "GRAY",
]
ALL_TINCTURES = METALS + COLORS

MUDDY_PAIRS = {
    frozenset({"GRAY", "BLACK"}),
    frozenset({"WHITE", "LIGHT_GRAY"}),
}

FIELD_COLOR_WEIGHT = 3
FIELD_METAL_WEIGHT = 1

# ordinary: fixed pattern name | None
# ordinary_pool: pool key from patterns_catalog.POOLS
# extra: second fixed field layer (tricolor)
# charge: bool - add a charge layer when room remains
# charge_pool: "mixed" (tfmc-heavy) | "tfmc" | "vanilla"
TEMPLATES = [
  # Solid field + emblem (tfmc-heavy)
    {"weight": 20, "ordinary": None, "charge": True, "charge_pool": "mixed"},
    # Tfmc borders + emblem
    {"weight": 12, "ordinary_pool": "tfmc_border", "charge": True, "charge_pool": "mixed"},
    # Tfmc bold fields
    {"weight": 10, "ordinary_pool": "tfmc_field", "charge": True, "charge_pool": "mixed"},
    {"weight": 8, "ordinary_pool": "tfmc_field", "charge": False},
    # Vanilla partitions + tfmc emblem
    {"weight": 12, "ordinary_pool": "vanilla_partition", "charge": True, "charge_pool": "mixed"},
    {"weight": 6, "ordinary_pool": "vanilla_partition", "charge": False},
    # Vanilla borders + emblem
    {"weight": 8, "ordinary_pool": "vanilla_border", "charge": True, "charge_pool": "mixed"},
    # Crosses (reduced weight, often without center charge)
    {"weight": 5, "ordinary_pool": "vanilla_cross", "charge": False},
    {"weight": 3, "ordinary_pool": "vanilla_cross", "charge": True, "charge_pool": "mixed"},
    # Tricolor layouts (no charge)
    {"weight": 7, "ordinary": "HALF_VERTICAL", "extra": "HALF_VERTICAL_RIGHT", "charge": False},
    {"weight": 5, "ordinary": "STRIPE_TOP", "extra": "STRIPE_BOTTOM", "charge": False},
    # Tfmc field + tfmc-only emblem
    {"weight": 8, "ordinary_pool": "tfmc_field", "charge": True, "charge_pool": "tfmc"},
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


def _other_class(tincture):
    return METALS if tincture in COLORS else COLORS


def _is_muddy(a, b):
    return frozenset({a, b}) in MUDDY_PAIRS


def _pick_field():
    pool = COLORS * FIELD_COLOR_WEIGHT + METALS * FIELD_METAL_WEIGHT
    return random.choice(pool)


def _pick_tincture(pool, used, adjacent):
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


def _pick_pattern_from_pool(pool_name: str) -> str:
    return random.choice(POOLS[pool_name])


def _pick_charge(pool_name: str) -> str:
    if pool_name == "tfmc":
        return random.choice(POOLS["tfmc_charge"])
    if pool_name == "vanilla":
        return random.choice(POOLS["vanilla_small_charge"])
    # mixed: tfmc-heavy with rare noisy icons
    roll = random.random()
    if roll < 0.05:
        return random.choice(POOLS["noisy"])
    if roll < 0.80:
        return random.choice(POOLS["tfmc_charge"])
    return random.choice(POOLS["vanilla_small_charge"])


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
    ordinary_pattern = None
    if template.get("ordinary_pool"):
        ordinary_pattern = _pick_pattern_from_pool(template["ordinary_pool"])
    elif template.get("ordinary"):
        ordinary_pattern = template["ordinary"]

    if ordinary_pattern:
        ordinary_color = _pick_tincture(_other_class(field), used, [field])
        used.append(ordinary_color)
        layers.append(f"{ordinary_color}.{ordinary_pattern}")

    if template.get("extra"):
        extra_bg = ordinary_color or field
        extra_color = _pick_tincture(_other_class(extra_bg), used, [extra_bg, field])
        used.append(extra_color)
        layers.append(f"{extra_color}.{template['extra']}")

    if template.get("charge") and len(layers) < 3:
        sits_on = ordinary_color or field
        charge_color = _pick_tincture(_other_class(sits_on), used, [sits_on])
        charge_pool = template.get("charge_pool", "mixed")
        charge = _pick_charge(charge_pool)
        layers.append(f"{charge_color}.{charge}")

    return layers
