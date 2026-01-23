import numpy as np
import sounddevice as sd
import threading
import time

# ---------- CONFIG ----------
SR        = 48_000
FRAMESIZE = 2048
f0        = 110.0
harmonics = [1, 2, 3, 5]
amp_lr    = 0.2
phase_lr  = 0.2
gain      = 20.0
running   = True

# ---------- DSP ----------
def target_z(f, fundamental):
    h = int(np.round(f / fundamental))
    return (1 / h) * np.exp(1j * 0) if h in harmonics else 0

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
        out = smith_block(noise, f0)
        stream.write(out)          # blocking write – no callback
    stream.stop(); stream.close()

# ---------- RUN ----------
print("♪  Blocking Smith-chart synth – Ctrl-C to quit  ♪")
try:
    threading.Thread(target=audio_loop, daemon=True).start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    running = False