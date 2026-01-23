import numpy as np, sounddevice as sd

SR, FRAMESIZE = 48000, 2048
f0 = 110.0
harmonics=[1,2,3,5]
amp_lr=phase_lr=0.2
THRESH=0.05; MAX_ITER=30

def target_z(f, fundamental):
    h=int(np.round(f/fundamental))
    return (1/h)*np.exp(1j*0) if h in harmonics else 0
def gamma(zl,z0): return (zl-z0)/(zl+z0) if z0 else 1.0

def smith_block(noise, f):
    spec=np.fft.rfft(noise)
    freqs=np.fft.rfftfreq(len(noise),1/SR)
    for k,freq in enumerate(freqs):
        z0=target_z(freq,f)
        if z0==0: spec[k]=0; continue
        for _ in range(MAX_ITER):
            g=gamma(spec[k],z0)
            if abs(g)<THRESH: break
            spec[k]-=amp_lr*(spec[k].real-z0.real)
            spec[k]*=np.exp(-1j*phase_lr*np.angle(g))
    return np.fft.irfft(spec,n=len(noise))*20.0

def callback(indata,outdata,frames,time,status):
    noise=np.random.randn(frames).astype(np.float32)
    outdata[:,0]=smith_block(noise,f0)

print("♪  Press Ctrl-C to stop  ♪")
with sd.OutputStream(SR,FRAMESIZE,channels=1,callback=callback):
    while True: sd.sleep(1000)