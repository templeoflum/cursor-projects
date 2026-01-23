
"""
master_ui_paned.py
----------------------------------------------------------------------
A Tkinter UI using PanedWindows for a more balanced, resizable layout:
1) A vertical PanedWindow splits the top synergy content from the bottom debug.
2) Another horizontal PanedWindow in the top splits step controls on the left
   from the synergy table on the right.
3) The bottom is a larger debug log area, easily adjustable by the user.

It still includes:
 - Step offsets & expansions for each step
 - A synergy table displaying synergy after each step
 - A global synergy seed slider
 - Buttons to run node.py or update.py, capturing logs in a scrolled text area.

Usage:
  python master_ui_paned.py
"""

import os
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import synergy_engine  # from synergy_engine.py

# Utility: gather step folders
def get_step_folders(steps_root="steps"):
    folders = []
    if not os.path.isdir(steps_root):
        return folders
    for item in sorted(os.listdir(steps_root)):
        step_path = os.path.join(steps_root, item)
        if os.path.isdir(step_path) and item.startswith(("01_", "02_", "03_", "04_", "05_", "06_")):
            folders.append(item)
    return folders

class StepUI:
    """
    Step controls: offset slider & expansions checkbutton
    """
    def __init__(self, parent, folder_name, short_name, on_change_callback):
        self.folder_name = folder_name
        self.stepName = short_name
        self.offsetVar = tk.DoubleVar(value=0.0)
        self.expansionsVar = tk.BooleanVar(value=False)

        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=5, pady=5)

        lbl = tk.Label(frame, text=short_name, width=12, anchor='w')
        lbl.pack(side=tk.LEFT, padx=5)

        offset_slider = tk.Scale(
            frame,
            from_=-0.2,
            to=0.2,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            length=120,
            variable=self.offsetVar,
            command=lambda val: on_change_callback()
        )
        offset_slider.pack(side=tk.LEFT, padx=5)

        expansions_cb = tk.Checkbutton(
            frame,
            text="Expansions",
            variable=self.expansionsVar,
            command=on_change_callback
        )
        expansions_cb.pack(side=tk.LEFT, padx=5)

    def to_dict(self):
        return {
            'stepName': self.stepName,
            'offset': self.offsetVar.get(),
            'expansions': self.expansionsVar.get()
        }

class MasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Synergy + Management (Paned Layout)")

        # Build top-level vertical PanedWindow
        self.vertical_pane = tk.PanedWindow(root, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        self.vertical_pane.pack(fill=tk.BOTH, expand=True)

        # Within the top portion, create a horizontal PanedWindow
        self.top_pane = tk.PanedWindow(self.vertical_pane, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        
        # We'll add synergy content to top_pane
        # Then the bottom debug area will be a second pane in vertical_pane

        # Step 1: synergy (top) frame => further split horizontally
        #   left: step controls
        #   right: synergy table

        # Left frame for step controls
        self.steps_frame = tk.Frame(self.top_pane, bd=2, relief=tk.GROOVE)
        # Right frame for synergy table
        self.table_frame = tk.Frame(self.top_pane, bd=2, relief=tk.GROOVE)

        self.top_pane.add(self.steps_frame, width=300)   # initial width for step controls
        self.top_pane.add(self.table_frame, stretch="always")  # synergy table can stretch

        # Add the top_pane to vertical_pane
        self.vertical_pane.add(self.top_pane, height=400)  # set an initial height for synergy portion

        # Step 2: bottom debug frame
        self.debug_frame = tk.Frame(self.vertical_pane, bd=2, relief=tk.SUNKEN)
        self.vertical_pane.add(self.debug_frame, height=200)  # initial height for debug

        # In the top synergy portion, we place:
        # - step controls on the left
        # - synergy table on the right
        # - synergy seed slider + management buttons at the bottom of the steps_frame

        # Gather step folders
        step_folders = get_step_folders("steps")

        self.stepUIs = []
        if not step_folders:
            msg_lbl = tk.Label(self.steps_frame, text="No steps found in 'steps' folder.")
            msg_lbl.pack(padx=20, pady=20)
        else:
            for folder in step_folders:
                short_name = folder.split("_", 1)[1] if "_" in folder else folder
                ui = StepUI(self.steps_frame, folder, short_name, on_change_callback=self.on_controls_changed)
                self.stepUIs.append(ui)

        # synergy table in table_frame
        self.synergy_table = ttk.Treeview(self.table_frame, columns=("synergy_val",), show="tree headings")
        self.synergy_table.heading("#0", text="Step")
        self.synergy_table.column("#0", width=120, stretch=False)
        self.synergy_table.heading("synergy_val", text="Synergy")
        self.synergy_table.column("synergy_val", width=100, stretch=False)
        self.synergy_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # synergy seed slider + mgmt tools at the bottom of steps_frame
        bottom_subframe = tk.Frame(self.steps_frame, bd=1, relief=tk.GROOVE)
        bottom_subframe.pack(side=tk.BOTTOM, fill=tk.X)

        seed_label = tk.Label(bottom_subframe, text="Seed: 0.50")
        seed_label.pack(side=tk.LEFT, padx=5)

        self.seed_value = tk.DoubleVar(value=0.5)
        def on_seed_move(val):
            seed_label.config(text=f"Seed: {float(val):.2f}")
            self.on_controls_changed()

        seed_slider = tk.Scale(
            bottom_subframe,
            from_=0.0, to=1.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            length=150,
            label="Global Seed",
            variable=self.seed_value,
            command=on_seed_move
        )
        seed_slider.pack(side=tk.LEFT, padx=5)

        # management buttons
        mgmt_btn_frame = tk.Frame(bottom_subframe)
        mgmt_btn_frame.pack(side=tk.RIGHT, padx=5)

        node_btn = tk.Button(mgmt_btn_frame, text="Generate Steps (node.py)", command=self.run_node_script)
        node_btn.pack(side=tk.TOP, pady=3, fill=tk.X)

        update_btn = tk.Button(mgmt_btn_frame, text="Update Steps (update.py)", command=self.run_update_script)
        update_btn.pack(side=tk.TOP, pady=3, fill=tk.X)

        # debug area in debug_frame
        self.log_area = scrolledtext.ScrolledText(self.debug_frame, wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # initial synergy calc
        self.on_controls_changed()

    def on_controls_changed(self):
        """
        Recompute synergy each time offsets/expansions or seed changes,
        then display synergy for each step in synergy_table
        """
        synergy_input = []
        for sUI in self.stepUIs:
            synergy_input.append(sUI.to_dict())

        results = synergy_engine.run_feedback_loop(synergy_input, self.seed_value.get())

        self.synergy_table.delete(*self.synergy_table.get_children())
        for step_name, synergy_val in results.items():
            synergy_val_str = f"{synergy_val:.3f}"
            self.synergy_table.insert("", "end", text=step_name, values=(synergy_val_str,))

    def run_node_script(self):
        """
        Calls node.py, capturing output in log_area
        """
        self.log_area.insert(tk.END, "\n=== Running node.py ===\n")
        self.log_area.see(tk.END)
        self.log_area.update_idletasks()

        cmd = ["python", "node.py"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout:
            self.log_area.insert(tk.END, result.stdout + "\n")
        if result.stderr:
            self.log_area.insert(tk.END, "[ERROR] " + result.stderr + "\n")

        self.log_area.insert(tk.END, "=== node.py finished ===\n")
        self.log_area.see(tk.END)

    def run_update_script(self):
        """
        Calls update.py, capturing output in log_area
        """
        self.log_area.insert(tk.END, "\n=== Running update.py ===\n")
        self.log_area.see(tk.END)
        self.log_area.update_idletasks()

        cmd = ["python", "update.py"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout:
            self.log_area.insert(tk.END, result.stdout + "\n")
        if result.stderr:
            self.log_area.insert(tk.END, "[ERROR] " + result.stderr + "\n")

        self.log_area.insert(tk.END, "=== update.py finished ===\n")
        self.log_area.see(tk.END)

def main():
    root = tk.Tk()
    app = MasterApp(root)
    # let's start with a bigger default
    root.geometry("1000x700")
    root.mainloop()

if __name__ == "__main__":
    main()
