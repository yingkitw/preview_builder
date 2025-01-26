import subprocess
import cv2
import os
import numpy as np
from pathlib import Path
import argparse
import json

class PreviewBuilder:
    def __init__(self, output_dir):
        # Video preview resolutions (for App Store)
        self.iphone_video_resolution = (886, 1920)
        self.ipad_video_resolution = (1200, 1600)
        
        # Screenshot resolutions (high resolution)
        self.iphone_screenshot_resolution = (1320, 2868)  # Higher resolution for screenshots
        self.ipad_screenshot_resolution = (2064, 2752)    # Higher resolution for screenshots
        
        self.required_duration = 60  # 1 minute in seconds
        self.screenshot_count = 10
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def _get_audio_duration(self, audio_path):
        """Get audio duration using FFprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(audio_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])

    def process_video(self, input_video, audio_file, device_type='iphone'):
        # Create screenshots directory if it doesn't exist
        screenshots_dir = self.output_dir / f'{device_type}_screenshots'
        screenshots_dir.mkdir(exist_ok=True)

        # Set resolution based on device type for video preview
        if device_type.lower() == 'iphone':
            width, height = self.iphone_video_resolution
        else:
            width, height = self.ipad_video_resolution

        # Generate output video filename
        output_video = self.output_dir / f'{device_type}_preview.mp4'

        # Calculate number of loops needed to reach 1 minute for both video and audio
        video_duration = self._get_video_duration(input_video)
        audio_duration = self._get_audio_duration(audio_file)
        
        video_loops = max(1, int(np.ceil(self.required_duration / video_duration)))
        audio_loops = max(1, int(np.ceil(self.required_duration / audio_duration)))

        print(f"Video duration: {video_duration:.2f}s (looping {video_loops} times)")
        print(f"Audio duration: {audio_duration:.2f}s (looping {audio_loops} times)")

        # Process video with FFmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Overwrite output file if exists
            '-stream_loop', str(video_loops),
            '-i', str(input_video),
            '-stream_loop', str(audio_loops),
            '-i', str(audio_file),
            '-vf', f'scale={width}:{height},pad={width}:{height}:0:0',
            '-t', str(self.required_duration),
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', '128k',
            str(output_video)
        ]

        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Generated preview video for {device_type}: {output_video}")

        # Capture screenshots from original input video
        self._capture_screenshots(str(input_video), screenshots_dir, device_type)

    def _get_video_duration(self, video_path):
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        cap.release()
        return duration

    def _capture_screenshots(self, video_path, output_dir, device_type):
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Get screenshot resolution based on device type
        if device_type.lower() == 'iphone':
            width, height = self.iphone_screenshot_resolution
        else:
            width, height = self.ipad_screenshot_resolution
        
        # Calculate frame positions for exactly 10 screenshots
        # Use linspace to get exactly 10 evenly spaced positions
        frame_positions = np.linspace(0, total_frames - 1, self.screenshot_count, dtype=int)
        
        screenshot_count = 0
        for frame_pos in frame_positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if ret:
                # Resize frame to the correct resolution
                frame_resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LANCZOS4)
                screenshot_path = os.path.join(output_dir, f'{device_type}_screenshot_{screenshot_count + 1}.jpg')
                cv2.imwrite(screenshot_path, frame_resized)
                print(f"Captured screenshot {screenshot_count + 1}/10: {screenshot_path}")
                screenshot_count += 1
        
        cap.release()
        
        # Verify we got all screenshots
        if screenshot_count != self.screenshot_count:
            print(f"Warning: Only captured {screenshot_count} screenshots instead of {self.screenshot_count}")

def main():
    parser = argparse.ArgumentParser(description='Create App Store preview videos and screenshots')
    parser.add_argument('--iphone', required=True, help='Input iPhone video file')
    parser.add_argument('--ipad', required=True, help='Input iPad video file')
    parser.add_argument('--audio', required=True, help='Input audio file (MP3)')
    parser.add_argument('--output', default='output', help='Output directory (default: output)')
    
    args = parser.parse_args()
    
    # Validate input files exist
    for input_file in [args.iphone, args.ipad, args.audio]:
        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            return 1
    
    preview_builder = PreviewBuilder(args.output)
    
    # Process iPhone video
    print("\nProcessing iPhone video...")
    preview_builder.process_video(
        input_video=args.iphone,
        audio_file=args.audio,
        device_type='iphone'
    )
    
    # Process iPad video
    print("\nProcessing iPad video...")
    preview_builder.process_video(
        input_video=args.ipad,
        audio_file=args.audio,
        device_type='ipad'
    )
    
    print("\nAll processing completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
