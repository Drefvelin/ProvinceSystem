# Now, after all provinces are painted, paint the borders
border_color = (0, 0, 0, 255)  # Solid black for kingdom borders
duchy_border_color = (255, 255, 255, 255)  # White for duchy borders
border_thickness = 5  # Adjustable thickness

def compute_border_owners(img_data, width, height, include_outer=True):
    """
    include_outer=True: count borders against transparent pixels as borders too.
    """
    borders = {}

    for y in range(height):
        for x in range(width):
            c = img_data[x, y]
            if c[3] == 0:
                continue
            c_rgb = c[:3]

            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if not (0 <= nx < width and 0 <= ny < height):
                    # edge of image counts as outer border
                    if include_outer:
                        borders.setdefault((x, y), set()).add(c_rgb)
                    continue

                n = img_data[nx, ny]
                if n[3] == 0:
                    if include_outer:
                        borders.setdefault((x, y), set()).add(c_rgb)
                    continue

                n_rgb = n[:3]
                if n_rgb != c_rgb:
                    borders.setdefault((x, y), set()).update((c_rgb, n_rgb))
                    borders.setdefault((nx, ny), set()).update((c_rgb, n_rgb))
    return borders

def apply_region_borders(
    img_data,
    region_color,
    border_owners,
    width,
    height,
    color=(0, 0, 0, 255),
    thickness=2
):
    """
    Paints borders for a given region_color.
    Because compute_border_owners stores border points on both sides,
    the dilation extends outward as well as inward.
    """
    t = thickness
    for (x, y), owners in border_owners.items():
        if region_color not in owners:
            continue

        for dy in range(-t, t + 1):
            ny = y + dy
            if 0 <= ny < height:
                for dx in range(-t, t + 1):
                    nx = x + dx
                    if 0 <= nx < width:
                        img_data[nx, ny] = color

def paint_borders(outline, between, new_img_data, height, width):
    borders = set()
    # Iterate through all pixels and check for borders
    if outline:
        for y in range(height):
            for x in range(width):
                pixel_color = new_img_data[x, y]
                if pixel_color[3] != 0:  # Only check non-transparent pixels
                    # Check neighboring pixels
                    neighbors = [
                        (x - 1, y),  # Left
                        (x + 1, y),  # Right
                        (x, y - 1),  # Up
                        (x, y + 1),  # Down
                    ]
                    for nx, ny in neighbors:
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbor_color = new_img_data[nx, ny]
                            if pixel_color != neighbor_color:  # Different color means border
                                if not between and neighbor_color[3] != 0:
                                    continue  # Skip if we are only drawing kingdom borders
                                else:
                                    for dx in range(-border_thickness, border_thickness + 1):
                                        for dy in range(-border_thickness, border_thickness + 1):
                                            bx, by = x + dx, y + dy
                                            if 0 <= bx < width and 0 <= by < height:
                                                borders.add((bx, by))

    # Apply the border color to all detected border pixels
    for x, y in borders:
        new_img_data[x, y] = border_color
    return new_img_data