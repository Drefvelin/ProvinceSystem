import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import numpy as np

PURPLE = np.array((160, 80, 200))
BLACK = (0, 0, 0)

# -----------------------------
# Load provinces.txt
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


# -----------------------------
# Compute county RGB
# -----------------------------
def compute_county_rgb(province_ids, id_to_color):
    colors = [np.array(id_to_color[pid]) for pid in province_ids if pid in id_to_color]
    if not colors:
        return "128,0,128"

    avg = np.mean(colors, axis=0)
    blended = avg * 0.6 + PURPLE * 0.4
    blended = np.clip(blended.astype(int), 0, 255)

    return f"{blended[0]},{blended[1]},{blended[2]}"


# -----------------------------
# GUI
# -----------------------------
class CountyCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("County Creator")

        self.color_to_id = {}
        self.id_to_color = {}

        self.image = None
        self.image_np = None
        self.display_img = None

        self.county_path = None
        self.counties = {}

        self.selected_provinces = set()

        # View state
        self.zoom = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 6.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start = None

        self.build_ui()

    # -----------------------------
    # UI
    # -----------------------------
    def build_ui(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack()

        ttk.Button(top, text="Load provinces.txt", command=self.load_provinces).grid(row=0, column=0)
        ttk.Button(top, text="Load provinces.png", command=self.load_map).grid(row=0, column=1)
        ttk.Button(top, text="Load county.json", command=self.load_county_file).grid(row=0, column=2)

        form = ttk.Frame(self.root, padding=5)
        form.pack()

        ttk.Label(form, text="County ID:").grid(row=0, column=0, sticky="e")
        self.county_id_entry = ttk.Entry(form, width=25)
        self.county_id_entry.grid(row=0, column=1)

        ttk.Label(form, text="County Name:").grid(row=1, column=0, sticky="e")
        self.county_name_entry = ttk.Entry(form, width=25)
        self.county_name_entry.grid(row=1, column=1)

        ttk.Button(form, text="Add County", command=self.add_county).grid(
            row=2, column=0, columnspan=2, pady=6
        )

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
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path:
            return
        self.color_to_id, self.id_to_color = load_provinces_txt(path)
        messagebox.showinfo("Loaded", "provinces.txt loaded")

    def load_map(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not path:
            return
        self.image = Image.open(path).convert("RGB")
        self.image_np = np.array(self.image)
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.refresh_map()

    def load_county_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return

        self.county_path = path
        with open(path, "r", encoding="utf-8") as f:
            self.counties = json.load(f) or {}

        messagebox.showinfo("Loaded", f"Loaded {len(self.counties)} counties")
        self.refresh_map()

    # -----------------------------
    # Interaction
    # -----------------------------
    def on_click(self, event):
        if self.image_np is None:
            return

        ix = int(event.x / self.zoom + self.offset_x)
        iy = int(event.y / self.zoom + self.offset_y)

        if iy < 0 or ix < 0 or iy >= self.image_np.shape[0] or ix >= self.image_np.shape[1]:
            return

        color = tuple(self.image_np[iy, ix])
        if color == BLACK or color not in self.color_to_id:
            return

        pid = self.color_to_id[color]

        if pid in self.selected_provinces:
            self.selected_provinces.remove(pid)
        else:
            self.selected_provinces.add(pid)

        self.refresh_map()

    # -----------------------------
    # County creation
    # -----------------------------
    def add_county(self):
        if not self.county_path:
            messagebox.showerror("Error", "Load county.json first")
            return

        cid = self.county_id_entry.get().strip()
        name = self.county_name_entry.get().strip()

        if not cid or not name:
            messagebox.showerror("Error", "County ID and name are required")
            return

        if cid in self.counties:
            messagebox.showerror("Error", f"County ID '{cid}' already exists")
            return

        for c in self.counties.values():
            if c.get("name") == name:
                messagebox.showerror("Error", f"County name '{name}' already exists")
                return

        if not self.selected_provinces:
            messagebox.showerror("Error", "No provinces selected")
            return

        rgb = compute_county_rgb(self.selected_provinces, self.id_to_color)

        self.counties[cid] = {
            "name": name,
            "provinces": sorted(self.selected_provinces),
            "rgb": rgb
        }

        with open(self.county_path, "w", encoding="utf-8") as f:
            json.dump(self.counties, f, indent=2)

        self.selected_provinces.clear()
        self.county_id_entry.delete(0, tk.END)
        self.county_name_entry.delete(0, tk.END)
        self.refresh_map()

        messagebox.showinfo("Added", f"County '{name}' added")

    # -----------------------------
    # Pan / Zoom
    # -----------------------------
    def start_pan(self, event):
        self.drag_start = (event.x, event.y)

    def pan(self, event):
        dx = event.x - self.drag_start[0]
        dy = event.y - self.drag_start[1]
        self.offset_x -= dx / self.zoom
        self.offset_y -= dy / self.zoom
        self.drag_start = (event.x, event.y)
        self.refresh_map()

    def on_zoom(self, event):
        factor = 1.1 if (event.num == 4 or event.delta > 0) else 0.9
        new_zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))

        cx, cy = event.x, event.y
        ix = cx / self.zoom + self.offset_x
        iy = cy / self.zoom + self.offset_y

        self.zoom = new_zoom
        self.offset_x = ix - cx / self.zoom
        self.offset_y = iy - cy / self.zoom
        self.refresh_map()

    # -----------------------------
    # Rendering
    # -----------------------------
    def refresh_map(self):
        if self.image is None:
            return

        assigned = set()
        for c in self.counties.values():
            assigned.update(c["provinces"])

        img_w, img_h = self.image.size
        canvas_w = max(1, self.canvas.winfo_width())
        canvas_h = max(1, self.canvas.winfo_height())

        view_w = int(canvas_w / self.zoom)
        view_h = int(canvas_h / self.zoom)

        x0 = int(max(0, min(self.offset_x, img_w - view_w)))
        y0 = int(max(0, min(self.offset_y, img_h - view_h)))
        x1 = min(img_w, x0 + view_w)
        y1 = min(img_h, y0 + view_h)

        img_np = np.array(self.image)[y0:y1, x0:x1]

        for pid in assigned.union(self.selected_provinces):
            if pid in self.id_to_color:
                mask = (img_np == self.id_to_color[pid]).all(axis=2)
                img_np[mask] = PURPLE

        img = Image.fromarray(img_np).resize(
            (canvas_w, canvas_h), Image.NEAREST
        )

        self.display_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.display_img)


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    CountyCreator(root)
    root.mainloop()
