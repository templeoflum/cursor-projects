import numpy as np
import sounddevice as sd
import threading
import time
import tkinter as tk
from tkinter import ttk

# ---------------- CONFIG ----------------
SR        = 48_000
FRAMESIZE = 2048
f0        = 220.0          # A3
harmonics = [1, 2, 3, 5]
amp_lr    = 0.2
phase_lr  = 0.2
gain      = 20.0
running   = True           # global kill-switch
midi_note = 57             # default A3

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
        for _ in range(30):
            g = gamma(spec[k], z0)
            if abs(g) < 0.05:
                break
            spec[k] -= amp_lr * (spec[k].real - z0.real)
            spec[k] *= np.exp(-1j * phase_lr * np.angle(g))
    return np.fft.irfft(spec, n=len(noise)) * gain

# ---------- AUDIO THREAD ----------
def audio_loop():
    stream = sd.OutputStream(SR, FRAMESIZE, channels=1)
    stream.start()
    while running:
        noise = np.random.randn(FRAMESIZE).astype(np.float32)
        out = smith_block(noise, midi_to_f0(midi_note))
        stream.write(out)
    stream.stop(); stream.close()

# ---------- GUI ----------
def build_gui():
    global midi_note
    root = tk.Tk()
    root.title("Smith-Chart Synth")

    # MIDI note slider
    ttk.Label(root, text="MIDI Note").pack(pady=2)
    note_var = tk.IntVar(value=midi_note)
    scale = ttk.Scale(root, from_=24, to=96, variable=note_var,
                      orient="horizontal",
                      command=lambda v: globals().__setitem__('midi_note', int(float(v))))
    scale.pack(fill="x", padx=10)

    # Harmonic toggles
    frame = ttk.LabelFrame(root, text="Harmonics 1-8")
    frame.pack(pady=5)
    for h in range(1, 9):
        var = tk.BooleanVar(value=(h in harmonics))
        cb = ttk.Checkbutton(frame, text=str(h),
                             variable=var,
                             command=lambda h=h, v=var: (harmonics.append(h) if v.get() else harmonics.remove(h)))
        cb.grid(row=(h-1)//4, column=(h-1) % 4, padx=2, pady=2)

    # Quit
    quit_btn = ttk.Button(root, text="Quit", command=lambda: globals().__setitem__('running', False) or root.quit())
    quit_btn.pack(pady=10)

    root.mainloop()

# ---------- RUN ----------
if __name__ == "__main__":
    threading.Thread(target=audio_loop, daemon=True).start()
    build_gui()