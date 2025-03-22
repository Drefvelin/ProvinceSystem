import random
import json

# All Minecraft dye colors
dye_colors = [
    "WHITE", "ORANGE", "LIGHT_BLUE", "YELLOW", "LIME",
    "GRAY", "LIGHT_GRAY", "CYAN", "BLUE", "BROWN", "GREEN", "RED", "BLACK"
]

# All pattern types (excluding BASE)
pattern_types = [
    "SQUARE_BOTTOM_LEFT", "SQUARE_BOTTOM_RIGHT", "SQUARE_TOP_LEFT", "SQUARE_TOP_RIGHT",
    "STRIPE_BOTTOM", "STRIPE_TOP", "STRIPE_LEFT", "STRIPE_RIGHT",
    "STRIPE_CENTER", "STRIPE_MIDDLE", "STRIPE_DOWNRIGHT", "STRIPE_DOWNLEFT", "SMALL_STRIPES",
    "CROSS", "STRAIGHT_CROSS", "TRIANGLE_BOTTOM", "TRIANGLE_TOP", "TRIANGLES_BOTTOM",
    "TRIANGLES_TOP", "DIAGONAL_LEFT", "DIAGONAL_RIGHT", "DIAGONAL_UP_LEFT",
    "DIAGONAL_UP_RIGHT", "CIRCLE", "RHOMBUS", "HALF_VERTICAL", "HALF_HORIZONTAL",
    "HALF_VERTICAL_RIGHT", "HALF_HORIZONTAL_BOTTOM", "BORDER", "CURLY_BORDER",
    "GRADIENT", "GRADIENT_UP", "BRICKS", "CREEPER", "SKULL", "FLOWER", "MOJANG", "GLOBE", "PIGLIN",
    
    "ARCS", "ARROW_DOWN", "ARROW_UP", "ARROWS_DOWN", "ARROWS_UP", "BLAM", "BOLTS", "BURN",
    "CASTLE", "CHECKER", "CHEQUERED", "CIRCLE_TILES", "CLOVER", "CLUB", "CLUBS", "COGS",
    "COMPANION", "CRESCENT", "CROWN", "CURTAINS", "DIAGONAL_BORDER", "DIAMOND", "DIAMONDS",
    "DOVETAIL", "EARTH", "FANCY", "FIRE", "FORK_BOTTOM", "FORK_TOP", "GONFALON", "HAMMER",
    "HEART", "HEARTS", "MOON", "PALACE", "PEACE", "PUMPKIN", "QUARTER_BOTTOM_LEFT",
    "QUARTER_BOTTOM_RIGHT", "QUARTER_TOP_LEFT", "QUARTER_TOP_RIGHT", "REVOLUTION", "RIBS",
    "RING", "SHIELD", "SMALL_STRIPE_LEFT", "SMALL_STRIPE_RIGHT", "SMALL_STRIPES_DOWNLEFT",
    "SMALL_STRIPES_DOWNRIGHT", "SMALL_STRIPES_HORIZONTAL", "SPADE", "SPADES", "STAR", "SUN",
    "SUNBURST", "SWORD", "TATTER", "TATTERED", "TRIDENT", "WATER", "WIND", "YIN_YANG"
]

# Backgrounds – Large area fill
background_patterns = [
    "DIAGONAL_LEFT", "DIAGONAL_RIGHT", "DIAGONAL_UP_LEFT", "DIAGONAL_UP_RIGHT",
    "TRIANGLE_BOTTOM", "TRIANGLE_TOP", "TRIANGLES_BOTTOM", "TRIANGLES_TOP",
    "SQUARE_BOTTOM_LEFT", "SQUARE_BOTTOM_RIGHT", "SQUARE_TOP_LEFT", "SQUARE_TOP_RIGHT",
    "HALF_VERTICAL", "HALF_HORIZONTAL", "HALF_VERTICAL_RIGHT", "HALF_HORIZONTAL_BOTTOM",
    "GRADIENT", "GRADIENT_UP", "QUARTER_BOTTOM_LEFT", "QUARTER_BOTTOM_RIGHT", 
    "QUARTER_TOP_LEFT", "QUARTER_TOP_RIGHT"
]

