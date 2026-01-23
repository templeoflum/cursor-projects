import tkinter as tk

class PolarOppositeSlidersAutoFlipDrift(tk.Frame):
    """
    Two sliders A and B in [0..1] such that A + B = 1.
    1) Moving either slider updates the other, so sum is always 1.
    2) If A or B reaches 1, they automatically flip (swap values).
    3) Both A and B gradually drift toward 0.5 over time.
    """
    def __init__(self, master=None, labelA="A", labelB="B", drift_rate=0.02):
        super().__init__(master)
        self.pack()

        self.labelA = labelA
        self.labelB = labelB

        # For avoiding infinite recursion from slider callbacks
        self._in_callback = False

        # The drift rate toward 0.5 per update cycle (small fraction).
        self.drift_rate = drift_rate

        # Variables for A and B
        self.varA = tk.DoubleVar(value=0.5)
        self.varB = tk.DoubleVar(value=0.5)

        self._build_ui()
        self._sync_sliders()   # ensure A + B = 1 initially
        self._schedule_drift() # start drifting loop

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
        1) Force B = 1 - A.
        2) If A = 1, swap.
        """
        if self._in_callback:
            return
        self._in_callback = True

        A = float(val_str)
        B = 1.0 - A
        self.varB.set(B)

        # Auto-flip if A ~ 1
        if abs(A - 1.0) < 1e-9:
            self._flip()

        self._update_label()
        self._in_callback = False

    def _on_sliderB(self, val_str):
        """
        Triggered when B’s slider moves.
        1) Force A = 1 - B.
        2) If B = 1, swap.
        """
        if self._in_callback:
            return
        self._in_callback = True

        B = float(val_str)
        A = 1.0 - B
        self.varA.set(A)

        # Auto-flip if B ~ 1
        if abs(B - 1.0) < 1e-9:
            self._flip()

        self._update_label()
        self._in_callback = False

    def _flip(self):
        """
        Swap A and B instantly.
        """
        A = self.varA.get()
        B = self.varB.get()
        self.varA.set(B)
        self.varB.set(A)

    def _sync_sliders(self):
        """
        Ensure A + B = 1 from the initial state, then update display.
        """
        A = self.varA.get()
        self.varB.set(1.0 - A)
        self._update_label()

    def _update_label(self):
        """
        Show A, B, and their sum in the label.
        """
        A = self.varA.get()
        B = self.varB.get()
        self.label_value.config(
            text=f"{self.labelA} = {A:.2f}, {self.labelB} = {B:.2f}, sum = {A + B:.2f}"
        )

    def _schedule_drift(self):
        """ Schedule the next drift update in 50 ms. """
        self.after(50, self._drift_towards_center)

    def _drift_towards_center(self):
        """
        Each cycle, gently pull A toward 0.5. B is set to 1 - A.
        Then schedule the next drift.
        """
        if not self._in_callback:  
            # Only drift if we aren't in the middle of a slider callback
            self._in_callback = True

            A = self.varA.get()
            # Move A slightly toward 0.5
            A += self.drift_rate * (0.5 - A)
            # Clamp A to [0..1]
            A = max(0.0, min(1.0, A))

            self.varA.set(A)
            self.varB.set(1.0 - A)

            # If A or B hits 1, do a flip
            if abs(A - 1.0) < 1e-9:
                self._flip()

            self._update_label()
            self._in_callback = False

        # Schedule next iteration
        self._schedule_drift()

# Example usage if run as a script:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Polar Opposite Sliders (Auto-flip & Drift to 0.5)")
    pos = PolarOppositeSlidersAutoFlipDrift(
        root, labelA="Alpha", labelB="Beta", drift_rate=0.02
    )
    root.mainloop()
