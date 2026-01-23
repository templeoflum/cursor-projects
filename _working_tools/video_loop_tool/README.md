# Video Loop Tool

**Status:** ✅ Working

GUI tool for video concatenation and creating seamless loops from multiple clips.

## Features

**Concatenate:** Join multiple videos into one

**Seamless Loop:** Takes exactly 4 videos and creates a complex seamless loop by:
- Splitting each video at midpoint
- Reversing certain segments
- Reassembling into 16-segment palindromic pattern
- Perfect for AI-generated video (Sora, etc.)

## Requirements

- Python 3+
- FFmpeg/FFprobe (bundled in `ffmpeg_executables/` or in PATH)

## Usage

**First time setup:**
```bash
python run_video_tool_setup.py
```

**After setup:**
```bash
cd video_tool/VideoLoopTool_Project
python video_tool_app_ui.py
```

## Notes

- Works with video-only clips (strips audio)
- Best with same codec/resolution/framerate inputs
