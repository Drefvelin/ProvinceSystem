import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import numpy as np


# -----------------------------
# Utilities
# -----------------------------
def load_provinces_txt(path):
    color_to_id = {}
    id_to_terrain = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" not in line:
                continue

            pid_part, rest = line.split("=", 1)
            pid = int(pid_part.strip())

            parts = [p.strip() for p in rest.split(";")]
            rgb_part = parts[0]
            r, g, b = map(int, rgb_part.split(","))

            color_to_id[(r, g, b)] = pid

            # Parse terrain if present
            terrain = None
            for part in parts[1:]:
                if part.isalpha():
                    terrain = part
                    break

            id_to_terrain[pid] = terrain or "unknown"

    return color_to_id, id_to_terrain


# -----------------------------
# Inspector App
# -----------------------------
class ProvinceInspector:
    def __init__(self, root):
        self.root = root
        self.root.title("Province Inspector")

        # Data
        self.color_to_id = {}
        self.id_to_terrain = {}
        self.image = None
        self.image_np = None

        # View
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start = None

        # Tk
        self.canvas = None
        self.canvas_img = None
        self.display_img = None

        # Info
        self.info_var = tk.StringVar(value="Load provinces.txt and provinces.png")

        self.build_ui()

    # -----------------------------
    # UI
    # -----------------------------
    def build_ui(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack(fill="x")

        ttk.Button(top, text="Load provinces.txt", command=self.load_txt).pack(side="left")
        ttk.Button(top, text="Load provinces.png", command=self.load_png).pack(side="left", padx=6)

        info_frame = ttk.Frame(self.root, padding=6)
        info_frame.pack(fill="x")

        ttk.Label(
            info_frame,
            textvariable=self.info_var,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        self.canvas = tk.Canvas(self.root, bg="black")
        self.canvas.pack(expand=True, fill="both")

        # Bindings
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)

    # -----------------------------
    # Loaders
    # -----------------------------
    def load_txt(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path:
            return

        self.color_to_id, self.id_to_terrain = load_provinces_txt(path)
        self.info_var.set(f"Loaded provinces.txt ({len(self.color_to_id)} provinces)")

    def load_png(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not path:
            return

        self.image = Image.open(path).convert("RGB")
        self.image_np = np.array(self.image)

        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.refresh_view()

    # -----------------------------
    # Interaction
    # -----------------------------
    def on_click(self, e):
        if self.image_np is None or not self.color_to_id:
            return

        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        vw, vh = int(cw / self.zoom), int(ch / self.zoom)

        x0 = int(max(0, min(self.offset_x, self.image.width - vw)))
        y0 = int(max(0, min(self.offset_y, self.image.height - vh)))

        ix = x0 + int(e.x * vw / cw)
        iy = y0 + int(e.y * vh / ch)

        if ix < 0 or iy < 0 or ix >= self.image.width or iy >= self.image.height:
            return

        r, g, b = self.image_np[iy, ix]
        pid = self.color_to_id.get((r, g, b))

        if pid is None:
            self.info_var.set(f"RGB: {r},{g},{b} → no province")
        else:
            terrain = self.id_to_terrain.get(pid, "unknown")
            self.info_var.set(
                f"Province ID: {pid} | Terrain: {terrain} | RGB: {r},{g},{b}"
            )

    def start_pan(self, e):
        self.drag_start = (e.x, e.y)

    def pan(self, e):
        dx, dy = e.x - self.drag_start[0], e.y - self.drag_start[1]
        self.offset_x -= dx / self.zoom
        self.offset_y -= dy / self.zoom
        self.drag_start = (e.x, e.y)
        self.refresh_view()

    def on_zoom(self, e):
        factor = 1.1 if (getattr(e, "delta", 0) > 0 or e.num == 4) else 0.9
        nz = max(0.2, min(6.0, self.zoom * factor))

        cx, cy = e.x, e.y
        ix = cx / self.zoom + self.offset_x
        iy = cy / self.zoom + self.offset_y

        self.zoom = nz
        self.offset_x = ix - cx / self.zoom
        self.offset_y = iy - cy / self.zoom
        self.refresh_view()

    # -----------------------------
    # Render
    # -----------------------------
    def refresh_view(self):
        if self.image is None:
            return

        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        vw, vh = int(cw / self.zoom), int(ch / self.zoom)

        x0 = int(max(0, min(self.offset_x, self.image.width - vw)))
        y0 = int(max(0, min(self.offset_y, self.image.height - vh)))

        img = self.image_np[y0:y0 + vh, x0:x0 + vw]
        img = Image.fromarray(img).resize((cw, ch), Image.NEAREST)

        self.display_img = ImageTk.PhotoImage(img)

        if self.canvas_img is None:
            self.canvas_img = self.canvas.create_image(0, 0, anchor="nw", image=self.display_img)
        else:
            self.canvas.itemconfig(self.canvas_img, image=self.display_img)


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    ProvinceInspector(root)
    root.mainloop()
