import os
import math
import yaml
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

###############################################################################
# STUBS: Utility & Synergy Functions
###############################################################################
def load_yaml_file(file_path):
    """Load a YAML file, raises FileNotFoundError if missing."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def normalize_value(value, min_range=-1, max_range=1):
    return max(min(value, max_range), min_range)

def calculate_fluctuation(degree):
    return math.sin(2 * math.pi * degree)

def extract_polarity_energy_rhythm(yaml_data):
    """
    Given a loaded YAML dictionary, tries to find 'dynamic_attributes' 
    and from there read subfields for 'polarity', 'energy', 'rhythm'.
    If not found, returns None or an empty dict.
    """
    if not isinstance(yaml_data, dict):
        return {}

    dyn_attrs = yaml_data.get("dynamic_attributes", {})
    if not isinstance(dyn_attrs, dict):
        return {}

    # Attempt to pull out each attribute
    result = {}

    # 1. Polarity
    pol = dyn_attrs.get("polarity", {})
    if isinstance(pol, dict):
        # Grab relevant subfields if they exist
        axis = pol.get("axis", "no axis")
        default_state = pol.get("default_state", "no default_state")
        result["polarity"] = {
            "axis": axis,
            "default_state": default_state,
        }

    # 2. Energy
    energy = dyn_attrs.get("energy", {})
    if isinstance(energy, dict):
        # Could be creative/feminine, etc.
        creative_val = energy.get("creative", None)
        receptive_val = energy.get("receptive", None)
        result["energy"] = {
            "creative": creative_val,
            "receptive": receptive_val
        }

    # 3. Rhythm
    rhythm = dyn_attrs.get("rhythm", {})
    if isinstance(rhythm, dict):
        cycle = rhythm.get("cycle", "no cycle")
        result["rhythm"] = {
            "cycle": cycle
        }

    return result

def process_dynamic_combination(
    foundation_data, foundation_dyn_data,
    application_data, application_tune_data,
    implementation_data,
    execution_data,
    design_data, design_language_data,
    seed_val
):
    """
    Synergy function that:
      1) enumerates top-level keys, 
      2) extracts 'polarity', 'energy', 'rhythm' from each file's dynamic_attributes
    """

    # Helper function extracts top-level keys:
    def top_level_keys(d):
        return list(d.keys()) if isinstance(d, dict) else ["No Data"]

    # Extract the top-level keys from each
    synergy_result = {
        "foundation_keys": top_level_keys(foundation_data),
        "foundation_dyn_keys": top_level_keys(foundation_dyn_data),
        "application_keys": top_level_keys(application_data),
        "application_tune_keys": top_level_keys(application_tune_data),
        "implementation_keys": top_level_keys(implementation_data),
        "execution_keys": top_level_keys(execution_data),
        "design_keys": top_level_keys(design_data),
        "design_language_keys": top_level_keys(design_language_data),
        "seed_used": seed_val
    }

    # Now extract polarity, energy, rhythm from each file
    # We'll store them in synergy_result["extracted_attributes"]
    synergy_result["extracted_attributes"] = {}

    synergy_result["extracted_attributes"]["foundation"] = extract_polarity_energy_rhythm(foundation_data)
    synergy_result["extracted_attributes"]["foundation_dyn"] = extract_polarity_energy_rhythm(foundation_dyn_data)
    synergy_result["extracted_attributes"]["application"] = extract_polarity_energy_rhythm(application_data)
    synergy_result["extracted_attributes"]["application_tune"] = extract_polarity_energy_rhythm(application_tune_data)
    synergy_result["extracted_attributes"]["implementation"] = extract_polarity_energy_rhythm(implementation_data)
    synergy_result["extracted_attributes"]["execution"] = extract_polarity_energy_rhythm(execution_data)
    synergy_result["extracted_attributes"]["design"] = extract_polarity_energy_rhythm(design_data)
    synergy_result["extracted_attributes"]["design_language"] = extract_polarity_energy_rhythm(design_language_data)

    return synergy_result

###############################################################################
# Main Application
###############################################################################

class FiveStepsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic 5 Steps Module with Polarity/Energy/Rhythm Extraction")
        self.root.geometry("900x800")

        # We'll keep track of last-used file paths for each step & sub-step
        self.last_paths = {
            "foundation": r".\foundation\laws\default.law",
            "foundation_dyn": r".\foundation\dynamics\default.dyn",
            "application": r".\application\resoforms\default.reso",
            "application_tune": r".\application\tuning\default.tune",
            "implementation": r".\implementation\rules\default.rule",
            "execution": r".\execution\styles\default.style",
            "design": r".\design\sheets\default.sheet",
            "design_lang": r".\design\designs\default.design"
        }

        # Step variables
        self.foundation_file = tk.StringVar(value="")
        self.foundation_dyn_file = tk.StringVar(value="")
        self.application_file = tk.StringVar(value="")
        self.application_tune_file = tk.StringVar(value="")
        self.implementation_file = tk.StringVar(value="")
        self.execution_file = tk.StringVar(value="")
        self.design_file = tk.StringVar(value="")
        self.design_language_file = tk.StringVar(value="")

        # Data store
        self.found_data = None
        self.found_dyn_data = None
        self.appl_data = None
        self.appl_tune_data = None
        self.impl_data = None
        self.exec_data = None
        self.desg_data = None
        self.desg_lang_data = None

        # The seed, default 0.5
        self.seed_value = tk.DoubleVar(value=0.5)

        self.build_ui()

    def build_ui(self):
        """Build the 5 steps UI plus synergy controls and debug area."""
        steps_frame = tk.Frame(self.root)
        steps_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Step 1: foundation
        self.create_step_ui(steps_frame, "foundation", "Select Foundation File", self.foundation_file)
        self.create_foundation_dyn_ui(steps_frame)

        # Step 2: application
        self.create_step_ui(steps_frame, "application", "Select Application File", self.application_file)
        self.create_application_tune_ui(steps_frame)

        # Step 3: implementation
        self.create_step_ui(steps_frame, "implementation", "Select Implementation File", self.implementation_file)

        # Step 4: execution
        self.create_step_ui(steps_frame, "execution", "Select Execution File", self.execution_file)

        # Step 5: design
        self.create_step_ui(steps_frame, "design", "Select Design File", self.design_file)
        self.create_design_language_ui(steps_frame)

        # synergy controls
        synergy_frame = tk.Frame(self.root)
        synergy_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(synergy_frame, text="Seed Value:").pack(side=tk.LEFT, padx=5)
        tk.Scale(synergy_frame, from_=0, to=1, resolution=0.01,
                 orient=tk.HORIZONTAL, length=300,
                 variable=self.seed_value
                 ).pack(side=tk.LEFT, padx=5)

        tk.Button(synergy_frame, text="Combine", command=self.combine_files, width=15).pack(side=tk.LEFT, padx=10)

        # debug area
        debug_frame = tk.LabelFrame(self.root, text="Debug / Errors Log")
        debug_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.debug_text = scrolledtext.ScrolledText(debug_frame, wrap=tk.WORD, width=90, height=8)
        self.debug_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Initialize defaults
        self.setup_defaults()

    def setup_defaults(self):
        """Check if default files exist in self.last_paths and set them if so."""
        self.debug_print("Checking default files for each step...")

        # For each step in last_paths, if the file exists, set the relevant StringVar
        self.try_set_default("foundation", self.foundation_file)
        self.try_set_default("foundation_dyn", self.foundation_dyn_file)
        self.try_set_default("application", self.application_file)
        self.try_set_default("application_tune", self.application_tune_file)
        self.try_set_default("implementation", self.implementation_file)
        self.try_set_default("execution", self.execution_file)
        self.try_set_default("design", self.design_file)
        self.try_set_default("design_lang", self.design_language_file)

    def try_set_default(self, step_key, var):
        """If last_paths[step_key] physically exists, set var to that path, else log not found."""
        path = self.last_paths[step_key]
        if os.path.isfile(path):
            var.set(path)
            self.debug_print(f"(Init) {step_key} default => {path}")
        else:
            self.debug_print(f"(Init) {step_key} default not found => {path}")

    def create_step_ui(self, parent, step_name, label_text, path_var):
        """Generic label frame for a step with a file path + browse button."""
        lf = tk.LabelFrame(parent, text=step_name.capitalize())
        lf.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(lf, text=label_text).pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(lf, textvariable=path_var, width=50)
        entry.pack(side=tk.LEFT, padx=5)

        btn = tk.Button(lf, text="Browse", command=lambda: self.pick_file(step_name, path_var))
        btn.pack(side=tk.LEFT, padx=5)

    def create_foundation_dyn_ui(self, parent):
        """Inside foundation step, sub-frame for .dyn input."""
        lf = tk.LabelFrame(parent, text="foundation: Dynamic (.dyn)")
        lf.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(lf, text="Select .dyn File").pack(side=tk.LEFT, padx=5)
        dyn_entry = tk.Entry(lf, textvariable=self.foundation_dyn_file, width=50)
        dyn_entry.pack(side=tk.LEFT, padx=5)

        dyn_btn = tk.Button(lf, text="Browse", command=lambda: self.pick_file("foundation_dyn", self.foundation_dyn_file))
        dyn_btn.pack(side=tk.LEFT, padx=5)

    def create_application_tune_ui(self, parent):
        """Inside application step, sub-frame for .tune input."""
        lf = tk.LabelFrame(parent, text="application: Tuning (.tune)")
        lf.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(lf, text="Select .tune File").pack(side=tk.LEFT, padx=5)
        tune_entry = tk.Entry(lf, textvariable=self.application_tune_file, width=50)
        tune_entry.pack(side=tk.LEFT, padx=5)

        tune_btn = tk.Button(lf, text="Browse", command=lambda: self.pick_file("application_tune", self.application_tune_file))
        tune_btn.pack(side=tk.LEFT, padx=5)

    def create_design_language_ui(self, parent):
        """In design step, a sub-frame for an additional .design language file."""
        lf = tk.LabelFrame(parent, text="design: Language (.design)")
        lf.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(lf, text="Select .design Language File").pack(side=tk.LEFT, padx=5)
        lang_entry = tk.Entry(lf, textvariable=self.design_language_file, width=50)
        lang_entry.pack(side=tk.LEFT, padx=5)

        lang_btn = tk.Button(lf, text="Browse", command=lambda: self.pick_file("design_lang", self.design_language_file))
        lang_btn.pack(side=tk.LEFT, padx=5)

    def pick_file(self, step_name, path_var):
        """User picks a file from file dialog, store in path_var + self.last_paths[step_name]."""
        file_path = filedialog.askopenfilename()
        if file_path:
            path_var.set(file_path)
            self.last_paths[step_name] = file_path
            self.debug_print(f"{step_name} => {file_path}")

    def combine_files(self):
        """Load each step's file + .dyn + .tune + design language => synergy, printing to debug + synergy window."""
        self.debug_print("\n=== Combining Files ===")

        try:
            # foundation
            self.found_data = self.load_step_file("foundation", self.foundation_file.get())
            self.debug_print(f"foundation => {self.foundation_file.get()}")

            # foundation .dyn
            if self.foundation_dyn_file.get():
                self.found_dyn_data = self.load_step_file("foundation_dyn", self.foundation_dyn_file.get())
                self.debug_print(f"foundation_dyn => {self.foundation_dyn_file.get()}")
            else:
                raise ValueError("No .dyn file selected in foundation step for dynamic attributes.")

            # application
            self.appl_data = self.load_step_file("application", self.application_file.get())
            self.debug_print(f"application => {self.application_file.get()}")

            # application tune
            if self.application_tune_file.get():
                self.appl_tune_data = self.load_step_file("application_tune", self.application_tune_file.get())
                self.debug_print(f"application_tune => {self.application_tune_file.get()}")
            else:
                raise ValueError("No .tune file selected in application step for tuning attributes.")

            # implementation
            self.impl_data = self.load_step_file("implementation", self.implementation_file.get())
            self.debug_print(f"implementation => {self.implementation_file.get()}")

            # execution
            self.exec_data = self.load_step_file("execution", self.execution_file.get())
            self.debug_print(f"execution => {self.execution_file.get()}")

            # design
            self.desg_data = self.load_step_file("design", self.design_file.get())
            self.debug_print(f"design => {self.design_file.get()}")

            # design language .design
            if self.design_language_file.get():
                self.desg_lang_data = self.load_step_file("design_lang", self.design_language_file.get())
                self.debug_print(f"design_lang => {self.design_language_file.get()}")
            else:
                raise ValueError("No design-language file (.design) selected in design step for language.")

            final_seed = float(self.seed_value.get())
            synergy_data = process_dynamic_combination(
                foundation_data=self.found_data,
                foundation_dyn_data=self.found_dyn_data,
                application_data=self.appl_data,
                application_tune_data=self.appl_tune_data,
                implementation_data=self.impl_data,
                execution_data=self.exec_data,
                design_data=self.desg_data,
                design_language_data=self.desg_lang_data,
                seed_val=final_seed
            )

            self.show_synergy_result(synergy_data)
        except Exception as e:
            self.debug_print(f"ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))

    def load_step_file(self, step_name, path):
        """If no path, return {}, else load YAML. We'll print a small debug statement as well."""
        if not path:
            self.debug_print(f"{step_name} => no path given, returning empty dict.")
            return {}
        data = load_yaml_file(path)
        if data is None:
            data = {}
        self.debug_print(f"{step_name} => loaded keys: {list(data.keys()) if isinstance(data, dict) else 'No keys'}")
        return data

    def show_synergy_result(self, synergy_data):
        """Display synergy data in a new Toplevel with scrolled text, also log to debug_text."""
        top = tk.Toplevel(self.root)
        top.title("Synergy Result")
        top.geometry("600x400")

        text_area = scrolledtext.ScrolledText(top, wrap=tk.WORD)
        text_area.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Dump synergy_data as YAML
        text_area.insert(tk.END, yaml.dump(synergy_data, sort_keys=False))
        text_area.configure(state=tk.DISABLED)

        self.debug_print(f"Synergy: {synergy_data}")

    def debug_print(self, msg):
        """Append a message to the debug_text area, easy to see + copy errors or logs."""
        if hasattr(self, "debug_text"):
            self.debug_text.insert(tk.END, msg + "\n")
            self.debug_text.see(tk.END)
        else:
            print(msg)

def main():
    root = tk.Tk()
    app = FiveStepsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
