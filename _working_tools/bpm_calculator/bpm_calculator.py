import tkinter as tk
from tkinter import ttk
import math

class BPMCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BPM Calculator")
        self.root.geometry("400x600")

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Input section
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 20))

        self.bpm_label = ttk.Label(self.input_frame, text="Base BPM:")
        self.bpm_label.pack(side=tk.LEFT, padx=(0, 10))

        self.bpm_entry = ttk.Entry(self.input_frame, width=10)
        self.bpm_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.bpm_entry.insert(0, "120")

        self.calculate_button = ttk.Button(self.input_frame, text="Calculate", command=self.calculate_bpm)
        self.calculate_button.pack(side=tk.LEFT)

        # Results section
        self.results_frame = ttk.Frame(self.main_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeview for results
        self.tree = ttk.Treeview(self.results_frame, columns=("Semitones", "BPM"), show="headings", height=25)
        self.tree.heading("Semitones", text="Semitones")
        self.tree.heading("BPM", text="BPM")
        self.tree.column("Semitones", width=100, anchor=tk.CENTER)
        self.tree.column("BPM", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Calculate initial values
        self.calculate_bpm()

    def calculate_bpm(self):
        try:
            base_bpm = float(self.bpm_entry.get())
            self.tree.delete(*self.tree.get_children())
            
            for semitone in range(-12, 13):
                new_bpm = base_bpm * (2 ** (semitone / 12))
                item_id = self.tree.insert("", tk.END, values=(f"{semitone:+d}", f"{new_bpm:.2f}"))
                # Optionally highlight the original BPM (0 semitones)
                if semitone == 0:
                    self.tree.item(item_id, tags=("original",))
        except ValueError:
            self.tree.delete(*self.tree.get_children())
            self.tree.insert("", tk.END, values=("Error", "Invalid BPM"))

if __name__ == "__main__":
    root = tk.Tk()
    app = BPMCalculator(root)
    root.mainloop() 