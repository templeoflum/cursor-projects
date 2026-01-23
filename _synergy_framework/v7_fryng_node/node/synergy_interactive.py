
import os
import yaml
import tkinter as tk
from tkinter import ttk

######################################################################
# CONFIG
######################################################################
EXPANSIONS_DIR = "node/fryng_core/expansions"  # Adjust if needed
REFRESH_INTERVAL_MS = 1500  # How often (ms) we re-aggregate synergy

######################################################################
# 1) YAML LOADING/WRITING + AGGREGATION
######################################################################

def load_yaml(path):
    """Reads a YAML file, returns {} if missing or parse error."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data else {}
    except:
        return {}

def save_yaml(path, data):
    """Writes 'data' as YAML to the given path."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)

def read_synergy():
    """
    Reads expansions from EXPANSIONS_DIR, returning a dict of synergy fields
    like {"potential_energy": 0.6, "potential_coherence": 0.4, ...}.
    We'll parse each .step file as YAML, guess a step key from the filename
    (e.g. "01_Potential.step" => "potential"), then look in data['steps'][step_key]
    and data['dynamic_attributes'] for numeric fields.
    """
    synergy_data = {}
    if not os.path.exists(EXPANSIONS_DIR):
        print(f"[read_synergy] expansions folder not found: {EXPANSIONS_DIR}")
        return synergy_data

    step_files = [fn for fn in os.listdir(EXPANSIONS_DIR) if fn.lower().endswith(".step")]
    if not step_files:
        print("[read_synergy] No .step files found, synergy_data is empty.")
        return synergy_data

    for fn in step_files:
        path = os.path.join(EXPANSIONS_DIR, fn)
        data = load_yaml(path)
        # figure out step_key from filename, e.g. "01_Potential.step" => "potential"
        step_parts = fn.split("_", 1)
        if len(step_parts) < 2:
            step_key = fn.rsplit(".", 1)[0].lower()
        else:
            step_key = step_parts[1].split(".")[0].lower()

        step_info = data.get("steps", {}).get(step_key, {})
        for k, v in step_info.items():
            if isinstance(v, (int, float)):
                synergy_data[f"{step_key}_{k}"] = v

        dyn = data.get("dynamic_attributes", {})
        for k, v in dyn.items():
            if isinstance(v, (int, float)):
                synergy_data[f"{step_key}_{k}"] = v

    return synergy_data

def write_synergy_value(field_key, new_val):
    """
    Writes the updated synergy value back to the expansions file.
    - field_key is something like "potential_energy" or "symmetry_intensity"
    - new_val is a float or int
    We'll parse 'field_key' to identify which expansions file we must edit:
      step_key = the part before '_' (like "potential"), 
      field_name = the part after '_' (like "energy").

    Then we open e.g. "01_Potential.step" if we see "potential" in the filename,
    find data['steps']['potential'][field_name] or data['dynamic_attributes'][field_name],
    and set it.
    """
    # parse the step_key and field_name from field_key
    # e.g. "potential_energy" => step_key="potential", field_name="energy"
    parts = field_key.split("_", 1)
    if len(parts) < 2:
        print(f"[write_synergy_value] Invalid field_key: {field_key}")
        return
    step_key, field_name = parts

    # find expansions file whose name includes e.g. "Potential.step"
    expansions = [fn for fn in os.listdir(EXPANSIONS_DIR) if fn.lower().endswith(".step")]
    match_file = None
    for fn in expansions:
        # "01_Potential.step" => step_parts[1].split(".")[0].lower() => "potential"
        step_parts = fn.split("_", 1)
        if len(step_parts) < 2:
            # fallback
            candidate = fn.rsplit(".",1)[0].lower()
        else:
            candidate = step_parts[1].split(".")[0].lower()

        if candidate == step_key:
            match_file = fn
            break

    if not match_file:
        print(f"[write_synergy_value] No expansions file found for step_key='{step_key}'")
        return

    # load that expansions file as YAML
    full_path = os.path.join(EXPANSIONS_DIR, match_file)
    data = load_yaml(full_path)

    # see if it belongs in data['steps'][step_key] or data['dynamic_attributes']
    # We'll check if field_name is in step info or dynamic_attributes
    step_info = data.setdefault("steps", {}).setdefault(step_key, {})
    dyn = data.setdefault("dynamic_attributes", {})

    # if field_name already in step_info, set that
    # else if it's in dyn, set that
    # otherwise we can guess where to place it
    if field_name in step_info:
        step_info[field_name] = new_val
        print(f"[write_synergy_value] Updated steps.{step_key}.{field_name} to {new_val}")
    elif field_name in dyn:
        dyn[field_name] = new_val
        print(f"[write_synergy_value] Updated dynamic_attributes.{field_name} to {new_val}")
    else:
        # guess: if  'energy' or 'intensity' etc. maybe it belongs in steps
        # or if 'coherence' or 'alignment' maybe belongs in dynamic_attributes
        # We'll just put it in steps for demonstration.
        step_info[field_name] = new_val
        print(f"[write_synergy_value] Created steps.{step_key}.{field_name} = {new_val}")

    save_yaml(full_path, data)
    print(f"[write_synergy_value] saved to: {full_path}")


