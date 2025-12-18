import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import re
import os

TERRAINS = {
    "plains": (60, 80),
    "forest": (30, 40),
    "hills": (15, 30),
    "mountain": (0, 5),
    "bog": (0, 5),
    "drylands": (0, 5),
}


def parse_existing(file_path):
    existing_rgbs = set()
    highest_id = 0

    if not os.path.exists(file_path):
        return existing_rgbs, 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"(\d+)\s*=\s*(\d+),(\d+),(\d+)", line)
            if match:
                pid = int(match.group(1))
                rgb = (int(match.group(2)), int(match.group(3)), int(match.group(4)))
                highest_id = max(highest_id, pid)
                existing_rgbs.add(rgb)

    return existing_rgbs, highest_id


class ProvinceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Province Editor")

        self.file_path = None
        self.existing_rgbs = set()
        self.next_id = 1

        self.build_ui()

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid()

        ttk.Button(frm, text="Select provinces.txt", command=self.select_file).grid(column=0, row=0, columnspan=2, pady=5)

        ttk.Label(frm, text="RGB (r,g,b):").grid(column=0, row=1, sticky="e")
        self.rgb_entry = ttk.Entry(frm, width=20)
        self.rgb_entry.grid(column=1, row=1)

        ttk.Label(frm, text="Terrain:").grid(column=0, row=2, sticky="e")
        self.terrain = tk.StringVar(value="plains")
        ttk.Combobox(frm, textvariable=self.terrain, values=list(TERRAINS.keys()), state="readonly").grid(column=1, row=2)

        ttk.Label(frm, text="Fertility (optional):").grid(column=0, row=3, sticky="e")
        self.fertility_entry = ttk.Entry(frm, width=20)
        self.fertility_entry.grid(column=1, row=3)

        ttk.Button(frm, text="Add Province", command=self.add_province).grid(column=0, row=4, columnspan=2, pady=10)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path:
            return

        self.file_path = path
        self.existing_rgbs, highest_id = parse_existing(path)
        self.next_id = highest_id + 1

        messagebox.showinfo("Loaded", f"Loaded {path}\nNext ID: {self.next_id}")

    def add_province(self):
        if not self.file_path:
            messagebox.showerror("Error", "Select provinces.txt first")
            return

        try:
            r, g, b = map(int, self.rgb_entry.get().split(","))
            rgb = (r, g, b)
        except Exception:
            messagebox.showerror("Error", "RGB must be in format r,g,b")
            return

        if rgb in self.existing_rgbs:
            messagebox.showerror("Error", "Province with this RGB already exists")
            return

        terrain = self.terrain.get()

        fertility_text = self.fertility_entry.get().strip()
        if fertility_text:
            fertility = int(fertility_text)
        else:
            lo, hi = TERRAINS[terrain]
            fertility = random.randint(lo, hi)

        line = f"{self.next_id} = {r},{g},{b};{terrain};{fertility}\n"

        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(line)

        self.existing_rgbs.add(rgb)
        self.next_id += 1

        messagebox.showinfo("Added", line.strip())


if __name__ == "__main__":
    root = tk.Tk()
    ProvinceGUI(root)
    root.mainloop()
