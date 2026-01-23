from tkinter import filedialog

# File Management
def load_yaml_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def add_file(layer_paths, listbox):
    file_path = filedialog.askopenfilename()
    if file_path:
        layer_paths.append(file_path)
        listbox.insert(tk.END, os.path.basename(file_path))
