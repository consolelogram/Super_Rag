import os
import json
from faster_whisper import WhisperModel

def transcribe_clips():
    """Iterates through video clips, transcribes audio, and saves metadata."""
    clips_dir = os.path.join("processed_data", "clips")
    meta_dir = os.path.join("processed_data", "metadata")
    
    # Initialize the model. Change device to "cuda" if you have an Nvidia GPU setup.
    print("Loading Faster-Whisper model (small)...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    
    # Grab all mp4 files and sort them to process in chronological order
    clips = sorted([f for f in os.listdir(clips_dir) if f.endswith(".mp4")])
    
    if not clips:
        print(f"Error: No clips found in {clips_dir}. Run Phase 1 first.")
        return

    for filename in clips:
        clip_path = os.path.join(clips_dir, filename)
        base_name = filename.replace(".mp4", "")
        meta_path = os.path.join(meta_dir, f"{base_name}_stt.json")
        
        # Skip if already processed (saves your life if the script crashes midway)
        if os.path.exists(meta_path):
            print(f"Skipping {filename} (already transcribed).")
            continue
            
        print(f"Transcribing {filename}...")
        
        # Transcribe directly from the mp4
        segments, info = model.transcribe(clip_path, beam_size=5)
        
        # Combine all spoken segments in the 10-second clip
        transcript = " ".join([segment.text for segment in segments]).strip()
        
        # Package and save the metadata
        metadata_payload = {
            "clip_filename": filename,
            "transcript": transcript
        }
        
        with open(meta_path, "w") as f:
            json.dump(metadata_payload, f, indent=4)
            
        print(f"Saved -> {meta_path}")

if __name__ == "__main__":
    transcribe_clips()