######################################################################
# 2) A TKINTER UI WITH INTERACTION
######################################################################

class SynergyMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interactive Synergy Visualization")
        self.geometry("450x400")

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

        # schedule the aggregator polling
        self.after(REFRESH_INTERVAL_MS, self.update_synergy_loop)

    def update_synergy_loop(self):
        new_data = read_synergy()
        # new_data might be empty or have numeric fields
        new_keys = set(new_data.keys())
        old_keys = set(self.widget_map.keys())

        # create new UI rows for new synergy fields
        for key in new_keys.difference(old_keys):
            val = new_data[key]
            row_frame = ttk.Frame(self.inner_frame)
            row_frame.pack(fill=tk.X, pady=2)

            label_key = ttk.Label(row_frame, text=f"{key}:")
            label_key.pack(side=tk.LEFT)

            # We'll create a slider if in [0..1], otherwise a text entry
            # But we can also choose to do a slider for bigger ranges
            # For demonstration, let's do a slider if 0 <= val <= 2, else a label
            if 0 <= val <= 2:
                # we'll keep a doublevar for the slider
                var = tk.DoubleVar(value=val)
                slider = ttk.Scale(row_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, variable=var)
                slider.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

                # watch for changes
                def on_slider_change(slider_key=key, var_ref=var):
                    new_val = var_ref.get()
                    # write synergy value back to expansions
                    write_synergy_value(slider_key, new_val)

                # trace the var in real time, or bind slider command:
                def slider_command(event, slider_key=key, var_ref=var):
                    new_val = var_ref.get()
                    write_synergy_value(slider_key, new_val)

                # either approach:
                slider.bind("<ButtonRelease-1>", slider_command)

                self.widget_map[key] = ("slider", var)
            else:
                # create a label that shows the float
                val_lbl = ttk.Label(row_frame, text=f"{val:.2f}")
                val_lbl.pack(side=tk.LEFT, padx=5)
                self.widget_map[key] = ("label", val_lbl)

        # update existing synergy fields
        for key in new_keys.intersection(old_keys):
            val = new_data[key]
            w_type, widget = self.widget_map[key]
            if w_type == "slider":
                # widget is a tk.DoubleVar
                widget.set(val)
            else:
                # it's a label
                widget.config(text=f"{val:.2f}")

        self.synergy_data = new_data

        # schedule next loop
        self.after(REFRESH_INTERVAL_MS, self.update_synergy_loop)


def run_synergy_visual():
    app = SynergyMonitor()
    app.mainloop()

if __name__ == "__main__":
    run_synergy_visual()
