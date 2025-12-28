import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import numpy as np

SELECT_COLOR = np.array((160, 80, 200), dtype=np.uint8)


# -----------------------------
# Utilities
# -----------------------------
def load_provinces_txt(path):
    color_to_id = {}
    id_to_color = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" not in line:
                continue
            pid, rest = line.split("=")
            pid = int(pid.strip())
            rgb_part = rest.split(";")[0]
            r, g, b = map(int, rgb_part.split(","))

            color_to_id[(r, g, b)] = pid
            id_to_color[pid] = (r, g, b)

    return color_to_id, id_to_color


def parse_rgb(rgb_str):
    return np.array(list(map(int, rgb_str.split(","))), dtype=np.uint8)


def rgb_to_str(rgb):
    return f"{int(rgb[0])},{int(rgb[1])},{int(rgb[2])}"


def tweak_rgb_near(base_rgb, used_rgb):
    base = np.array(base_rgb, dtype=np.int16)
    if tuple(base) not in used_rgb:
        return base.astype(np.uint8)

    for d in [1, -1, 2, -2, 3, -3, 5, -5, 8, -8, 10, -10]:
        for axis in range(3):
            cand = base.copy()
            cand[axis] += d
            cand = np.clip(cand, 0, 255).astype(np.uint8)
            if tuple(cand) not in used_rgb:
                return cand

    return base.astype(np.uint8)


