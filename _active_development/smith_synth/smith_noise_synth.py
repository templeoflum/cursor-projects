import numpy as np
import sounddevice as sd   # pip install sounddevice

# -------------------- USER TWEAKS --------------------
SR          = 48_000       # sample rate
FRAMESIZE   = 2048         # STFT hop = FRAMESIZE // 4
TARGET_HARM = [1, 2, 3, 5] # harmonic numbers to reinforce
LEARNING    = dict(a=0.2,  p=0.2)  # amplitude & phase learning rates
THRESHOLD   = 0.05         # stop iterating when error < this
MAX_ITERS   = 30           # safety guard
# -----------------------------------------------------

def target_impedance(f, f0):
    """Return the complex Z0 for a harmonic partial."""
    harm_idx = int(np.round(f / f0))
    if harm_idx in TARGET_HARM:
        mag = 1.0 / harm_idx     # 1/n amplitude rule
        phase = 0.0              # lock phase to zero for simplicity
        return mag * np.exp(1j * phase)
    return 0.0                   # zero everywhere else

def reflection(zl, z0):
    """Smith-chart Γ."""
    if z0 == 0:
        return 1.0               # undefined, treat as total mismatch
    return (zl - z0) / (zl + z0)

def smith_synth(noise_frame, f0):
    """Transform one STFT frame."""
    X = np.fft.rfft(noise_frame)
    freqs = np.fft.rfftfreq(len(noise_frame), 1/SR)
    for k, f in enumerate(freqs):
        z0 = target_impedance(f, f0)
        if z0 == 0:
            X[k] = 0
            continue
        for _ in range(MAX_ITERS):
            gamma = reflection(X[k], z0)
            if abs(gamma) < THRESHOLD:
                break
            # gradient descent on amplitude & phase
            X[k] -= LEARNING['a'] * (X[k].real - z0.real)
            phase_shift = -LEARNING['p'] * np.angle(gamma)
            X[k] *= np.exp(1j * phase_shift)
    return np.fft.irfft(X, n=len(noise_frame))

# -------------------- REAL-TIME LOOP --------------------
def callback(indata, outdata, frames, time, status):
    noise = np.random.randn(frames).astype(np.float32)
    outdata[:, 0] = smith_synth(noise, f0=110.0)  # fundamental = 110 Hz

with sd.Stream(samplerate=SR, blocksize=FRAMESIZE,
               channels=1, callback=callback):
    print("♪ Playing Smith-chart noise synth.  Ctrl-C to stop ♪")
    while True:
        sd.sleep(1000)