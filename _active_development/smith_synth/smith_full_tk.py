"""
smith_full_tk.py – full-parameter Smith-chart noise synth
"""
import json, os, threading, time, numpy as np, sounddevice as sd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------- CONFIG ----------
SR        = 48_000
FRAMESIZE = 2048
MAX_HARM  = 8
PRESET_DIR = "presets"

os.makedirs(PRESET_DIR, exist_ok=True)

# ---------- STATE ----------
state = {
    "midi_note": 69,
    "fine_cents": 0,
    "glide_ms": 0,
    "harm_amp": [1.0 / h for h in range(1, MAX_HARM + 1)],
    "harm_phase": [0.0] * MAX_HARM,
    "noise_colour": 0.0,           # 0=white, 1=pink, 2=brown
    "attack_ms": 1,
    "decay_ms": 1000,
    "mix": 1.0,
    "gain": 1.0,
    "limit": 0.95,
    "running": True
}

current_f0 = midi_to_f0 = lambda m, c: 440 * 2 ** ((m - 69 + c / 100) / 12)
envelope_buf = np.ones(FRAMESIZE)
lock = threading.Lock()

# ---------- DSP ----------
def noise_colour(n, colour):
    # 0=white, 1=pink (1/f), 2=brown (1/f²)
    if colour == 0: return n
    if colour == 1: return np.cumsum(n) * 0.0001
    return np.cumsum(np.cumsum(n)) * 1e-6

def ad_envelope(length, attack, decay):
    a = int(attack * 0.001 * SR)
    d = int(decay * 0.001 * SR)
    env = np.ones(length)
    if a: env[:a] = np.linspace(0, 1, a)
    if d and a + d < length:
        env[a:a + d] = np.linspace(1, 0.1, d)
    return env

def smith_block(noise):
    with lock:
        f = current_f0(state["midi_note"], state["fine_cents"])
        amps  = np.array(state["harm_amp"],  dtype=np.float32)
        phases = np.array(state["harm_phase"], dtype=np.float32)
    spec = np.fft.rfft(noise.astype(np.float32))
    freqs = np.fft.rfftfreq(len(noise), 1 / SR)
    out_spec = np.zeros_like(spec, dtype=np.complex64)
    for k, freq in enumerate(freqs):
        h = int(np.round(freq / f))
        if 1 <= h <= MAX_HARM:
            out_spec[k] = amps[h - 1] * np.exp(1j * phases[h - 1])
    out = np.fft.irfft(out_spec, n=len(noise))
    env = ad_envelope(len(noise), state["attack_ms"], state["decay_ms"])
    out = out * env * state["gain"]
    out = np.tanh(out / state["limit"]) * state["limit"]
    dry = noise * 0.1
    final = dry * (1 - state["mix"]) + out * state["mix"]
    return final.astype(np.float32)

def audio_loop():
    stream = sd.OutputStream(SR, FRAMESIZE, channels=1)
    stream.start()
    while state["running"]:
        noise = noise_colour(np.random.randn(FRAMESIZE), state["noise_colour"])
        out = smith_block(noise)
        stream.write(out)
    stream.stop(); stream.close()

# ---------- GUI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smith-Chart Synth – Full Panel")
        self.geometry("700x650")
        self.build_ui()
        threading.Thread(target=audio_loop, daemon=True).start()

    def build_ui(self):
        # MIDI + fine
        frm = ttk.LabelFrame(self, text="Pitch")
        frm.pack(fill="x", padx=5, pady=5)
        ttk.Label(frm, text="MIDI").grid(row=0, column=0)
        ttk.Scale(frm, from_=24, to=96, orient="horizontal",
                  command=lambda v: self.update("midi_note", int(float(v)))).set(state["midi_note"])
        ttk.Label(frm, text="Fine (cents)").grid(row=0, column=2)
        ttk.Scale(frm, from_=-50, to=50, orient="horizontal",
                  command=lambda v: self.update("fine_cents", float(v))).grid(row=0, column=3)

        # Glide
        ttk.Label(frm, text="Glide (ms)").grid(row=1, column=0)
        ttk.Scale(frm, from_=0, to=1000, orient="horizontal",
                  command=lambda v: self.update("glide_ms", float(v))).grid(row=1, column=1, columnspan=3, sticky="ew")

        # Harmonics
        harm_frm = ttk.LabelFrame(self, text="Harmonics (amp & phase)")
        harm_frm.pack(fill="both", expand=True, padx=5, pady=5)
        for h in range(1, MAX_HARM + 1):
            ttk.Label(harm_frm, text=f"{h}").grid(row=h - 1, column=0)
            ttk.Scale(harm_frm, from_=0, to=2, orient="horizontal",
                      command=lambda v, h=h: self.update("harm_amp", float(v), idx=h - 1)).grid(row=h - 1, column=1, sticky="ew")
            ttk.Scale(harm_frm, from_=-3.14, to=3.14, orient="horizontal",
                      command=lambda v, h=h: self.update("harm_phase", float(v), idx=h - 1)).grid(row=h - 1, column=2, sticky="ew")

        # Misc controls
        misc = ttk.LabelFrame(self, text="Global")
        misc.pack(fill="x", padx=5, pady=5)
        for key, frm, to in [("noise_colour", 0, 2), ("attack_ms", 1, 1000), ("decay_ms", 1, 5000),
                             ("mix", 0, 1), ("gain", 0.1, 5), ("limit", 0.2, 1)]:
            ttk.Label(misc, text=key.replace("_", " ").title()).pack(side="left")
            ttk.Scale(misc, from_=frm, to=to, orient="horizontal",
                      command=lambda v, k=key: self.update(k, float(v))).pack(side="left", fill="x", expand=True)

        # Presets
        preset = ttk.Frame(self)
        preset.pack(fill="x", padx=5, pady=5)
        ttk.Button(preset, text="Save Preset", command=self.save_preset).pack(side="left")
        ttk.Button(preset, text="Load Preset", command=self.load_preset).pack(side="left")
        ttk.Button(preset, text="Panic", command=self.panic).pack(side="left")

    def update(self, key, val, idx=None):
        with lock:
            if idx is None:
                state[key] = val
            else:
                state[key][idx] = val

    def save_preset(self):
        file = filedialog.asksaveasfilename(defaultextension=".json", initialdir=PRESET_DIR)
        if file:
            with open(file, "w") as f:
                json.dump({k: v for k, v in state.items() if k != "running"}, f, indent=2)

    def load_preset(self):
        file = filedialog.askopenfilename(initialdir=PRESET_DIR, filetypes=[("JSON", "*.json")])
        if file:
            with open(file) as f:
                data = json.load(f)
            with lock:
                state.update(data)
            self.sync_ui()

    def sync_ui(self):
        # crude: rebuild window – fast enough for demo
        for w in self.winfo_children():
            w.destroy()
        self.build_ui()

    def panic(self):
        state["gain"] = 0.0
        time.sleep(0.1)
        state["gain"] = 1.0

if __name__ == "__main__":
    App().mainloop()