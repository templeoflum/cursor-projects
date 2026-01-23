"""
hex_steps_isometric_ui_expansions_final_bordered.py

Features:
 - Reverts expansions-based approach (expansionsOnVar, expansionsVal, label "Exp?" etc.).
 - Adds Start/Stop button that toggles expansions+cycles for all steps.
 - Replaces inline debug scrolled text with "Show Debug" popup.
 - Adds borders to synergy table, bar chart, bottom tools, and synergy lines frames for a uniform look.
 - Auto-centers bar chart on resize, synergy lines on the right with centerX=408.

"""

import math
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess

import synergy_engine  # synergy_engine.run_feedback_loop(...) => dict

STEP_NAMES = ["Potential","Symmetry","Flow","Connectivity","Emergence","Recursion"]

###############################################################################
# StepNodeUI
###############################################################################
class StepNodeUI:
    """One node representing expansions + cycle controls for a single step."""
    def __init__(self, parent_canvas, stepName, index, config, on_change_callback):
        self.canvas = parent_canvas
        self.stepName = stepName
        self.index = index
        self.config = config
        self.on_change_callback = on_change_callback

        # Offset
        self.offsetVar = tk.DoubleVar(value=0.0)

        # Expansions
        self.expansionsOnVar = tk.BooleanVar(value=False)
        self.expansionsVal = tk.DoubleVar(value=0.3)

        # Cycle
        self.cycleVar = tk.BooleanVar(value=False)
        self.freqVar = tk.DoubleVar(value=0.04)
        self.amplitudeVar = tk.DoubleVar(value=0.03)

        # Build sub-frame in a small UI block
        self.frame = tk.Frame(parent_canvas, bd=1, relief=tk.GROOVE, bg="#ddd")
        self._build_subframe()
        self.place_in_hex()

    def _build_subframe(self):
        wlen = int(self.config["widgetLength"])

        lbl_title = tk.Label(self.frame, text=self.stepName, font=("Arial",9,"bold"), bg="#ddd")
        lbl_title.pack(anchor="w", pady=2)

        # row1 => offset slider
        row1 = tk.Frame(self.frame, bg="#ddd")
        row1.pack(anchor="w", pady=2)
        tk.Label(row1, text="Off:", font=("Arial",8), bg="#ddd").pack(side=tk.LEFT, padx=1)
        offset_slider = tk.Scale(
            row1, from_=-0.1, to=0.1, resolution=0.01,
            orient=tk.HORIZONTAL, length=wlen,
            variable=self.offsetVar,
            command=lambda v: self.on_change_callback(),
            bg="#ddd", highlightthickness=0
        )
        offset_slider.pack(side=tk.LEFT, padx=2)

        # row2 => expansions check + slider
        row2 = tk.Frame(self.frame, bg="#ddd")
        row2.pack(anchor="w", pady=2)

        cb_exp = tk.Checkbutton(
            row2, text="Exp?", variable=self.expansionsOnVar,
            command=self.on_change_callback,
            bg="#ddd", font=("Arial",8)
        )
        cb_exp.pack(side=tk.LEFT, padx=2)

        exp_slider = tk.Scale(
            row2, from_=0.0, to=1.0, resolution=0.01,
            orient=tk.HORIZONTAL, length=wlen,
            variable=self.expansionsVal,
            command=lambda v: self.on_change_callback(),
            bg="#ddd", highlightthickness=0
        )
        exp_slider.pack(side=tk.LEFT, padx=2)

        # row3 => cycle check + freq slider
        row3 = tk.Frame(self.frame, bg="#ddd")
        row3.pack(anchor="w", pady=2)

        cb_cycle = tk.Checkbutton(
            row3, text="Cyc?", variable=self.cycleVar,
            command=self.on_change_callback,
            bg="#ddd", font=("Arial",8)
        )
        cb_cycle.pack(side=tk.LEFT, padx=2)

        tk.Label(row3, text="F:", font=("Arial",8), bg="#ddd").pack(side=tk.LEFT)
        freq_slider = tk.Scale(
            row3, from_=0.0, to=0.2, resolution=0.01,
            orient=tk.HORIZONTAL, length=wlen,
            variable=self.freqVar,
            command=lambda v: self.on_change_callback(),
            bg="#ddd", highlightthickness=0
        )
        freq_slider.pack(side=tk.LEFT, padx=2)

        # row4 => amplitude
        row4 = tk.Frame(self.frame, bg="#ddd")
        row4.pack(anchor="w", pady=2)
        tk.Label(row4, text="A:", font=("Arial",8), bg="#ddd").pack(side=tk.LEFT)
        amp_slider = tk.Scale(
            row4, from_=0.005, to=0.33, resolution=0.005,
            orient=tk.HORIZONTAL, length=wlen,
            variable=self.amplitudeVar,
            command=lambda v: self.on_change_callback(),
            bg="#ddd", highlightthickness=0
        )
        amp_slider.pack(side=tk.LEFT, padx=2)

    def place_in_hex(self):
        """Position the sub-frame in an isometric ring around centerX, centerY."""
        cX = self.config["centerX"]
        cY = self.config["centerY"]
        radius = self.config["ringRadius"] * self.config["frameScale"]
        isoFactor = self.config["verticalSkew"]

        angle = (2*math.pi/6)*self.index - math.pi/2
        x = cX + radius*math.cos(angle)
        y = cY + radius*math.sin(angle)* isoFactor

        self.canvas.delete(str(id(self.frame)))
        self.canvas.create_window(
            x, y, window=self.frame, anchor="center",
            tags=str(id(self.frame))
        )

    def compute_offset(self, elapsed, maxCyc):
        """If cycle is on, we add a small sinusoidal offset to the base offset."""
        if self.cycleVar.get():
            freq = self.freqVar.get()
            amp = self.amplitudeVar.get()
            cyc = amp * math.sin(2*math.pi * freq * elapsed)
            base_off = self.offsetVar.get()
            raw_off = base_off + cyc
            lo = base_off - maxCyc
            hi = base_off + maxCyc
            if raw_off < lo: raw_off = lo
            if raw_off > hi: raw_off = hi
            return raw_off
        return self.offsetVar.get()

    def expansions_value(self):
        """If expansions are toggled on, return expansionsVal, else 0.0"""
        if self.expansionsOnVar.get():
            return self.expansionsVal.get()
        return 0.0


