# main_ui.py
import tkinter as tk
from tkinter import ttk
import os
import sys

try:
    from ...fryng_core.fryng_run import (
        load_synergy_data,
        update_synergy_step,
        run_synergy_logic
    )
except ImportError:
    # fallback placeholders
    def load_synergy_data():
        return {"potential": 0.1, "symmetry": 0.2, "flow": 0.3,
                "connectivity": 0.4, "emergence": 0.5, "recursion": 0.6}
    def update_synergy_step(step, val):
        print("placeholder update synergy step:", step, val)
    def run_synergy_logic():
        print("placeholder synergy logic")


def launch_ui():
    root = tk.Tk()
    root.title("Fryng UI - 6-Step Synergy")

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    # show synergy in a label
    synergy_lbl = ttk.Label(frame, text="(No synergy loaded yet)")
    synergy_lbl.pack(pady=5)

    def refresh_synergy_label():
        synergy = load_synergy_data()
        synergy_text = "\n".join(f"{k}: {v}" for k, v in synergy.items() if isinstance(v, float))
        synergy_lbl.config(text=f"Synergy:\n{synergy_text}")

    # Button to refresh synergy from file
    refresh_button = ttk.Button(frame, text="Refresh Synergy", command=refresh_synergy_label)
    refresh_button.pack(pady=5)

    # run synergy logic button
    run_button = ttk.Button(frame, text="Run Synergy Logic", command=run_synergy_logic)
    run_button.pack(pady=5)

    # Example slider controlling 'flow'
    flow_label = ttk.Label(frame, text="Flow: ???")
    flow_label.pack(pady=5)

    flow_var = tk.DoubleVar(value=0.3)  # default

    def on_flow_change(*args):
        val = flow_var.get()
        flow_label.config(text=f"Flow: {val:.2f}")
        # Update synergy step in synergy_attrs.json
        update_synergy_step("flow", val)

    flow_slider = ttk.Scale(frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                            variable=flow_var, command=lambda e: on_flow_change())
    flow_slider.pack(pady=5)

    # finalize window
    root.mainloop()


if __name__ == "__main__":
    launch_ui()
