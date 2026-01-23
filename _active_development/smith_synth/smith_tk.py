"""
smith_tk.py – Smith-chart noise synth with Tkinter GUI
"""
import numpy as np
import sounddevice as sd
import threading
import time
import tkinter as tk
from tkinter import ttk

# ---------------- CONFIG ----------------
SR        = 48_000
FRAMESIZE = 2048
f0        = 220.0
harmonics = [1, 2, 3, 5]
amp_lr    = 0.2
phase_lr  = 0.2
THRESH    = 0.05
MAX_ITER  = 30
running   = True       # global kill-switch

# ---------------- DSP ----------------
def midi_to_f0(m): return 440 * 2 ** ((m - 69) / 12)

def target_z(f, fundamental):
    h = int(np.round(f / fundamental))
    return (1 / h) * np.exp(1j * 0) if 1 <= h <= 8 and h in harmonics else 0

def gamma(zl, z0):
    return (zl - z0) / (zl + z0) if z0 else 1.0

def smith_block(noise, f):
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(len(noise), 1 / SR)
    for k, freq in enumerate(freqs):
        z0 = target_z(freq, f)
        if z0 == 0:
            spec[k] = 0
            continue
        for _ in range(MAX_ITER):
            g = gamma(spec[k], z0)
            if abs(g) < THRESH:
                break
            spec[k] -= amp_lr * (spec[k].real - z0.real)
            spec[k] *= np.exp(-1j * phase_lr * np.angle(g))
    out = np.fft.irfft(spec, n=len(noise))
    return out * 10.0  # gain

def audio_callback(indata, outdata, frames, time_, status):
    noise = np.random.randn(frames).astype(np.float32)
    outdata[:, 0] = smith_block(noise, midi_to_f0(midi_note))

def audio_loop():
    try:
        with sd.OutputStream(SR, FRAMESIZE, channels=1, callback=audio_callback):
            while running:
                time.sleep(0.1)
    except Exception as e:
        print("AUDIO THREAD CRASHED:", e)
        import traceback; traceback.print_exc()

# ---------------- GUI ----------------
def build_gui():
    global midi_note
    root = tk.Tk()
    root.title("Smith Chart Synth (Tk)")

    ttk.Label(root, text="MIDI Note").grid(row=0, column=0, padx=5, pady=5)
    note_var = tk.IntVar(value=69)
    scale = ttk.Scale(root, from_=24, to=96, variable=note_var,
                      orient="horizontal", command=lambda v: globals().__setitem__('midi_note', int(float(v))))
    scale.grid(row=0, column=1, padx=5, pady=5)
    midi_note = note_var.get()

    ttk.Label(root, text="Harmonics 1-8").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    harm_vars = []
    for h in range(1, 9):
        var = tk.BooleanVar(value=(h in harmonics))
        cb = ttk.Checkbutton(root, text=str(h),
                             variable=var,
                             command=lambda h=h, v=var: (harmonics.append(h) if v.get() else harmonics.remove(h)))
        cb.grid(row=1 + (h-1)//4, column=1 + (h-1) % 4, padx=2, pady=2)

    quit_btn = ttk.Button(root, text="Quit", command=lambda: globals().__setitem__('running', False) or root.quit())
    quit_btn.grid(row=3, column=0, columnspan=5, pady=10)

    root.mainloop()

# ---------------- RUN ----------------
if __name__ == "__main__":
    threading.Thread(target=audio_loop, daemon=True).start()
    build_gui()