###############################################################################
class HexStepsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hex Steps UI w/ Expansions + Start/Stop + Debug Popup + Bordered Subsections")

        self.start_time = time.time()

        # We'll store logs in memory; show them in a separate popup
        self.log_buffer = []
        self.synergy_items_cached = []
        self.last_synergy_data = {}

        # user can toggle expansions/cycles for all steps using start/stop
        self.global_run = True

        # final defaults
        self.config = {
            "centerX": 408,  # new final center X
            "centerY": 345,
            "ringRadius": 233,
            "frameScale": 1.3,
            "maxCyc": 0.05,
            "widgetLength": 150,
            "verticalSkew": 0.7
        }

        self._build_layout()
        self._build_nodes()

        self.update_cycle()

    def _build_layout(self):
        # main horizontal PanedWindow
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        ########### left synergy area => synergy table + bar chart
        self.left_frame = tk.LabelFrame(self.main_pane, text="Synergy (Left)", bd=2, relief=tk.RAISED)
        self.main_pane.add(self.left_frame, width=480, minsize=460)

        # synergy top => synergy table
        synergy_top = tk.LabelFrame(self.left_frame, text="Synergy Table", bd=2, relief=tk.RIDGE)
        synergy_top.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=10, pady=10)

        self.synergy_table = ttk.Treeview(
            synergy_top, columns=("val",),
            show="tree headings", height=8
        )
        self.synergy_table.heading("#0", text="Step")
        self.synergy_table.column("#0", width=120, stretch=False)
        self.synergy_table.heading("val", text="Synergy")
        self.synergy_table.column("val", width=80, anchor="center", stretch=False)
        self.synergy_table.pack(fill=tk.X, expand=False)

        # synergy bottom => bar chart
        synergy_bottom = tk.LabelFrame(self.left_frame, text="Bar Chart", bd=2, relief=tk.RIDGE)
        synergy_bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.bar_canvas = tk.Canvas(synergy_bottom, bg="white")
        self.bar_canvas.pack(fill=tk.BOTH, expand=True)
        self.bar_canvas.bind("<Configure>", self._on_bar_canvas_resize)

        # bottom => seed, toggles, start/stop
        bottom_tools = tk.LabelFrame(self.left_frame, text="Tools", bd=2, relief=tk.RAISED)
        bottom_tools.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # top row => seed slider, node/update, config
        row1 = tk.Frame(bottom_tools)
        row1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(row1, text="Seed:", font=("Arial",9,"bold")).pack(side=tk.LEFT, padx=5)
        self.seed_value = tk.DoubleVar(value=0.5)
        def on_seed(val):
            self.on_controls_changed()
        seed_slider = tk.Scale(
            row1, from_=0.0, to=1.0, resolution=0.01,
            orient=tk.HORIZONTAL, length=120,
            variable=self.seed_value,
            command=on_seed
        )
        seed_slider.pack(side=tk.LEFT, padx=5)

        mgmt_frame = tk.Frame(row1)
        mgmt_frame.pack(side=tk.LEFT, padx=5)

        node_btn = tk.Button(mgmt_frame, text="node.py", command=self.run_node_script)
        node_btn.pack(side=tk.TOP, pady=2, fill=tk.X)
        upd_btn = tk.Button(mgmt_frame, text="update.py", command=self.run_update_script)
        upd_btn.pack(side=tk.TOP, pady=2, fill=tk.X)

        config_btn = tk.Button(row1, text="Hex Config", command=self.open_config_popup)
        config_btn.pack(side=tk.LEFT, padx=5)

        # row2 => toggles + start/stop + show debug
        row2 = tk.Frame(bottom_tools)
        row2.pack(side=tk.TOP, fill=tk.X, pady=3)

        self.all_expansions_var = tk.BooleanVar(value=False)
        expansions_cb = tk.Checkbutton(
            row2, text="All Expansions",
            variable=self.all_expansions_var,
            command=self.toggle_all_expansions
        )
        expansions_cb.pack(side=tk.LEFT, padx=5)

        self.all_cycles_var = tk.BooleanVar(value=False)
        cycles_cb = tk.Checkbutton(
            row2, text="All Cycles",
            variable=self.all_cycles_var,
            command=self.toggle_all_cycles
        )
        cycles_cb.pack(side=tk.LEFT, padx=5)

        self.startstop_btn = tk.Button(row2, text="Stop", command=self.handle_startstop)
        self.startstop_btn.pack(side=tk.LEFT, padx=10)

        dbg_btn = tk.Button(row2, text="Show Debug", command=self.show_debug_popup)
        dbg_btn.pack(side=tk.LEFT, padx=10)

        ########### right => synergy lines
        right_frame = tk.LabelFrame(self.main_pane, text="Synergy Lines (Right)", bd=2, relief=tk.RAISED)
        self.main_pane.add(right_frame, stretch="always")

        self.hex_canvas = tk.Canvas(right_frame, bg="#fafafa")
        self.hex_canvas.pack(fill=tk.BOTH, expand=True)

    def _build_nodes(self):
        self.step_nodes = []
        for i, sname in enumerate(STEP_NAMES):
            node = StepNodeUI(
                parent_canvas=self.hex_canvas,
                stepName=sname,
                index=i,
                config=self.config,
                on_change_callback=self.on_controls_changed
            )
            self.step_nodes.append(node)

    ###########################################################################
    # toggles
    ###########################################################################
    def toggle_all_expansions(self):
        new_val = self.all_expansions_var.get()
        for node in self.step_nodes:
            node.expansionsOnVar.set(new_val)
        self.on_controls_changed()

    def toggle_all_cycles(self):
        new_val = self.all_cycles_var.get()
        for node in self.step_nodes:
            node.cycleVar.set(new_val)
        self.on_controls_changed()

    ###########################################################################
    # START/STOP => override expansions+cycles
    ###########################################################################
    def handle_startstop(self):
        if self.global_run:
            # currently "running" => user pressed => STOP => expansions/cycles off
            self.global_run = False
            self.startstop_btn.config(text="Start")
            for node in self.step_nodes:
                node.expansionsOnVar.set(False)
                node.cycleVar.set(False)
            self.all_expansions_var.set(False)
            self.all_cycles_var.set(False)
        else:
            # not running => user pressed => START => expansions/cycles on
            self.global_run = True
            self.startstop_btn.config(text="Stop")
            for node in self.step_nodes:
                node.expansionsOnVar.set(True)
                node.cycleVar.set(True)
            self.all_expansions_var.set(True)
            self.all_cycles_var.set(True)

        self.on_controls_changed()

    ###########################################################################
    # synergy cycle => offset updates
    ###########################################################################
    def update_cycle(self):
        elapsed = time.time() - self.start_time
        maxCyc = self.config["maxCyc"]
        for node in self.step_nodes:
            cyc_off = node.compute_offset(elapsed, maxCyc)
            node.offsetVar.set(cyc_off)

        self.on_controls_changed()
        self.root.after(100, self.update_cycle)

    ###########################################################################
    # synergy & bar chart
    ###########################################################################
    def on_controls_changed(self):
        synergy_input = []
        for node in self.step_nodes:
            synergy_input.append({
                'stepName': node.stepName,
                'offset': node.offsetVar.get(),
                'expansions': node.expansions_value()
            })
        seed = float(self.seed_value.get())

        results = synergy_engine.run_feedback_loop(synergy_input, seed)
        if not isinstance(results, dict):
            results = {}

        self.last_synergy_data = results
        synergy_items = sorted(results.items(), key=lambda x:x[0])
        self.synergy_items_cached = synergy_items

        self._update_synergy_table()
        self._update_bar_chart()
        self._draw_synergy_connections()

    def _update_synergy_table(self):
        """Refresh synergy table from synergy_items_cached."""
        synergy_items = self.synergy_items_cached
        # clear old rows
        for item in self.synergy_table.get_children():
            self.synergy_table.delete(item)
        # re-insert sorted
        for step_name,val in synergy_items:
            vs = f"{val:.3f}"
            self.synergy_table.insert("", "end", text=step_name, values=(vs,))

    def _on_bar_canvas_resize(self, event):
        self._update_bar_chart()

    def _update_bar_chart(self):
        self.bar_canvas.delete("all")
        synergy_items = self.synergy_items_cached
        if not synergy_items:
            self.bar_canvas.create_text(80,40,text="No synergy data", fill="black")
            return

        cW = self.bar_canvas.winfo_width()
        top_m=30
        bar_h=20
        gap=8
        max_w=240

        needed_width = max_w + 80
        if cW> needed_width:
            left_m = (cW-needed_width)/2
        else:
            left_m = 10

        y=top_m
        for step_name,val in synergy_items:
            val = max(0, min(1, val))
            bar_width= val*max_w
            color="#1E90FF"
            if val>0.6:
                color="#FF6347"
            elif val<0.3:
                color="#ADFF2F"

            self.bar_canvas.create_rectangle(left_m, y, left_m+bar_width, y+bar_h, fill=color)
            text_x= left_m+bar_width+10
            text_y= y+bar_h/2
            self.bar_canvas.create_text(text_x, text_y, text=f"{val:.3f}", anchor='w')
            self.bar_canvas.create_text(left_m-10, y+bar_h/2, text=step_name, anchor='e')
            y+= bar_h+gap

    ###########################################################################
    # synergy lines on right
    ###########################################################################
    def _draw_synergy_connections(self):
        self.hex_canvas.delete("synergy")
        synergy_items = self.synergy_items_cached
        if not synergy_items:
            return

        cx = self.config["centerX"]
        cy = self.config["centerY"]
        baseR = self.config["ringRadius"]
        isoFactor = self.config["verticalSkew"]

        points = []
        for i, (step_name, val) in enumerate(synergy_items):
            val = max(0, min(1, val))
            angle = (2*math.pi/6)*i - math.pi/2
            synergy_r = baseR*(0.5 + 0.5*val)
            px = cx + synergy_r*math.cos(angle)
            py = cy + synergy_r*math.sin(angle)* isoFactor

            color="#1E90FF"
            if val>0.6:
                color="#FF6347"
            elif val<0.3:
                color="#ADFF2F"
            thickness= 1 + val*3

            self.hex_canvas.create_line(cx, cy, px, py,
                                        fill=color, width=thickness, tags="synergy")
            points.append((px,py))

        # synergy polygon
        poly_coords=[]
        for (x,y) in points:
            poly_coords.append(x)
            poly_coords.append(y)
        self.hex_canvas.create_polygon(
            *poly_coords,
            fill="#999999", outline="#555555",
            width=2, stipple="gray25",
            tags="synergy"
        )

    ###########################################################################
    # node.py / update.py => store logs in memory, show them in debug popup
    ###########################################################################
    def run_node_script(self):
        cmd=["python","node.py"]
        out=subprocess.run(cmd, capture_output=True, text=True)
        if out.stdout:
            self.log_buffer.append(out.stdout)
        if out.stderr:
            self.log_buffer.append("[ERROR] "+out.stderr)

    def run_update_script(self):
        cmd=["python","update.py"]
        out=subprocess.run(cmd, capture_output=True, text=True)
        if out.stdout:
            self.log_buffer.append(out.stdout)
        if out.stderr:
            self.log_buffer.append("[ERROR] "+out.stderr)

    def show_debug_popup(self):
        pop = tk.Toplevel(self.root)
        pop.title("Debug Log")
        txt = scrolledtext.ScrolledText(pop, wrap=tk.WORD, width=80, height=20)
        txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for line in self.log_buffer:
            txt.insert(tk.END, line + "\n")
        txt.configure(state="disabled")

    ###########################################################################
    # hex config popup
    ###########################################################################
    def open_config_popup(self):
        pop = tk.Toplevel(self.root)
        pop.title("Hex Config with Bordered Layout")

        ring_lab = tk.LabelFrame(pop, text="Ring Radius", bd=2, relief=tk.GROOVE)
        ring_lab.pack(fill=tk.X, padx=5, pady=5)
        ring_var = tk.DoubleVar(value=self.config["ringRadius"])
        ring_sld = tk.Scale(
            ring_lab, from_=80, to=300, resolution=1,
            orient=tk.HORIZONTAL, length=250,
            variable=ring_var,
            command=lambda val: self._on_hex_config_changed("ringRadius", float(val))
        )
        ring_sld.pack(padx=5, pady=5)

        cx_lab = tk.LabelFrame(pop, text="Center X", bd=2, relief=tk.GROOVE)
        cx_lab.pack(fill=tk.X, padx=5, pady=5)
        cx_var = tk.DoubleVar(value=self.config["centerX"])
        cx_sld = tk.Scale(
            cx_lab, from_=50, to=800, resolution=1,
            orient=tk.HORIZONTAL, length=250,
            variable=cx_var,
            command=lambda val: self._on_hex_config_changed("centerX", float(val))
        )
        cx_sld.pack(padx=5, pady=5)

        cy_lab = tk.LabelFrame(pop, text="Center Y", bd=2, relief=tk.GROOVE)
        cy_lab.pack(fill=tk.X, padx=5, pady=5)
        cy_var = tk.DoubleVar(value=self.config["centerY"])
        cy_sld = tk.Scale(
            cy_lab, from_=50, to=600, resolution=1,
            orient=tk.HORIZONTAL, length=250,
            variable=cy_var,
            command=lambda val: self._on_hex_config_changed("centerY", float(val))
        )
        cy_sld.pack(padx=5, pady=5)

        maxCyc_lab = tk.LabelFrame(pop, text="Max Cyc Offset", bd=2, relief=tk.GROOVE)
        maxCyc_lab.pack(fill=tk.X, padx=5, pady=5)
        maxCyc_var = tk.DoubleVar(value=self.config["maxCyc"])
        maxCyc_sld = tk.Scale(
            maxCyc_lab, from_=0.0, to=0.01, resolution=0.0001,
            orient=tk.HORIZONTAL, length=250,
            variable=maxCyc_var,
            command=lambda val: self._on_hex_config_changed("maxCyc", float(val))
        )
        maxCyc_sld.pack(padx=5, pady=5)

        fs_lab = tk.LabelFrame(pop, text="Frame Scale", bd=2, relief=tk.GROOVE)
        fs_lab.pack(fill=tk.X, padx=5, pady=5)
        fs_var = tk.DoubleVar(value=self.config["frameScale"])
        fs_sld = tk.Scale(
            fs_lab, from_=0.5, to=2.0, resolution=0.05,
            orient=tk.HORIZONTAL, length=250,
            variable=fs_var,
            command=lambda val: self._on_hex_config_changed("frameScale", float(val))
        )
        fs_sld.pack(padx=5, pady=5)

        wl_lab = tk.LabelFrame(pop, text="Widget Length", bd=2, relief=tk.GROOVE)
        wl_lab.pack(fill=tk.X, padx=5, pady=5)
        wl_var = tk.DoubleVar(value=self.config["widgetLength"])
        wl_sld = tk.Scale(
            wl_lab, from_=40, to=200, resolution=5,
            orient=tk.HORIZONTAL, length=250,
            variable=wl_var,
            command=lambda val: self._on_hex_config_changed("widgetLength", float(val))
        )
        wl_sld.pack(padx=5, pady=5)

        vs_lab = tk.LabelFrame(pop, text="Vertical Skew", bd=2, relief=tk.GROOVE)
        vs_lab.pack(fill=tk.X, padx=5, pady=5)
        vs_var = tk.DoubleVar(value=self.config["verticalSkew"])
        vs_sld = tk.Scale(
            vs_lab, from_=0.3, to=1.0, resolution=0.05,
            orient=tk.HORIZONTAL, length=250,
            variable=vs_var,
            command=lambda val: self._on_hex_config_changed("verticalSkew", float(val))
        )
        vs_sld.pack(padx=5, pady=5)

    def _on_hex_config_changed(self, key, val):
        self.config[key] = val
        for node in self.step_nodes:
            if key=="widgetLength":
                node.frame.destroy()
                node.frame = tk.Frame(self.hex_canvas, bd=1, relief=tk.GROOVE, bg="#ddd")
                node._build_subframe()
            node.place_in_hex()
        self.on_controls_changed()

def main():
    root = tk.Tk()
    root.geometry("1300x700")
    app = HexStepsApp(root)
    root.mainloop()

if __name__=="__main__":
    main()
