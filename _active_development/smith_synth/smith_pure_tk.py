import numpy as np, sounddevice as sd, threading, tkinter as tk
from tkinter import ttk

# ---------- CONFIG ----------
SR        = 48_000
FRAMESIZE = 2048
MAX_HARM  = 8

state = {
    "gain": 1.0,
    "pitch": 69,           # MIDI note
    "harm_amp":  [1/h for h in range(1, MAX_HARM+1)],
    "harm_phase": [0.0]*MAX_HARM,
    "noise_type": 0,       # 0=white, 1=pink, 2=brown
    "smith_mix": 1.0,      # 0=raw, 1=fully processed, >1=overdrive
}
lock = threading.Lock()

# ---------- DSP ----------
def midi_to_f0(m): return 440 * 2 ** ((m - 69) / 12)

def noise_gen(n, t):
    if t == 0: return np.random.randn(n).astype(np.float32)
    if t == 1: return np.cumsum(np.random.randn(n)) * 0.0001
    return np.cumsum(np.cumsum(np.random.randn(n))) * 1e-6

def smith_block(buf, f0):
    with lock:
        amps  = np.array(state["harm_amp"],  dtype=np.float32)
        phs   = np.array(state["harm_phase"], dtype=np.float32)
        mix   = state["smith_mix"]
        gain  = state["gain"]
    spec = np.fft.rfft(buf)
    freqs = np.fft.rfftfreq(len(buf), 1/SR)
    out_spec = np.zeros_like(spec)
    for k, f in enumerate(freqs):
        h = int(np.round(f / f0))
        if 1 <= h <= MAX_HARM:
            out_spec[k] = amps[h-1] * np.exp(1j * phs[h-1])
    out = np.fft.irfft(out_spec, n=len(buf))
    raw = buf * 0.1
    final = raw * (1 - mix) + out * mix
    return np.tanh(final * gain).astype(np.float32)

def audio_loop():
    stream = sd.OutputStream(SR, FRAMESIZE, channels=1)
    stream.start()
    while True:
        buf = noise_gen(FRAMESIZE, state["noise_type"])
        out = smith_block(buf, midi_to_f0(state["pitch"]))
        stream.write(out)

# ---------- GUI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smith-Chart Noise Synth")
        self.geometry("500x600")
        self.build_ui()
        threading.Thread(target=audio_loop, daemon=True).start()

    def build_ui(self):
        # persistent Tk variables
        self.pitch_var   = tk.IntVar(value=state["pitch"])
        self.gain_var    = tk.DoubleVar(value=state["gain"])
        self.mix_var     = tk.DoubleVar(value=state["smith_mix"])
        self.noise_var   = tk.IntVar(value=state["noise_type"])

        # Pitch
        ttk.Label(self, text="Pitch (MIDI)").pack()
        ttk.Scale(self, from_=24, to=96, orient="horizontal",
                  variable=self.pitch_var,
                  command=lambda v: self.update("pitch", int(float(v)))).pack()

        # Gain
        ttk.Label(self, text="Gain").pack()
        ttk.Scale(self, from_=0.1, to=5, orient="horizontal",
                  variable=self.gain_var,
                  command=lambda v: self.update("gain", float(v))).pack()

        # Smith mix
        ttk.Label(self, text="Smith Mix (0–raw, 1–full, >1–over)").pack()
        ttk.Scale(self, from_=0, to=2, orient="horizontal",
                  variable=self.mix_var,
                  command=lambda v: self.update("smith_mix", float(v))).pack()

        # Noise type radio
        ttk.Label(self, text="Noise Type").pack()
        for idx, name in enumerate(("White", "Pink", "Brown")):
            ttk.Radiobutton(self, text=name, value=idx,
                            variable=self.noise_var,
                            command=lambda i=idx: self.update("noise_type", i)).pack(anchor="w")

        # Harmonics
        frm = ttk.LabelFrame(self, text="Harmonics (amp / phase)")
        frm.pack(fill="both", expand=True, padx=5, pady=5)
        self.h_amp_vars  = [tk.DoubleVar(value=v) for v in state["harm_amp"]]
        self.h_pha_vars  = [tk.DoubleVar(value=v) for v in state["harm_phase"]]

        for h in range(1, MAX_HARM + 1):
            ttk.Label(frm, text=f"{h}").grid(row=h-1, column=0)
            ttk.Scale(frm, from_=0, to=2, orient="horizontal",
                      variable=self.h_amp_vars[h-1],
                      command=lambda v, i=h-1: self.update("harm_amp", float(v), idx=i)).grid(row=h-1, column=1, sticky="ew")
            ttk.Scale(frm, from_=-3.14, to=3.14, orient="horizontal",
                      variable=self.h_pha_vars[h-1],
                      command=lambda v, i=h-1: self.update("harm_phase", float(v), idx=i)).grid(row=h-1, column=2, sticky="ew")

        ttk.Button(self, text="Quit", command=self.quit).pack(pady=5)

    def update(self, key, val, idx=None):
        with lock:
            if idx is None:
                state[key] = val
            else:
                state[key][idx] = val

if __name__ == "__main__":
    App().mainloop()