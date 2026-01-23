# BPM Calculator

**Status:** ✅ Complete

Calculate how tempo changes when pitch-shifting music.

## What It Does

Given a base BPM, shows how the tempo changes for pitch shifts from -12 to +12 semitones.

Formula: `new_BPM = base_BPM × 2^(semitones/12)`

## Usage

```bash
python bpm_calculator.py
```

- Enter base BPM
- Click Calculate
- View table of all semitone/BPM combinations

## Requirements

Python 3 with tkinter (usually included by default).
