import tkinter as tk

class PolarOppositeSliders(tk.Frame):
    """
    Two sliders A and B in [0..1] such that A + B = 1.
    Moving either slider updates the other.
    A label shows A, B, and the sum (always 1).
    A Flip button swaps A and B.
    """
    def __init__(self, master=None, labelA="A", labelB="B"):
        super().__init__(master)
        self.pack()

        # Keep track if we're already updating to avoid infinite callbacks
        self._in_callback = False

        self.labelA = labelA
        self.labelB = labelB

        # Variables for A and B
        self.varA = tk.DoubleVar(value=0.5)
        self.varB = tk.DoubleVar(value=0.5)

        # Build UI
        self._build_ui()

        # Sync initial values
        self._sync_sliders()

    def _build_ui(self):
        # Slider for A
        tk.Label(self, text=f"{self.labelA}").pack()
        self.sliderA = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01,
                                orient=tk.HORIZONTAL, variable=self.varA,
                                command=self._on_sliderA)
        self.sliderA.pack(fill=tk.X, padx=5, pady=5)

        # Slider for B
        tk.Label(self, text=f"{self.labelB}").pack()
        self.sliderB = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01,
                                orient=tk.HORIZONTAL, variable=self.varB,
                                command=self._on_sliderB)
        self.sliderB.pack(fill=tk.X, padx=5, pady=5)

        # Label for displaying values
        self.label_value = tk.Label(self, text="")
        self.label_value.pack(pady=5)

        # Flip button
        tk.Button(self, text="Flip", command=self._flip_values).pack()

    def _on_sliderA(self, new_val):
        """
        Triggered when A’s slider moves.
        Forces B = 1 - A, updates display.
        """
        if self._in_callback:
            return
        self._in_callback = True

        A = float(new_val)
        B = 1.0 - A
        self.varB.set(B)

        self._update_label()

        self._in_callback = False

    def _on_sliderB(self, new_val):
        """
        Triggered when B’s slider moves.
        Forces A = 1 - B, updates display.
        """
        if self._in_callback:
            return
        self._in_callback = True

        B = float(new_val)
        A = 1.0 - B
        self.varA.set(A)

        self._update_label()

        self._in_callback = False

    def _flip_values(self):
        """
        Swaps A and B (A -> B, B -> A).
        """
        A = self.varA.get()
        B = self.varB.get()
        self.varA.set(B)
        self.varB.set(A)
        self._update_label()

    def _sync_sliders(self):
        """
        Ensures A + B = 1 from the initial default or assigned values.
        """
        A = self.varA.get()
        self.varB.set(1.0 - A)
        self._update_label()

    def _update_label(self):
        """
        Updates the displayed text to show A, B, and their sum.
        """
        A = self.varA.get()
        B = self.varB.get()
        self.label_value.config(
            text=f"{self.labelA} = {A:.2f},  {self.labelB} = {B:.2f},  Sum = {A + B:.2f}"
        )

# Example usage if run as a script:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Polar Opposite Sliders Example")
    pos = PolarOppositeSliders(root, labelA="Alpha", labelB="Beta")
    root.mainloop()
