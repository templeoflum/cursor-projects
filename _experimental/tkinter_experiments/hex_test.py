import tkinter as tk
import random
import math

# -- Constants / config
ATTR_NAMES = ["potential", "symmetry", "flow", "connectivity", "emergence", "recursion"]

# Coordinates for a simple ring of 6 hex positions around center
# (center_x, center_y), each with a small offset
HEX_COORDS = [
    ( 0, -1),  # top
    ( 0.866, -0.5),  # top-right
    ( 0.866,  0.5),  # bottom-right
    ( 0,      1),  # bottom
    (-0.866,  0.5),  # bottom-left
    (-0.866, -0.5)   # top-left
]
HEX_RADIUS = 40   # size of each hex cell on screen
CANVAS_SIZE = 400 # width & height

class AttributeSystem:
    """
    Holds the 6 attributes, the seed, and any custom 'universal law',
    'tuning function', and 'run function' you'd like to define.
    """
    def __init__(self, seed=0.5):
        self.seed = seed
        # Initialize all attributes in [0,1]
        self.values = {
            "potential":   0.5,
            "symmetry":    0.5,
            "flow":        0.5,
            "connectivity":0.5,
            "emergence":   0.5,
            "recursion":   0.5
        }

    def universal_law(self):
        """
        Placeholder for a 'universal law' that might constrain attributes
        or couple them. Here we just ensure all remain in [0,1].
        """
        for k in self.values:
            v = self.values[k]
            self.values[k] = max(0.0, min(1.0, v))

    def tuning_function(self, attr_name):
        """
        Placeholder for a 'tuning function' that modifies an attribute
        based on the seed or other factors. (Completely arbitrary here.)
        """
        base_val = self.values[attr_name]
        # Example: shift the attribute slightly toward the seed
        self.values[attr_name] = 0.9 * base_val + 0.1 * self.seed

    def run_step(self):
        """
        The 'run function': each step, we:
          1) apply some random offset,
          2) use a tuning function,
          3) enforce the universal law.
        """
        for k in self.values:
            # inject small random offset in [-0.02, 0.02]
            self.values[k] += random.uniform(-0.02, 0.02)
            # custom tuning
            self.tuning_function(k)
        # clamp after modifications
        self.universal_law()

class HexGridDisplay(tk.Frame):
    """
    A lightweight display that draws 6 hexes on a canvas, each labeled
    with an attribute name and color-coded by that attribute’s [0..1] value.
    """
    def __init__(self, master, attr_system):
        super().__init__(master)
        self.attr_system = attr_system
        self.canvas = tk.Canvas(self, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Keep references to drawn hexagons and labels
        self.hex_shapes = {}
        self.hex_labels = {}

        self.draw_hexes()

    def draw_hexes(self):
        """
        Create the 6 hex shapes (once), store their canvas IDs, and also
        create text labels. Coordinates in HEX_COORDS are scaled & centered.
        """
        cx = CANVAS_SIZE // 2
        cy = CANVAS_SIZE // 2
        scale = 100  # distance factor from center

        for i, name in enumerate(ATTR_NAMES):
            hx = cx + HEX_COORDS[i][0] * scale
            hy = cy + HEX_COORDS[i][1] * scale

            # Draw the hex polygon
            points = self._hex_points(hx, hy, HEX_RADIUS)
            color = self._value_to_color(self.attr_system.values[name])
            hex_id = self.canvas.create_polygon(points, fill=color, outline="black")
            
            # Label in center of the hex
            label_id = self.canvas.create_text(hx, hy, text=name, fill="black")

            self.hex_shapes[name] = hex_id
            self.hex_labels[name] = label_id

    def update_hexes(self):
        """
        Update the fill color for each hex based on the attribute value,
        and optionally update any label text if desired.
        """
        for name in ATTR_NAMES:
            val = self.attr_system.values[name]
            color = self._value_to_color(val)
            self.canvas.itemconfig(self.hex_shapes[name], fill=color)
            # (Optional) update the text to show numeric value
            self.canvas.itemconfig(self.hex_labels[name], text=f"{name}\n{val:.2f}")

    def _hex_points(self, cx, cy, r):
        """
        Return the (x, y) points of a regular hex centered at (cx, cy)
        with 'radius' r.
        """
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30  # shift so one vertex is top
            angle_rad = math.radians(angle_deg)
            x = cx + r * math.cos(angle_rad)
            y = cy + r * math.sin(angle_rad)
            points.append((x, y))
        # Flatten for create_polygon
        flat = []
        for p in points:
            flat.extend(p)
        return flat

    def _value_to_color(self, val):
        """
        Convert a [0..1] value to a simple grayscale or color hex.
        Here, we do grayscale. Feel free to adapt (e.g., to rainbow).
        """
        shade = int(val * 255)
        return f"#{shade:02x}{shade:02x}{shade:02x}"

class MainApp(tk.Frame):
    """
    Brings everything together: a seed slider, the AttributeSystem,
    and the HexGridDisplay. Runs an update loop that evolves the system.
    """
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        # The underlying model
        self.attr_system = AttributeSystem(seed=0.5)

        # UI elements
        # 1) A slider to adjust the central 'seed'
        self.seed_var = tk.DoubleVar(value=self.attr_system.seed)
        tk.Label(self, text="Seed").pack()
        tk.Scale(self, from_=0.0, to=1.0, resolution=0.01,
                 orient=tk.HORIZONTAL, variable=self.seed_var,
                 command=self.update_seed).pack(fill=tk.X)

        # 2) The hex display
        self.hex_view = HexGridDisplay(self, self.attr_system)
        self.hex_view.pack()

        # Start the animation loop
        self.update_loop()

    def update_seed(self, *args):
        """
        Whenever the slider changes, update the system’s seed.
        """
        self.attr_system.seed = self.seed_var.get()

    def update_loop(self):
        """
        Periodic update: step the system, redraw, and schedule again.
        """
        self.attr_system.run_step()      # update attribute values
        self.hex_view.update_hexes()     # re-color the hexes
        self.after(100, self.update_loop)

def main():
    root = tk.Tk()
    root.title("Seed & 6 Attributes (Hex Grid)")
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
