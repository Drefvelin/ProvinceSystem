"""Generate a simple classic 64x64 Steve-like skin for the mannequin."""
from pathlib import Path

from PIL import Image, ImageDraw

img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

skin = (198, 134, 96, 255)
hair = (78, 52, 36, 255)
shirt = (55, 120, 180, 255)
pants = (50, 55, 150, 255)
shoes = (45, 35, 30, 255)
eye_w = (255, 255, 255, 255)
eye_b = (40, 80, 140, 255)
mouth = (120, 70, 55, 255)
hat = (60, 40, 28, 180)


def fill(box: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    d.rectangle(box, fill=color)


# Head
fill((8, 0, 15, 7), hair)
fill((16, 0, 23, 7), skin)
fill((0, 8, 7, 15), skin)
fill((8, 8, 15, 15), skin)
fill((16, 8, 23, 15), skin)
fill((24, 8, 31, 15), hair)
fill((10, 12, 11, 13), eye_w)
fill((13, 12, 14, 13), eye_w)
fill((10, 12, 10, 13), eye_b)
fill((13, 12, 13, 13), eye_b)
fill((11, 14, 12, 14), mouth)
fill((8, 8, 15, 9), hair)
fill((40, 0, 47, 7), hat)
fill((40, 8, 47, 15), hat)

# Body
fill((20, 16, 27, 19), shirt)
fill((28, 16, 35, 19), shirt)
fill((16, 20, 19, 31), shirt)
fill((20, 20, 27, 31), shirt)
fill((28, 20, 31, 31), shirt)
fill((32, 20, 39, 31), shirt)

# Right arm
fill((44, 16, 47, 19), skin)
fill((48, 16, 51, 19), skin)
fill((40, 20, 43, 31), skin)
fill((44, 20, 47, 31), skin)
fill((48, 20, 51, 31), skin)
fill((52, 20, 55, 31), skin)
fill((44, 20, 47, 23), shirt)

# Left arm (modern layout)
fill((36, 48, 39, 51), skin)
fill((40, 48, 43, 51), skin)
fill((32, 52, 35, 63), skin)
fill((36, 52, 39, 63), skin)
fill((40, 52, 43, 63), skin)
fill((44, 52, 47, 63), skin)
fill((36, 52, 39, 55), shirt)

# Right leg
fill((4, 16, 7, 19), pants)
fill((8, 16, 11, 19), shoes)
fill((0, 20, 3, 31), pants)
fill((4, 20, 7, 31), pants)
fill((8, 20, 11, 31), pants)
fill((12, 20, 15, 31), pants)
fill((4, 28, 7, 31), shoes)

# Left leg (modern)
fill((20, 48, 23, 51), pants)
fill((24, 48, 27, 51), shoes)
fill((16, 52, 19, 63), pants)
fill((20, 52, 23, 63), pants)
fill((24, 52, 27, 63), pants)
fill((28, 52, 31, 63), pants)
fill((20, 60, 23, 63), shoes)

out = Path(__file__).resolve().parents[1] / "public" / "skins" / "skin.png"
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out)
print(f"wrote {out} {img.size}")
