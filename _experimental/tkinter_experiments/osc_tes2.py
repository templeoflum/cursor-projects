import tkinter as tk
import numpy as np
import sounddevice as sd

class LightweightSineApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Lightweight Sine")

        # Internal state
        self.sr = 44100
        self.blocksize = 256
        self.phase = 0.0
        self.running = False
        
        # Sliders: both in [0,1], but frequency mapped to 0–1000 Hz
        self.amp_var = tk.DoubleVar(value=0.5)  # 0 -> silent, 1 -> max amplitude
        self.freq_var = tk.DoubleVar(value=0.4) # 0 -> 0 Hz, 1 -> 1000 Hz

        tk.Label(master, text="Amplitude").pack()
        tk.Scale(master, from_=0, to=1, resolution=0.01, 
                 orient=tk.HORIZONTAL, variable=self.amp_var).pack(fill=tk.X)

        tk.Label(master, text="Frequency").pack()
        tk.Scale(master, from_=0, to=1, resolution=0.01,
                 orient=tk.HORIZONTAL, variable=self.freq_var).pack(fill=tk.X)

        btn_frame = tk.Frame(master)
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Start", command=self.start_audio).pack(side=tk.LEFT, expand=True)
        tk.Button(btn_frame, text="Stop", command=self.stop_audio).pack(side=tk.LEFT, expand=True)

        # Simple canvas-based “oscilloscope”
        self.canvas = tk.Canvas(master, width=400, height=150, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.wave_id = None

        self.update_scope()  # start updating the scope

    def audio_callback(self, outdata, frames, time_info, status_flags):
        if status_flags:
            print(status_flags)
        amp = self.amp_var.get()
        freq_hz = self.freq_var.get() * 1000.0
        t = np.arange(frames)
        # Increment phase properly each block
        phase_inc = 2 * np.pi * freq_hz / self.sr
        # Generate sine wave in [0,1] by shifting and scaling
        data = amp * (0.5 * np.sin(self.phase + phase_inc * t) + 0.5)
        self.phase += phase_inc * frames
        self.phase %= 2 * np.pi
        outdata[:] = data.reshape(-1, 1)

    def start_audio(self):
        if not self.running:
            self.stream = sd.OutputStream(samplerate=self.sr,
                                          channels=1,
                                          blocksize=self.blocksize,
                                          callback=self.audio_callback)
            self.running = True
            self.stream.start()

    def stop_audio(self):
        if self.running:
            self.stream.stop()
            self.stream.close()
            self.running = False

    def update_scope(self):
        # Draw a quick representation of one block of data
        self.canvas.delete(self.wave_id)  # remove old line if it exists
        width = int(self.canvas.winfo_width())
        height = int(self.canvas.winfo_height())

        amp = self.amp_var.get()
        freq_hz = self.freq_var.get() * 1000.0
        t = np.arange(self.blocksize)
        phase_inc = 2 * np.pi * freq_hz / self.sr
        data = amp * (0.5 * np.sin(self.phase + phase_inc * t) + 0.5)

        # Scale each sample into canvas coordinates
        points = []
        for i, val in enumerate(data):
            x = i * width / self.blocksize
            y = height - (val * height)  # flip so 0 at bottom
            points.append((x, y))

        # Draw as one continuous polyline
        if len(points) > 1:
            flat_pts = []
            for p in points:
                flat_pts.extend(p)
            self.wave_id = self.canvas.create_line(flat_pts, fill="blue")

        # Don’t advance the phase for the visual block, so the audio & visuals remain in sync
        self.master.after(30, self.update_scope)  # ~30 FPS

def main():
    root = tk.Tk()
    app = LightweightSineApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
