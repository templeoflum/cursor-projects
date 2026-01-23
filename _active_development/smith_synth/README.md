# Smith Noise Synth

**Status:** 🔨 In Development

Real-time audio synthesizer that creates tones from noise using harmonic shaping.

## Concept

Uses FFT analysis to extract harmonics from colored noise (white/pink/brown), then reshapes them using amplitude and phase controls inspired by Smith-chart impedance concepts.

## Versions

**Full version** (recommended):
```bash
python smith_full_tk.py
```
- Preset save/load
- Attack/decay envelope
- Noise color selection
- 8 harmonic controls

**Pure version** (simpler):
```bash
python smith_pure_tk.py
```
- Just pitch, gain, and harmonic controls

## Requirements

```bash
pip install -r requirements.txt
```

- `numpy`
- `sounddevice`

## Future Development

- More harmonic controls
- MIDI input
- Effects processing
- Better presets
