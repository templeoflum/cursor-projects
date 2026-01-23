
import tkinter as tk
from tkinter import ttk
import os
import time

# direct import aggregator from same folder
import synergy_aggregator

REFRESH_INTERVAL_MS = 1500

class SynergyMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Synergy Visual Test")
        self.geometry("400x300")

        self.widget_map = {}
        self.synergy_data = {}

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.inner_frame = ttk.Frame(self.canvas)
        self.inner_frame.bind("<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas_frame = self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # after 1.5s, call update loop
        self.after(REFRESH_INTERVAL_MS, self.update_synergy_loop)

    def update_synergy_loop(self):
        print("[SynergyMonitor] Poll aggregator ...")
        new_data = synergy_aggregator.aggregate_synergy()
        print("[SynergyMonitor] aggregator =>", new_data)

        new_keys = set(new_data.keys())
        old_keys = set(self.widget_map.keys())

        # create widgets for new synergy keys
        for key in new_keys.difference(old_keys):
            row_frame = ttk.Frame(self.inner_frame)
            row_frame.pack(fill=tk.X, pady=2)

            label = ttk.Label(row_frame, text=f"{key}:")
            label.pack(side=tk.LEFT, padx=5)

            val = new_data[key]
            if 0.0 <= val <= 1.0:
                pb_var = tk.DoubleVar(value=val)
                pb = ttk.Progressbar(row_frame, length=150, variable=pb_var, maximum=1.0)
                pb.pack(side=tk.LEFT, padx=5)
                self.widget_map[key] = ("progress", pb_var)
            else:
                val_label = ttk.Label(row_frame, text=f"{val}")
                val_label.pack(side=tk.LEFT, padx=5)
                self.widget_map[key] = ("label", val_label)

        # update existing synergy keys
        for key in new_keys.intersection(old_keys):
            val = new_data[key]
            w_type, widget = self.widget_map[key]
            if w_type == "progress":
                widget.set(val if val <= 1.0 else 1.0)
            else:
                widget.config(text=f"{val:.2f}")

        self.synergy_data = new_data
        self.after(REFRESH_INTERVAL_MS, self.update_synergy_loop)

def run_synergy_visual():
    app = SynergyMonitor()
    app.mainloop()

if __name__ == "__main__":
    run_synergy_visual()
