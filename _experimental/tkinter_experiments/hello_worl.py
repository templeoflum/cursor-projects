import tkinter as tk

def build_ui(root, params):
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    label = tk.Label(frame, text="Hello World!", bg="lightblue")
    label.pack(pady=10)

    return frame
