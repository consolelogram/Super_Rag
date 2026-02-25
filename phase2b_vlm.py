import os
import json
import cv2
import base64
import ollama

def extract_frames(video_path, num_frames=3):
    """Extracts evenly spaced frames from a video clip."""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_b64 = []
    
    if total_frames == 0:
        return frames_b64

    # Calculate intervals for start, middle, and end frames
    intervals = [int(total_frames * 0.1), int(total_frames * 0.5), int(total_frames * 0.9)]
    
    for frame_idx in intervals:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            # Convert frame to jpg, then to base64 for Ollama
            _, buffer = cv2.imencode('.jpg', frame)
            b64_str = base64.b64encode(buffer).decode('utf-8')
            frames_b64.append(b64_str)
            
    cap.release()
    return frames_b64

def generate_visual_captions():
    """Feeds frames and audio transcripts to the VLM to generate scene descriptions."""
    clips_dir = os.path.join("processed_data", "clips")
    meta_dir = os.path.join("processed_data", "metadata")
    
    clips = sorted([f for f in os.listdir(clips_dir) if f.endswith(".mp4")])
    
    for filename in clips:
        base_name = filename.replace(".mp4", "")
        vlm_path = os.path.join(meta_dir, f"{base_name}_vlm.json")
        stt_path = os.path.join(meta_dir, f"{base_name}_stt.json")
        
        if os.path.exists(vlm_path):
            print(f"Skipping {filename} (already captioned).")
            continue
            
        print(f"Analyzing visuals for {filename}...")
        
        # 1. Grab the transcript from Phase 2a
        transcript = "No dialogue."
        if os.path.exists(stt_path):
            with open(stt_path, "r") as f:
                stt_data = json.load(f)
                transcript = stt_data.get("transcript", "No dialogue.")
                
        # 2. Extract visual frames
        clip_path = os.path.join(clips_dir, filename)
        images_b64 = extract_frames(clip_path)
        
        if not images_b64:
            print(f"Failed to extract frames for {filename}.")
            continue

        # 3. Multi-modal Prompt Fusion
        prompt = (
            f"You are analyzing a 10-second video clip. "
            f"Here is the spoken dialogue during this clip: '{transcript}'. "
            f"Based on this audio context and the provided sequential frames, "
            f"write a brief, factual description of the scene, identifying key objects, people, and actions."
        )

        try:
            response = ollama.chat(
                model='llava',
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': images_b64
                }]
            )
            caption = response['message']['content'].strip()
            
            # 4. Save the combined knowledge
            metadata_payload = {
                "clip_filename": filename,
                "caption": caption
            }
            
            with open(vlm_path, "w") as f:
                json.dump(metadata_payload, f, indent=4)
                
            print(f"Saved -> {vlm_path}")
            
        except Exception as e:
            print(f"Error processing {filename} with Ollama: {e}")

if __name__ == "__main__":
    # Ensure Ollama is running in the background before executing!
    generate_visual_captions()