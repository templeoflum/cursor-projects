import tkinter as tk
from tkinter import filedialog, messagebox
import os
import yaml

###############################################################################
# STUBS for External Modules (Replace with real code or remove)
###############################################################################
def load_yaml_file(path):
    """Stub function simulating load_yaml_file from file_management."""
    print(f"DEBUG: Attempting to load file: {path}")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def process_dynamic_combination(layered_files, dyn_data, tune_data):
    """
    Stub function simulating process_dynamic_combination from data_processing.
    Returns a simple dictionary merging file counts for demonstration.
    """
    total_items = sum(len(layer) for layer in layered_files)
    seed_val = dyn_data.get("seed", "No Seed")
    tune_info = list(tune_data.keys()) if isinstance(tune_data, dict) else ["No tune info"]
    return {
        "info": f"Processed {total_items} layered-file items.",
        "dyn_seed_used": seed_val,
        "tune_keys_found": tune_info
    }

###############################################################################
# UI helper stubs (similar to ui_framework)
###############################################################################
def create_label_frame(parent, text):
    frame = tk.LabelFrame(parent, text=text)
    frame.pack(fill=tk.X, padx=5, pady=5)
    print(f"UI debug: Created LabelFrame '{text}'")
    return frame

def create_listbox_with_scrollbar(parent):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.X, padx=5, pady=5)
    listbox = tk.Listbox(frame, height=4)
    listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    print("UI debug: Created Listbox with Scrollbar")
    return listbox

def create_add_file_button(parent, button_text, file_list, listbox):
    """
    Creates a button that, when clicked, opens a file dialog
    and appends the selected file to file_list, displaying in listbox.
    """
    def on_click():
        file_path = filedialog.askopenfilename()
        if file_path and file_path not in file_list:
            file_list.append(file_path)
            listbox.insert(tk.END, os.path.basename(file_path))
            print(f"UI debug: Added {file_path} to {button_text}")
    btn = tk.Button(parent, text=button_text, command=on_click)
    btn.pack(side=tk.LEFT, padx=5)
    print(f"UI debug: Created Button '{button_text}'")

def create_slider(parent, label_text, tk_doublevar):
    """
    Creates a label + slider that updates the given tk.DoubleVar.
    """
    frame = tk.Frame(parent)
    frame.pack(fill=tk.X, padx=5, pady=5)

    label = tk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT, padx=5)

    slider = tk.Scale(frame, from_=0, to=1, resolution=0.01,
                      orient=tk.HORIZONTAL, length=300,
                      variable=tk_doublevar)
    slider.pack(side=tk.LEFT, padx=5)

    print(f"UI debug: Created slider '{label_text}' with default {tk_doublevar.get()}")
    return slider

def create_file_dropdown(parent, label_text, file_list, dropdown_var,
                         file_type_label, file_extension, update_dropdown_func):
    """
    Creates a label + OptionMenu. If file_list is empty, we provide a default string to avoid errors.
    """
    frame = tk.Frame(parent)
    frame.pack(fill=tk.X, padx=5, pady=5)

    label = tk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT, padx=5)

    if len(file_list) == 0:
        default_value = "No files"
        dropdown_menu = tk.OptionMenu(frame, dropdown_var, default_value)
        print(f"UI debug: Created empty OptionMenu for {label_text}")
    else:
        default_value = file_list[0]
        dropdown_menu = tk.OptionMenu(frame, dropdown_var, default_value, *file_list[1:])
        print(f"UI debug: Created OptionMenu for {label_text} with default={default_value}")

    dropdown_menu.config(width=25)
    dropdown_menu.pack(side=tk.LEFT, padx=5)

    return dropdown_menu

###############################################################################
# Directory Setup
###############################################################################
# We'll define 7 defaults: default.law, default.dyn, default.tune, default.reso,
# default.style, default.rule, default.sheet for each layer, stored in subfolders:
# foundation -> default.law, default.sheet
# application -> default.dyn, default.reso
# implementation -> default.rule
# execution -> default.tune
# design -> default.style

layers_directories = {
    "Foundation": os.path.join(os.getcwd(), "foundation"),
    "Application": os.path.join(os.getcwd(), "application"),
    "Implementation": os.path.join(os.getcwd(), "implementation"),
    "Execution": os.path.join(os.getcwd(), "execution"),
    "Design": os.path.join(os.getcwd(), "design"),
}

layer_file_paths = {
    "Foundation": [
        os.path.join(layers_directories["Foundation"], "default.law"),
        os.path.join(layers_directories["Foundation"], "default.sheet")
    ],
    "Application": [
        os.path.join(layers_directories["Application"], "default.dyn"),
        os.path.join(layers_directories["Application"], "default.reso")
    ],
    "Implementation": [
        os.path.join(layers_directories["Implementation"], "default.rule")
    ],
    "Execution": [
        os.path.join(layers_directories["Execution"], "default.tune")
    ],
    "Design": [
        os.path.join(layers_directories["Design"], "default.style")
    ],
}

def initialize_layer_file_paths():
    """
    If the default.* file physically exists in the subfolder, keep it in the list.
    Otherwise, remove it to avoid errors. 
    """
    for layer_name, paths in layer_file_paths.items():
        valid_paths = []
        for fp in paths:
            if os.path.isfile(fp):
                valid_paths.append(fp)
            else:
                print(f"Debug: {fp} not found for layer {layer_name}")
        layer_file_paths[layer_name] = valid_paths

initialize_layer_file_paths()

