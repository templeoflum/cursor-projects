"""
smith_debug.py – instrumented callback to expose the real signature being invoked
"""
import numpy as np
import sounddevice as sd
import threading
import time
import inspect
import dearpygui.dearpygui as dpg

# ---------------- CONFIG ----------------
SR, FRAMESIZE = 48_000, 2048

# ---------- INSTRUMENTED CALLBACK ----------
def dsp_callback(indata, outdata, frames, time_, status):
    # 1. Print what we actually received
    print("[CALLBACK] args:", len(inspect.signature(dsp_callback).parameters),
          "data:", outdata.shape, "frames:", frames, "status:", status)

    # 2. Fill buffer to avoid underflow
    outdata[:] = 0.1 * np.sin(2 * np.pi * 440 * np.arange(frames) / SR)[:, None]

# ---------- QUICK GUI (optional) ----------
dpg.create_context()
dpg.create_viewport(title="Debug Smith", width=300, height=100)
with dpg.window(label="Debug"):
    dpg.add_text("Close to quit.")
dpg.setup_dearpygui()
dpg.show_viewport()

# ---------- START STREAM ----------
try:
    stream = sd.OutputStream(
        samplerate=SR,
        blocksize=FRAMESIZE,
        channels=1,
        callback=dsp_callback
    )
    stream.start()
    print("✅ Stream started")
except Exception as e:
    print("❌ Could not start:", e)
    raise

# ---------- GUI LOOP ----------
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

stream.stop()
stream.close()
dpg.destroy_context()