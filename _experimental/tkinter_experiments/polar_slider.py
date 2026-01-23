import tkinter as tk

class PolarOppositeSlider(tk.Frame):
    """
    A simple widget that keeps A + B = 1.
    Slider sets A in [0..1], B is 1 - A.
    A Flip button inverts them: A -> 1 - A, B -> 1 - B.
    """
    def __init__(self, master=None, labelA="A", labelB="B"):
        super().__init__(master)
        self.pack()

        self.labelA = labelA
        self.labelB = labelB

        # State variable for A in [0..1].
        # B is always 1 - A.
        self.varA = tk.DoubleVar(value=0.5)

        # Build UI
        self._build_ui()

        # Initial update
        self._update_labels()

    def _build_ui(self):
        # Slider controlling A
        tk.Label(self, text=f"Slide {self.labelA}").pack()
        slider = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01,
                          orient=tk.HORIZONTAL, variable=self.varA,
                          command=self._on_slider)
        slider.pack(fill=tk.X, padx=5, pady=5)

        # Labels for A and B
        self.label_value = tk.Label(self, text="")
        self.label_value.pack()

        # Flip button
        flip_btn = tk.Button(self, text="Flip", command=self._flip_values)
        flip_btn.pack(pady=5)

    def _on_slider(self, *args):
        """
        Called whenever the slider moves.
        Enforces A in [0..1], sets B = 1 - A, updates labels.
        """
        self._update_labels()

    def _flip_values(self):
        """
        Swaps A and B by setting A -> 1 - A.
        """
        currentA = self.varA.get()
        self.varA.set(1.0 - currentA)
        self._update_labels()

    def _update_labels(self):
        """
        Updates the displayed text for A and B.
        """
        A = self.varA.get()
        B = 1.0 - A
        self.label_value.config(
            text=f"{self.labelA}: {A:.2f},  {self.labelB}: {B:.2f}"
        )

# Example usage if run as a script:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Polar Opposite Slider Example")
    pos = PolarOppositeSlider(root, labelA="Value X", labelB="Value Y")
    root.mainloop()
