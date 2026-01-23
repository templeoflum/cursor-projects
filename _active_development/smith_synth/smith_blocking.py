"""
smith_blocking.py – real-time Smith-chart noise synth without PortAudio callbacks
"""
import numpy as np
import sounddevice as sd   # still used only for sd.play (blocking)
import dearpygui.dearpygui as dpg
import threading
import time

# ---------- CONFIG ----------
SR        = 48_000
FRAMESIZE = 2048
MAX_HARM  = 16
f0        = 220.0
harmonics = [1, 2, 3, 5]
amp_lr    = 0.2
phase_lr  = 0.2
running   = True

# ---------- DSP ----------
def midi_to_f0(m): return 440 * 2 ** ((m - 69) / 12)

def target_z(f, fundamental):
    h = int(np.round(f / fundamental))
    return (1 / h) * np.exp(1j * 0) if 1 <= h <= MAX_HARM and h in harmonics else 0

def gamma(zl, z0):
    return (zl - z0) / (zl + z0) if z0 else 1.0

def process_block(noise, f0):
    win = np.hanning(FRAMESIZE)
    x   = np.zeros(FRAMESIZE)
    x[:len(noise)] = noise
    spec = np.fft.rfft(win * x)
    freqs = np.fft.rfftfreq(FRAMESIZE, 1 / SR)

    for k, f in enumerate(freqs):
        z0_val = target_z(f, f0)
        if z0_val == 0:
            spec[k] = 0
            continue
        for _ in range(30):
            g = gamma(spec[k], z0_val)
            if abs(g) < 0.05:
                break
            spec[k] -= amp_lr * (spec[k].real - z0_val.real)
            spec[k] *= np.exp(-1j * phase_lr * np.angle(g))

    out = np.fft.irfft(spec, n=FRAMESIZE) * win
    return out[:len(noise)]

# ---------- AUDIO THREAD (blocking) ----------
def audio_loop():
    while running:
        noise = np.random.randn(FRAMESIZE).astype(np.float32)
        audio = process_block(noise, midi_to_f0(midi_note))
        sd.play(audio, SR, blocking=True)

# ---------- GUI ----------
midi_note = 69   # A4

dpg.create_context()
dpg.create_viewport(title="Smith Blocking Synth", width=500, height=300)

with dpg.window(label="Controls"):
    def update_f0_from_midi(sender, value):
        global midi_note, f0
        midi_note = int(value)
        f0 = midi_to_f0(midi_note)

    dpg.add_slider_int(label="MIDI Note", default_value=midi_note,
                       min_value=24, max_value=96, callback=update_f0_from_midi)

    dpg.add_text("Harmonics")
    for h in range(1, MAX_HARM + 1):
        dpg.add_checkbox(label=str(h), default_value=(h in harmonics),
                         callback=lambda s, v, h=h: (harmonics.append(h) if v else harmonics.remove(h)))

    dpg.add_button(label="Quit", callback=lambda: globals().__setitem__('running', False))

dpg.setup_dearpygui()
dpg.show_viewport()

# start audio in background (blocking `sd.play` is thread-safe)
threading.Thread(target=audio_loop, daemon=True).start()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

running = False
dpg.destroy_context()