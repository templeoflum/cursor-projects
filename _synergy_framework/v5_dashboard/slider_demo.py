
"""
resistant_slider_full_tuned.py
----------------------------------------------------------------------
A stable, physically-based synergy slider with:

1) A main synergy slider. During drag:
   - synergy EXACTLY = user input (no external forces).
2) On release:
   - synergy tries to remain at synergyCenter (the last synergy),
   - boundary repulsion keeps synergy away from 0 or 1,
   - velocity-based with friction for smooth transitions,
   - optional scaling mode for boundary force: normal, pi, phi.

We also have 3 param sliders + 1 combobox:
 - alpha_slider  : synergy force pulling synergy -> synergyCenter
 - boundary_slider: base boundary factor
 - friction_slider: velocity damping each frame
 - scaling_box (combobox): multiply boundary by pi or phi (or none)

If synergy is pinned near the edges, you might see boundary repulsion push it 
inward after release, but user can forcibly hold synergy at edges while dragging.
"""

import tkinter as tk
from tkinter import ttk
import math
import time

class ResistantSliderFullTuned:
    def __init__(self, master):
        self.master = master
        master.title("Resistant Slider: Balanced & Debug Sliders")

        # synergy position & velocity
        self.synergy = 0.5
        self.velocity = 0.0
        # user tries to move synergy_slider => synergy = user_input while dragging
        self.user_input = 0.5
        # synergyCenter is the last synergy at time of release
        self.synergyCenter = 0.5
        # dragging state
        self.is_dragging = False

        # Main synergy label
        self.synergy_label = tk.Label(master, text="Synergy: 0.50", font=("Arial", 14))
        self.synergy_label.pack(pady=5)

        # synergy slider
        self.synergy_slider = tk.Scale(
            master,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            length=320,
            command=self.on_slider_move
        )
        self.synergy_slider.set(self.synergy)
        self.synergy_slider.pack(pady=5)

        # bind press/release
        self.synergy_slider.bind("<ButtonPress-1>", self.start_drag)
        self.synergy_slider.bind("<ButtonRelease-1>", self.stop_drag)

        # Tuning param frame
        param_frame = tk.LabelFrame(master, text="Tuning & Debug")
        param_frame.pack(padx=10, pady=10, fill=tk.X)

        # 1) alpha: synergy -> synergyCenter
        self.alpha_var = tk.DoubleVar(value=2.5)
        self.build_param_slider(
            parent=param_frame,
            label_text="Alpha Force",
            var=self.alpha_var,
            from_=0.0, to_=10.0,
            resolution=0.1
        )

        # 2) boundary: base factor
        self.boundary_var = tk.DoubleVar(value=3.0)
        self.build_param_slider(
            parent=param_frame,
            label_text="Boundary",
            var=self.boundary_var,
            from_=0.0, to_=10.0,
            resolution=0.1
        )

        # 3) friction: velocity damping
        self.friction_var = tk.DoubleVar(value=0.9)
        self.build_param_slider(
            parent=param_frame,
            label_text="Friction",
            var=self.friction_var,
            from_=0.5, to_=0.99,
            resolution=0.01
        )

        # 4) scaling mode
        # We'll apply pi or phi to boundary force or friction, your choice.
        # Let's do boundary force multiplied by scale_factor from combobox
        self.scaling_mode = tk.StringVar(value="normal")
        scale_frame = tk.Frame(param_frame)
        scale_frame.pack(fill=tk.X, pady=3)
        scale_label = tk.Label(scale_frame, text="Scaling Mode:", width=12, anchor='w')
        scale_label.pack(side=tk.LEFT, padx=5)
        self.scaling_box = ttk.Combobox(
            scale_frame,
            textvariable=self.scaling_mode,
            values=["normal", "pi", "phi"],
            state="readonly"
        )
        self.scaling_box.pack(side=tk.LEFT)
        self.scaling_box.bind("<<ComboboxSelected>>", lambda e: None)

        # time-based updates
        self.dt = 0.016  # ~60 fps
        self.prev_time = time.time()

        self.update_synergy()

    def build_param_slider(self, parent, label_text, var, from_, to_, resolution):
        row = tk.Frame(parent)
        row.pack(fill=tk.X, padx=5, pady=2)
        lbl = tk.Label(row, text=label_text, width=10, anchor='w')
        lbl.pack(side=tk.LEFT)
        s = tk.Scale(
            row,
            from_=from_,
            to=to_,
            resolution=resolution,
            orient=tk.HORIZONTAL,
            length=150,
            variable=var
        )
        s.pack(side=tk.LEFT)

    # synergy slider drag events
    def on_slider_move(self, val_str):
        self.user_input = float(val_str)

    def start_drag(self, event):
        self.is_dragging = True
        self.velocity = 0.0

    def stop_drag(self, event):
        self.is_dragging = False
        # synergy becomes synergyCenter
        self.synergyCenter = self.synergy

    # boundary force
    def boundary_force(self, s):
        """
        If synergy is near 0 or 1, push synergy away strongly.
        We'll do base factor * scale / dist^2
        scale = 1 if normal, pi if pi, or phi if phi
        """
        base = self.boundary_var.get()
        scale_mode = self.scaling_mode.get()
        if scale_mode == "pi":
            scale_factor = math.pi
        elif scale_mode == "phi":
            scale_factor = (1 + math.sqrt(5))/2  # ~1.618
        else:
            scale_factor = 1.0

        factor = base * scale_factor

        force = 0.0
        eps = 1e-6

        # if synergy <0.05 => push synergy up
        if s < 0.05:
            dist = max(s**2, eps)
            force += factor / dist
        # if synergy>0.95 => push synergy down
        if s>0.95:
            dist = max((1-s)**2, eps)
            force -= factor / dist

        return force

    def update_synergy(self):
        now = time.time()
        dt = self.dt
        # if too big dt => clamp
        if (now - self.prev_time)>0.1:
            self.prev_time = now
        else:
            self.prev_time = now

        if self.is_dragging:
            # synergy = user_input
            self.synergy = self.user_input
            self.velocity = 0.0
        else:
            # physics
            alpha = self.alpha_var.get()
            friction = self.friction_var.get()

            # net force
            net_force = 0.0

            # 1) synergy => synergyCenter
            net_force += alpha*(self.synergyCenter - self.synergy)

            # 2) boundary repulsion
            net_force += self.boundary_force(self.synergy)

            # velocity
            self.velocity += net_force*dt
            # friction
            self.velocity *= friction

            new_synergy = self.synergy + self.velocity*dt
            # clamp synergy
            if new_synergy<0.0:
                new_synergy=0.0
                self.velocity=0.0
            elif new_synergy>1.0:
                new_synergy=1.0
                self.velocity=0.0

            self.synergy = new_synergy

        # update UI
        self.synergy_slider.set(self.synergy)
        self.synergy_label.config(text=f"Synergy: {self.synergy:.3f}")

        self.master.after(int(dt*1000), self.update_synergy)

def main():
    root = tk.Tk()
    app = ResistantSliderFullTuned(root)
    root.geometry("560x380")
    root.mainloop()

if __name__ == "__main__":
    main()