###############################################################################
# MAIN UI
###############################################################################
root = tk.Tk()
root.title("Dynamic Combiner Module")
root.geometry("800x800")
print("UI debug: Main window created (800x800)")

# The seed the user can adjust, defaulted to 0.5
seed_value = tk.DoubleVar(root, value=0.50)
print(f"UI debug: Default seed_value set to {seed_value.get()}")

# We'll define default placeholders for .dyn and .tune
dyn_files = [os.path.join(layers_directories["Application"], "default.dyn")]
tune_files = [os.path.join(layers_directories["Execution"], "default.tune")]

# If they don't physically exist, remove them
dyn_files = [f for f in dyn_files if os.path.isfile(f)]
tune_files = [f for f in tune_files if os.path.isfile(f)]

# If the lists end up empty, user must pick manually
dyn_dropdown_var = tk.StringVar(value=(os.path.basename(dyn_files[0]) if dyn_files else "No .dyn files"))
tune_dropdown_var = tk.StringVar(value=(os.path.basename(tune_files[0]) if tune_files else "No .tune files"))

def add_file_to_dropdown(file_list, dropdown_var, update_dropdown_func, file_type, file_extension):
    file_path = filedialog.askopenfilename(filetypes=[(file_type, file_extension)])
    if file_path and file_path not in file_list:
        file_list.append(file_path)
        dropdown_var.set(os.path.basename(file_path))
        update_dropdown_func()
        print(f"UI debug: Added {file_path} to {file_type}")

def update_dropdown(menu, file_list, dropdown_var):
    menu.delete(0, "end")
    for f in file_list:
        menu.add_command(
            label=os.path.basename(f),
            command=lambda val=f: dropdown_var.set(val)
        )
    print("UI debug: Updated dropdown with new file list")

def update_dyn_dropdown():
    update_dropdown(dyn_dropdown["menu"], dyn_files, dyn_dropdown_var)

def update_tune_dropdown():
    update_dropdown(tune_dropdown["menu"], tune_files, tune_dropdown_var)

def combine_with_seed():
    """
    Attempts to merge all layered files + .dyn + .tune with the chosen seed.
    """
    try:
        selected_dyn_label = dyn_dropdown_var.get()
        selected_tune_label = tune_dropdown_var.get()

        # Find actual path from our dyn_files or tune_files
        selected_dyn_file = None
        for f in dyn_files:
            if os.path.basename(f) == selected_dyn_label:
                selected_dyn_file = f
                break

        selected_tune_file = None
        for f in tune_files:
            if os.path.basename(f) == selected_tune_label:
                selected_tune_file = f
                break

        if not selected_dyn_file:
            raise ValueError(f"Please select a valid .dyn file. Current label={selected_dyn_label}")
        if not selected_tune_file:
            raise ValueError(f"Please select a valid .tune file. Current label={selected_tune_label}")

        # Load them
        dyn_data = load_yaml_file(selected_dyn_file)
        tune_data = load_yaml_file(selected_tune_file)
        dyn_data["seed"] = seed_value.get()

        loaded_files = {}
        for layer, paths in layer_file_paths.items():
            loaded_files[layer] = []
            for fp in paths:
                if os.path.isfile(fp):
                    loaded_files[layer].append(load_yaml_file(fp))

        combined_data = process_dynamic_combination(
            [loaded_files[layer] for layer in layer_file_paths.keys()],
            dyn_data,
            tune_data
        )
        print("DEBUG: Combined data =>", combined_data)
        messagebox.showinfo("Combination Result", str(combined_data))

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Main frame for layering
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)
print("UI debug: Created main_frame for layered sections")

layer_listboxes = {}

def create_section(frame, layer_name):
    section_frame = create_label_frame(frame, f"{layer_name} Files")
    listbox = create_listbox_with_scrollbar(section_frame)
    layer_listboxes[layer_name] = listbox
    create_add_file_button(section_frame, f"Add {layer_name} File", layer_file_paths[layer_name], listbox)

# Create sections for each layer
for layer_name in layer_file_paths.keys():
    create_section(main_frame, layer_name)

# .dyn/.tune section
dyn_tune_frame = create_label_frame(main_frame, "Dynamic and Tuning File Selection")

dyn_dropdown = create_file_dropdown(
    dyn_tune_frame,
    "Dynamic File Selection",
    dyn_files,
    dyn_dropdown_var,
    "Dynamic File",
    "*.dyn",
    update_dyn_dropdown
)
tk.Button(
    dyn_tune_frame,
    text="Add .dyn File",
    command=lambda: add_file_to_dropdown(
        dyn_files,
        dyn_dropdown_var,
        update_dyn_dropdown,
        "Dynamic File",
        "*.dyn"
    )
).pack(padx=5, pady=5, side=tk.LEFT)

tune_dropdown = create_file_dropdown(
    dyn_tune_frame,
    "Tuning File Selection",
    tune_files,
    tune_dropdown_var,
    "Tuning File",
    "*.tune",
    update_tune_dropdown
)
tk.Button(
    dyn_tune_frame,
    text="Add .tune File",
    command=lambda: add_file_to_dropdown(
        tune_files,
        tune_dropdown_var,
        update_tune_dropdown,
        "Tuning File",
        "*.tune"
    )
).pack(padx=5, pady=5, side=tk.LEFT)

# The seed slider (default=0.5)
create_slider(main_frame, "Adjust Seed Value", seed_value)

# Combine button
tk.Button(main_frame, text="Combine Files", command=combine_with_seed, width=20).pack(pady=20)

print("UI debug: All widgets constructed. Starting mainloop.")
root.mainloop()
