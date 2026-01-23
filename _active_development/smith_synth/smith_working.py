import numpy as np
import sounddevice as sd

# ---------- CONFIG ----------
SR        = 48_000
FRAMESIZE = 2048
f0        = 110.0          # low A
harmonics = [1, 2, 3, 5]
amp_lr    = 0.2
phase_lr  = 0.2
THRESH    = 0.05
MAX_ITER  = 30

def target_z(f, fundamental):
    h = int(np.round(f / fundamental))
    return (1 / h) * np.exp(1j * 0) if h in harmonics else 0

def gamma(zl, z0):
    return (zl - z0) / (zl + z0) if z0 else 1.0

def smith_synth(frame, f):
    spec = np.fft.rfft(frame)
    freqs = np.fft.rfftfreq(len(frame), 1 / SR)
    for k, freq in enumerate(freqs):
        z0 = target_z(freq, f)
        if z0 == 0:
            spec[k] = 0
            continue
        for _ in range(MAX_ITER):
            g = gamma(spec[k], z0)
            if abs(g) < THRESH:
                break
            # crude gradient step
            spec[k] -= amp_lr * (spec[k].real - z0.real)
            spec[k] *= np.exp(-1j * phase_lr * np.angle(g))
    return np.fft.irfft(spec, n=len(frame))

def callback(indata, outdata, frames, time, status):
    noise = np.random.randn(frames).astype(np.float32)
    out = smith_synth(noise, f0) * 10.0  # << gain boost
    outdata[:, 0] = out

if __name__ == "__main__":
    print("♪  Press Ctrl-C to stop  ♪")
    try:
        with sd.OutputStream(
            samplerate=SR,
            blocksize=FRAMESIZE,
            channels=1,
            callback=callback
        ):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("Stopped.")