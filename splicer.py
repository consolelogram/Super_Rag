import os
import math
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def setup_directories():
    """Creates the strict folder architecture required for the pipeline."""
    dirs = [
        "raw_video",
        "processed_data/clips",
        "processed_data/metadata"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
def segment_video(video_filename, chunk_length=10):
    """Slices a video into fixed-length chunks without re-encoding."""
    raw_path = os.path.join("raw_video", video_filename)
    
    if not os.path.exists(raw_path):
        print(f"Error: Drop your video in the 'raw_video' folder as '{video_filename}'.")
        return

    # Get total duration
    with VideoFileClip(raw_path) as video:
        duration = video.duration

    total_clips = math.ceil(duration / chunk_length)
    print(f"Total video duration: {duration:.2f} seconds. Segmenting into {total_clips} clips...")

    # Slice and export
    for i in range(total_clips):
        start_time = i * chunk_length
        end_time = min((i + 1) * chunk_length, duration)
        
        # Strict naming convention (clip_0000_0010.mp4) for vector/graph mapping later
        start_str = f"{int(start_time):04d}"
        end_str = f"{int(end_time):04d}"
        output_filename = f"clip_{start_str}_{end_str}.mp4"
        output_path = os.path.join("processed_data", "clips", output_filename)
        
        # Stream copy extraction
        ffmpeg_extract_subclip(raw_path, start_time, end_time, targetname=output_path)
        print(f"Created: {output_filename}")

if __name__ == "__main__":
    setup_directories()
    # Drop a test video named 'test.mp4' in raw_video/ before running
    segment_video("test.mp4", chunk_length=10)