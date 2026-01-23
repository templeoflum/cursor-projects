"""
smith_debug_sound.py – minimal loop that prints *everything*
"""
import numpy as np
import sounddevice as sd
import time

SR        = 48_000
FRAMESIZE = 2048
f0        = 440.0          # purposely loud A4
harmonics = [1]

def target_z(f, fundamental):
    h = int(np.round(f / fundamental))
    return (1 / h) if 1 <= h <= 8 and h in harmonics else 0

def process_block(noise, f0):
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(len(noise), 1 / SR)
    for k, f in enumerate(freqs):
        z0 = target_z(f, f0)
        if z0 == 0:
            spec[k] = 0
            continue
        spec[k] = z0  # replace instead of iterate for clarity
    out = np.fft.irfft(spec, n=len(noise))
    return out * 20.0        # 20× gain → ~0.4 peak

# ---------- TEST OUTPUT ----------
print("Available devices:")
print(sd.query_devices())

print("\nUsing default device:", sd.default.device)

# simple blocking test – 1 second worth of frames
for i in range(int(SR / FRAMESIZE)):
    noise = np.random.randn(FRAMESIZE) * 0.5
    audio = process_block(noise, f0)
    print(f"Frame {i}: max={audio.max():.3f}  rms={np.sqrt(np.mean(audio**2)):.3f}")
    sd.play(audio, SR, blocking=True)

print("Finished 1-second burst")