# -----------------------------
# GUI
# -----------------------------
class CountyCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("County Creator")

        # Data
        self.color_to_id = {}
        self.id_to_color = {}
        self.counties = {}
        self.county_path = None
        self.province_to_county = {}

        # Images
        self.image = None
        self.image_np = None
        self.province_map = None
        self.rendered_map = None

        # Selection
        self.selected_provinces = []
        self.selected_set = set()

        # Modes
        self.delete_mode = False

        # View
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start = None

        # Tk
        self.canvas = None
        self.canvas_img = None
        self.display_img = None
        self.initialized = False

        self.build_ui()

    # -----------------------------
    # UI
    # -----------------------------
    def build_ui(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack(fill="x")

        ttk.Button(top, text="Load provinces.txt", command=self.load_provinces).grid(row=0, column=0)
        ttk.Button(top, text="Load provinces.png", command=self.load_map).grid(row=0, column=1)
        ttk.Button(top, text="Load county.json", command=self.load_counties).grid(row=0, column=2)

        self.init_btn = ttk.Button(top, text="Init", command=self.init_app, state="disabled")
        self.init_btn.grid(row=0, column=3, padx=10)

        ttk.Button(top, text="Add County", command=self.add_county).grid(row=0, column=4)
        ttk.Button(top, text="Delete County", command=self.enable_delete_mode).grid(row=0, column=5)

        self.canvas = tk.Canvas(self.root, bg="black")
        self.canvas.pack(expand=True, fill="both")

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)

    # -----------------------------
    # Loaders
    # -----------------------------
    def load_provinces(self):
        p = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if not p:
            return
        self.color_to_id, self.id_to_color = load_provinces_txt(p)
        self.check_ready()

    def load_map(self):
        p = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
        if not p:
            return
        self.image = Image.open(p).convert("RGB")
        self.image_np = np.array(self.image)
        self.offset_x = self.offset_y = 0
        self.zoom = 1.0
        self.check_ready()

    def load_counties(self):
        p = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not p:
            return
        self.county_path = p
        with open(p, "r", encoding="utf-8") as f:
            self.counties = json.load(f) or {}
        self.check_ready()

    def check_ready(self):
        if self.color_to_id and self.image_np is not None and self.county_path:
            self.init_btn.config(state="normal")

    # -----------------------------
    # INIT
    # -----------------------------
    def init_app(self):
        self.build_province_map()
        self.rebuild_province_to_county()
        self.assign_county_colors()
        self.rebuild_rendered_map()

        self.initialized = True
        self.init_btn.config(state="disabled")
        self.refresh_view()

    def build_province_map(self):
        h, w, _ = self.image_np.shape
        self.province_map = np.full((h, w), -1, dtype=np.int32)

        packed = (
            (self.image_np[:, :, 0].astype(np.int32) << 16)
            | (self.image_np[:, :, 1].astype(np.int32) << 8)
            | self.image_np[:, :, 2].astype(np.int32)
        )

        lookup = {(r << 16) | (g << 8) | b: pid for (r, g, b), pid in self.color_to_id.items()}
        for c, pid in lookup.items():
            self.province_map[packed == c] = pid

    def rebuild_province_to_county(self):
        self.province_to_county.clear()
        for cid, c in self.counties.items():
            for pid in c.get("provinces", []):
                self.province_to_county[int(pid)] = cid

    def assign_county_colors(self):
        used = set()
        for cid, county in self.counties.items():
            provs = county.get("provinces", [])
            base = self.id_to_color.get(int(provs[0]), (128, 0, 128)) if provs else (128, 0, 128)
            rgb = tweak_rgb_near(base, used)
            used.add(tuple(rgb))
            county["rgb"] = rgb_to_str(rgb)

        with open(self.county_path, "w", encoding="utf-8") as f:
            json.dump(self.counties, f, indent=2)

    def rebuild_rendered_map(self):
        self.rendered_map = self.image_np.copy()
        for pid, cid in self.province_to_county.items():
            self.rendered_map[self.province_map == pid] = parse_rgb(self.counties[cid]["rgb"])

    # -----------------------------
    # Interaction
    # -----------------------------
    def enable_delete_mode(self):
        if not self.initialized:
            return
        self.delete_mode = True
        self.canvas.config(cursor="X_cursor")

    def on_click(self, e):
        if not self.initialized:
            return

        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        vw, vh = int(cw / self.zoom), int(ch / self.zoom)

        x0 = int(max(0, min(self.offset_x, self.image.width - vw)))
        y0 = int(max(0, min(self.offset_y, self.image.height - vh)))

        ix = x0 + int(e.x * vw / cw)
        iy = y0 + int(e.y * vh / ch)

        pid = int(self.province_map[iy, ix])
        if pid == -1:
            return

        # DELETE MODE
        if self.delete_mode:
            cid = self.province_to_county.get(pid)
            if not cid:
                self.exit_delete_mode()
                return

            if not messagebox.askyesno("Delete County", f"Delete {cid}?"):
                self.exit_delete_mode()
                return

            del self.counties[cid]
            self.rebuild_province_to_county()
            self.assign_county_colors()
            self.rebuild_rendered_map()
            self.refresh_view()

            self.exit_delete_mode()
            return

        # NORMAL SELECTION
        if pid in self.province_to_county:
            return

        if pid in self.selected_set:
            self.selected_set.remove(pid)
            self.selected_provinces.remove(pid)
        else:
            self.selected_set.add(pid)
            self.selected_provinces.append(pid)

        self.refresh_view()

    def exit_delete_mode(self):
        self.delete_mode = False
        self.canvas.config(cursor="")

    def add_county(self):
        if not self.selected_provinces:
            messagebox.showerror("Error", "No provinces selected")
            return

        cid = f"COUNTY_{len(self.counties) + 1}"
        self.counties[cid] = {
            "name": cid,
            "provinces": list(self.selected_provinces),
            "rgb": "0,0,0",
        }

        self.selected_provinces.clear()
        self.selected_set.clear()

        self.rebuild_province_to_county()
        self.assign_county_colors()
        self.rebuild_rendered_map()
        self.refresh_view()

        with open(self.county_path, "w", encoding="utf-8") as f:
            json.dump(self.counties, f, indent=2)

        messagebox.showinfo("Added", f"{cid} added")

    # -----------------------------
    # View
    # -----------------------------
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

    def refresh_view(self):
        if not self.initialized:
            return

        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        vw, vh = int(cw / self.zoom), int(ch / self.zoom)

        x0 = int(max(0, min(self.offset_x, self.image.width - vw)))
        y0 = int(max(0, min(self.offset_y, self.image.height - vh)))

        img = self.rendered_map[y0:y0 + vh, x0:x0 + vw]

        if self.selected_provinces:
            vis = self.province_map[y0:y0 + vh, x0:x0 + vw]
            img = img.copy()
            img[np.isin(vis, self.selected_provinces)] = SELECT_COLOR

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
    CountyCreator(root)
    root.mainloop()
