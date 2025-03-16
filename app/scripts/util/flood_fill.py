from PIL import Image
from collections import deque

def flood_fill(x, y, target_color, new_color, visited, data, new_data, width, height):
    queue = deque([(x, y)])
    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if 0 <= cx < width and 0 <= cy < height and data[cx, cy][:3] == target_color:
            new_data[cx, cy] = new_color + (255,)
            visited.add((cx, cy))
            queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])