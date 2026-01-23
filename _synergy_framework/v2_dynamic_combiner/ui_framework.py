import tkinter as tk
from tkinter import filedialog

# Colors from the design language
COLORS = {
    "background": "#4B2E6F",  # Midnight Violet
    "accent": "#2EE59D",  # Aurora Green
    "secondary": "#D46344",  # Copper Dawn
    "neutral": "#E6E9EF",  # Morning Mist
    "text": "#FFFFFF",  # High contrast for readability
}

# Apply styles to the root window
def style_root_window(root):
    root.configure(bg=COLORS["background"])
    root.title("Dynamic Combiner Module")
    root.geometry("800x800")

# Create a label frame
def create_label_frame(parent, title, padx=10, pady=10):
    frame = tk.LabelFrame(parent, text=title, padx=padx, pady=pady, bg=COLORS["background"], fg=COLORS["text"])
    frame.pack(fill="x", padx=10, pady=5)
    return frame

# Create a listbox with a scrollbar
def create_listbox_with_scrollbar(parent, width=60, height=5):
    listbox = tk.Listbox(parent, width=width, height=height, bg=COLORS["neutral"], fg=COLORS["text"], highlightthickness=0)
    listbox.pack(side="left", fill="y", padx=5, pady=5)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)
    return listbox

# Add file button
def create_add_file_button(parent, label, file_paths, listbox):
    def add_file():
        file_path = filedialog.askopenfilename()
        if file_path and file_path not in file_paths:
            file_paths.append(file_path)
            listbox.insert(tk.END, file_path)
    tk.Button(parent, text=label, command=add_file, bg=COLORS["secondary"], fg=COLORS["text"]).pack(pady=5)

# Styled button with hover effect
def create_styled_button(parent, text, command):
    button = tk.Button(parent, text=text, command=command, bg=COLORS["secondary"], fg=COLORS["text"], relief="flat")
    button.bind("<Enter>", lambda e: button.config(bg=COLORS["accent"]))
    button.bind("<Leave>", lambda e: button.config(bg=COLORS["secondary"]))
    button.pack(pady=5)
    return button

def create_file_dropdown(parent, label, file_list, dropdown_var, file_type, file_extension, update_func):
    """
    Creates a dropdown menu and a button for adding files of a specific type.
    """
    frame = create_label_frame(parent, label)
    dropdown = tk.OptionMenu(frame, dropdown_var, "Select a file", *file_list)
    dropdown.pack(side="left", padx=5)
    tk.Button(frame, text=f"Add {file_type}",
              command=lambda: add_file_to_dropdown(file_list, dropdown_var, update_func, file_type, file_extension)).pack(side="left", padx=5)
    return dropdown


# Add file to dropdown
def add_file_to_dropdown(file_list, dropdown_var, file_type, file_extension):
    file_path = filedialog.askopenfilename(filetypes=[(file_type, file_extension)])
    if file_path and file_path not in file_list:
        file_list.append(file_path)
        dropdown_var.set(file_path)

# Create a slider for numeric input
def create_slider(parent, label, variable, from_=0, to=1, resolution=0.01, length=400):
    frame = create_label_frame(parent, label)
    slider = tk.Scale(frame, from_=from_, to=to, resolution=resolution, orient=tk.HORIZONTAL, length=length,
                      bg=COLORS["background"], fg=COLORS["text"], highlightthickness=0, troughcolor=COLORS["neutral"])
    slider.config(command=lambda val: variable.set(float(val)))
    slider.set(variable.get())
    slider.pack(fill="x", padx=10, pady=5)
    return slider
