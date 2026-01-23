import tkinter as tk

class PolarOppositeSlidersAutoFlip(tk.Frame):
    """
    Two sliders A and B in [0..1] such that A + B = 1.
    Moving either slider updates the other, so sum is always 1.
    If A or B reaches 1, they automatically flip (swap values).
    """
    def __init__(self, master=None, labelA="A", labelB="B"):
        super().__init__(master)
        self.pack()

        self.labelA = labelA
        self.labelB = labelB

        # Avoid infinite recursion between callbacks
        self._in_callback = False

        # Variables for A and B
        self.varA = tk.DoubleVar(value=0.5)
        self.varB = tk.DoubleVar(value=0.5)

        self._build_ui()
        self._sync_sliders()  # ensure A + B = 1 initially

    def _build_ui(self):
        # Slider for A
        tk.Label(self, text=f"{self.labelA}").pack()
        self.sliderA = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01,
                                orient=tk.HORIZONTAL,
                                variable=self.varA,
                                command=self._on_sliderA)
        self.sliderA.pack(fill=tk.X, padx=5, pady=5)

        # Slider for B
        tk.Label(self, text=f"{self.labelB}").pack()
        self.sliderB = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01,
                                orient=tk.HORIZONTAL,
                                variable=self.varB,
                                command=self._on_sliderB)
        self.sliderB.pack(fill=tk.X, padx=5, pady=5)

        # Label for displaying A, B, and sum
        self.label_value = tk.Label(self, text="")
        self.label_value.pack(pady=5)

    def _on_sliderA(self, val_str):
        """
        Triggered when A’s slider moves.
        1) Force B = 1 - A
        2) If A = 1, swap A and B
        """
        if self._in_callback:
            return
        self._in_callback = True

        A = float(val_str)
        B = 1.0 - A
        self.varB.set(B)

        # Auto-flip if A is exactly 1
        if abs(A - 1.0) < 1e-9:
            self._flip()

        self._update_label()
        self._in_callback = False

    def _on_sliderB(self, val_str):
        """
        Triggered when B’s slider moves.
        1) Force A = 1 - B
        2) If B = 1, swap A and B
        """
        if self._in_callback:
            return
        self._in_callback = True

        B = float(val_str)
        A = 1.0 - B
        self.varA.set(A)

        # Auto-flip if B is exactly 1
        if abs(B - 1.0) < 1e-9:
            self._flip()

        self._update_label()
        self._in_callback = False

    def _flip(self):
        """
        Swap A and B (A->B, B->A).
        """
        A = self.varA.get()
        B = self.varB.get()
        self.varA.set(B)
        self.varB.set(A)

    def _sync_sliders(self):
        """
        Ensure A + B = 1 from initial state, then update display.
        """
        A = self.varA.get()
        self.varB.set(1.0 - A)
        self._update_label()

    def _update_label(self):
        """
        Show A, B, and A+B in the label.
        """
        A = self.varA.get()
        B = self.varB.get()
        self.label_value.config(
            text=f"{self.labelA} = {A:.2f}, {self.labelB} = {B:.2f}, sum = {A + B:.2f}"
        )

# Example usage if run as a script:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Polar Opposite Sliders (Auto-flip at 1)")
    pos = PolarOppositeSlidersAutoFlip(root, labelA="Alpha", labelB="Beta")
    root.mainloop()
