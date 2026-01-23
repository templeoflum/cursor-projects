import os
import yaml
import math
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# Load YAML file
def load_yaml_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

# Normalize a value within a range
def normalize_value(value, min_range=-1, max_range=1):
    return max(min(value, max_range), min_range)

# Calculate harmonic fluctuation
def calculate_fluctuation(degree):
    return math.sin(2 * math.pi * degree)

# Resolve unified or specific seed
def resolve_seed(dynamic_attributes, law_data, dyn_data):
    """
    Resolve the effective seed for dynamic attributes.
    Priority: Unified seed from .dyn > Specific seed in .law or attributes.
    """
    unified_seed = dyn_data.get("seed", None)
    use_unified_seed = dyn_data.get("use_unified_seed", False)

    print(f"Unified Seed: {unified_seed}, use_unified_seed: {use_unified_seed}")  # Debug output

    if use_unified_seed and unified_seed is not None:
        return unified_seed, "Inherited from Unified Seed"

    specific_seed = dynamic_attributes.get("seed", law_data.get("seed", 0.35))
    return specific_seed, "Explicitly Defined"

# Process dynamic attributes
def process_dynamic_combination(law_data, file_data, dyn_data, fluctuation_factor=1.2):
    if not (law_data and file_data and dyn_data):
        raise ValueError("All inputs (law, file, dyn) must be valid.")

    dynamic_defaults = dyn_data.get("attributes", {})
    dynamic_attributes = file_data.get("dynamic_attributes", {})

    # Merge defaults with file attributes
    for key, value in dynamic_defaults.items():
        dynamic_attributes.setdefault(key, value)

    # Resolve unified seed
    effective_seed, seed_source = resolve_seed(dynamic_attributes, law_data, dyn_data)
    dynamic_attributes["seed"] = effective_seed  # Ensure unified seed is displayed in output
    dynamic_attributes["seed_source"] = seed_source  # Debugging source

    print(f"Effective Unified Seed: {effective_seed} ({seed_source})")  # Debugging output

    # Calculate tuned values for attributes
    for attr, attr_data in dynamic_attributes.items():
        if isinstance(attr_data, dict) and "fluctuation_range" in attr_data:
            range_min, range_max = map(float, attr_data["fluctuation_range"].split(" to "))
            offset_min, offset_max = map(float, attr_data.get("offset_range", "0 to 0").split(" to "))

            # Calculate fluctuation and offset
            fluctuation = calculate_fluctuation(effective_seed) * fluctuation_factor
            offset = (offset_max - offset_min) * fluctuation + (offset_min + offset_max) / 2

            # Calculate final value
            modulated_value = (fluctuation * (range_max - range_min) / 2) + ((range_min + range_max) / 2) + offset
            final_value = normalize_value(modulated_value, range_min, range_max)

            attr_data["tuned_value"] = round(final_value, 4)  # Store tuned value
            print(f"Tuned '{attr}' to {attr_data['tuned_value']}")  # Debug output

    # Resolve rhythm phase and cycle explicitly
    cycle = dynamic_attributes.get("rhythm", {}).get("cycle", "Undefined")
    phase_data = dynamic_attributes.get("rhythm", {}).get("phase", {})
    degree = effective_seed  # Directly tie degree to the effective seed
    phases = phase_data.get("phases", ["growth", "peak", "decline", "reset"])
    current_phase = phases[int(degree * len(phases)) % len(phases)] if phases else "Undefined"

    dynamic_attributes["rhythm"]["phase"] = {
        "current": current_phase,
        "degree": round(degree, 4),
        "phases": phases,
        "seed": effective_seed,  # Use the effective seed for tracking
    }

    print(f"Cycle: {cycle}, Phase: {current_phase}, Degree: {degree}, Seed: {effective_seed}")

    # Resolve energy
    creative_energy = dynamic_attributes.get("energy", {}).get("creative", 0.5)
    receptive_energy = dynamic_attributes.get("energy", {}).get("receptive", 0.5)
    dynamic_attributes["energy"]["balanced"] = round((creative_energy + receptive_energy) / 2, 4)

    return dynamic_attributes

# Display results in a new window
def display_results(output_data):
    result_window = tk.Toplevel(root)
    result_window.title("Combined Results")
    result_window.geometry("800x600")

    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=90, height=35)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    text_area.insert(tk.END, yaml.dump(output_data, sort_keys=False))
    text_area.configure(state="disabled")

# Update dynamic attributes and refresh results
def update_and_display_results(seed_value):
    try:
        law_data = load_yaml_file(law_file_path.get())
        dyn_data = load_yaml_file(dyn_file_path.get())
        file_data = load_yaml_file(dynamic_file_path.get())

        # Update the seed in dyn_data dynamically
        dyn_data["seed"] = seed_value

        combined_data = process_dynamic_combination(law_data, file_data, dyn_data)
        return combined_data  # Return combined data for display
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

# Select and process files
def combine_files():
    try:
        seed_value = float(seed_slider.get())
        combined_data = update_and_display_results(seed_value)
        if combined_data:
            display_results(combined_data)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Initialize UI
root = tk.Tk()
root.title("Dynamic Combiner Module")
script_dir = os.path.dirname(os.path.abspath(__file__))

law_file_path = tk.StringVar(value=os.path.join(script_dir, "laws/default.law"))
dyn_file_path = tk.StringVar(value=os.path.join(script_dir, "dynamics/default.dyn"))
dynamic_file_path = tk.StringVar(value=os.path.join(script_dir, "resoforms/default.reso"))

tk.Label(root, text="Select .law File").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=law_file_path, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=lambda: law_file_path.set(filedialog.askopenfilename())).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Select .dyn File").grid(row=1, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=dyn_file_path, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=lambda: dyn_file_path.set(filedialog.askopenfilename())).grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text="Select Dynamic File").grid(row=2, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=dynamic_file_path, width=50).grid(row=2, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=lambda: dynamic_file_path.set(filedialog.askopenfilename())).grid(row=2, column=2, padx=10, pady=10)

# Seed adjustment slider and input box
tk.Label(root, text="Adjust Seed Value").grid(row=3, column=0, padx=10, pady=10)

# Input box for seed value
seed_value_input = tk.Entry(root, width=10)
seed_value_input.insert(0, "0.35")  # Default seed value
seed_value_input.grid(row=3, column=1, padx=10, pady=10)

# Slider for seed adjustment
seed_slider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=400)
seed_slider.set(0.35)  # Default seed value
seed_slider.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Update seed value dynamically
def update_seed_from_input():
    try:
        seed_value = float(seed_value_input.get())
        seed_slider.set(seed_value)  # Sync slider with input box
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid numeric seed value.")

def update_seed_from_slider(val):
    seed_value_input.delete(0, tk.END)
    seed_value_input.insert(0, val)

# Apply seed button
tk.Button(root, text="Apply Seed", command=combine_files).grid(row=3, column=2, padx=10, pady=10)
seed_slider.config(command=update_seed_from_slider)

root.mainloop()
