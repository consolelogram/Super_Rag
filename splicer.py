import os
import math
import subprocess

CLIPS_DIR = os.path.join("processed_data", "clips")
os.makedirs(CLIPS_DIR, exist_ok=True)

def segment_video(video_path, chunk_length=10):
    # Get duration
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    duration = float(subprocess.check_output(cmd).decode().strip())
    print(f"Total video duration: {duration:.2f} seconds")

    num_chunks = math.ceil(duration / chunk_length)

    for i in range(num_chunks):
        start = i * chunk_length
        length = min(chunk_length, duration - start)

        out = os.path.join(
            CLIPS_DIR,
            f"clip_{start:04.0f}_{start+length:04.0f}.mp4"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-i", video_path,
            "-t", str(length),
            "-map", "0:v:0",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            out
        ]

        subprocess.run(cmd, check=True)
        print(f"Saved {out}")

if __name__ == "__main__":
    segment_video("D:\\ramratanhacksrm\\ramr\\raw_video\\test.mp4", chunk_length=10)