# Stripes – Linear lines
stripe_patterns = [
    "STRIPE_BOTTOM", "STRIPE_TOP", "STRIPE_LEFT", "STRIPE_RIGHT", "STRIPE_CENTER",
    "STRIPE_MIDDLE", "STRIPE_DOWNRIGHT", "STRIPE_DOWNLEFT", "SMALL_STRIPES",
    "SMALL_STRIPE_LEFT", "SMALL_STRIPE_RIGHT", "SMALL_STRIPES_DOWNLEFT", "SMALL_STRIPES_DOWNRIGHT",
    "SMALL_STRIPES_HORIZONTAL", "CROSS", "STRAIGHT_CROSS", "BORDER", "CURLY_BORDER"
]

# Ornaments – Smaller or iconographic
ornament_patterns = list(set(pattern_types) - set(background_patterns) - set(stripe_patterns))

minecraft_dye_colors = {
    "white":     (255, 255, 255),
    "orange":    (216, 127, 51),
    "light_blue": (102, 153, 216),
    "yellow":    (229, 229, 51),
    "lime":      (127, 204, 25),
    "gray":      (76, 76, 76),
    "light_gray": (153, 153, 153),
    "cyan":      (76, 127, 153),
    "blue":      (51, 76, 178),
    "brown":     (102, 76, 51),
    "green":     (102, 127, 51),
    "red":       (153, 51, 51),
    "black":     (25, 25, 25),
}

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

def get_contrasting_color(used_colors, all_colors, dye_rgb_map):
    threshold = 100  # Higher = stronger contrast

    contrasting = [
        color for color in all_colors
        if all(color_distance(dye_rgb_map[color.lower()], dye_rgb_map[used.lower()]) > threshold for used in used_colors)
    ]

    if contrasting:
        return random.choice(contrasting)
    else:
        # fallback to any unused color
        unused = [c for c in all_colors if c not in used_colors]
        return random.choice(unused) if unused else random.choice(all_colors)

def get_similar_color(used_colors, all_colors, dye_rgb_map, threshold=80):
    color_usage = {color: used_colors.count(color) for color in all_colors}

    # Build a weighted list of similar colors with weights decreasing on repeated use
    weighted_similar = []
    for color in all_colors:
        if any(color_distance(dye_rgb_map[color.lower()], dye_rgb_map[used.lower()]) < threshold for used in used_colors):
            usage_count = color_usage.get(color, 0)
            weight = max(1, 3 - usage_count)  # First use = weight 3, second = 2, third+ = 1
            weighted_similar.extend([color] * weight)

    if weighted_similar:
        return random.choice(weighted_similar)
    else:
        # fallback to unused or any available color
        unused = [c for c in all_colors if c not in used_colors]
        return random.choice(unused) if unused else random.choice(all_colors)

def generate_random_banner():
    used_colors = []
    base_color = random.choice(dye_colors)
    used_colors.append(base_color)
    patterns = [f"{base_color}.BASE"]

    # Background (80% chance)
    if random.random() < 0.8:
        bg_color = get_similar_color(used_colors, dye_colors, minecraft_dye_colors)
        bg_pattern = random.choice(background_patterns)
        patterns.append(f"{bg_color}.{bg_pattern}")
        used_colors.append(bg_color)

    # Stripe (60% chance)
    if random.random() < 0.6:
        stripe_color = get_similar_color(used_colors, dye_colors, minecraft_dye_colors)
        stripe_pattern = random.choice(stripe_patterns)
        patterns.append(f"{stripe_color}.{stripe_pattern}")
        used_colors.append(stripe_color)

    # Ornaments
    ornament_count = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
    used_ornaments = set()

    for _ in range(ornament_count):
        while True:
            ornament = random.choice(ornament_patterns)
            if ornament not in used_ornaments:
                used_ornaments.add(ornament)
                break
        ornament_color = get_similar_color(used_colors, dye_colors, minecraft_dye_colors)
        if random.random() < 0.6 or _ == 0:
            ornament_color = get_contrasting_color(used_colors, dye_colors, minecraft_dye_colors)
        patterns.append(f"{ornament_color}.{ornament}")
        used_colors.append(ornament_color)

    return patterns

