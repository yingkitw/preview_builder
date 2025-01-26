# App Store Preview Builder

This Python script helps create preview videos for the App Store, supporting both iPhone and iPad formats.

## Features

### Video Previews
- iPhone preview: 886x1920
- iPad preview: 1200x1600
- Adds background audio
- Ensures videos are exactly 30 seconds long
- H.264 encoding with High Profile Level 4.0
- Target bit rate: 10-12 Mbps
- VBR max rate: 220 Mbps
- Frame rate: 30 fps

### Screenshots
- iPhone screenshots: 1320x2868
- iPad screenshots: 2064x2752
- Captures 6 evenly-spaced screenshots from each video
- High-quality resizing using Lanczos algorithm

### Audio
- Stereo configuration
- AAC codec
- 256 kbps bitrate
- 48 kHz sample rate

## Supported File Extensions
- Video: `.mov`, `.m4v`, `.mp4`
- Audio: `.mp3`, `.wav`, `.aac`

## Requirements

- Python 3.7+
- FFmpeg installed on your system
- OpenCV and NumPy Python packages

## Installation

Install the required Python packages globally:

```bash
pip install opencv-python numpy
```

## Usage

```bash
python preview_builder.py --iphone INPUT_IPHONE_VIDEO --ipad INPUT_IPAD_VIDEO --audio BACKGROUND_AUDIO [--output OUTPUT_DIR]
```

### Arguments

- `--iphone`: Input iPhone video file (required)
- `--ipad`: Input iPad video file (required)
- `--audio`: Input audio file (required)
- `--output`: Output directory (optional, default: 'output')

### Example

```bash
python preview_builder.py --iphone recording_iphone.mp4 --ipad recording_ipad.mp4 --audio background.mp3 --output my_previews
```

### Output Structure

The script will create the following structure in your output directory:
- `output/iphone_preview.mp4` - Processed iPhone video (886x1920)
- `output/ipad_preview.mp4` - Processed iPad video (1200x1600)
- `output/iphone_screenshots/` - Directory containing 6 iPhone screenshots (1320x2868)
- `output/ipad_screenshots/` - Directory containing 6 iPad screenshots (2064x2752)
