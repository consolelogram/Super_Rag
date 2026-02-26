import os
import json
import av
from faster_whisper import WhisperModel

CLIPS_DIR = os.path.join("processed_data", "clips")
META_DIR = os.path.join("processed_data", "metadata")

MODEL_SIZE = "large-v3"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"


def has_audio_stream(video_path: str) -> bool:
    """
    Returns True if the video file has at least one audio stream.
    """
    try:
        container = av.open(video_path)
        audio_streams = [s for s in container.streams if s.type == "audio"]
        container.close()
        return len(audio_streams) > 0
    except Exception:
        return False


def transcribe_clips():
    os.makedirs(META_DIR, exist_ok=True)

    model = WhisperModel(
        MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE
    )

    clips = sorted(f for f in os.listdir(CLIPS_DIR) if f.endswith(".mp4"))

    for filename in clips:
        clip_path = os.path.join(CLIPS_DIR, filename)
        base = filename.replace(".mp4", "")
        out_path = os.path.join(META_DIR, f"{base}_stt.json")

        if os.path.exists(out_path):
            print(f"[SKIP] {filename}")
            continue

        print(f"Transcribing {filename}...")

        # -------- HARD AUDIO CHECK --------
        if not has_audio_stream(clip_path):
            print(f"[NO AUDIO STREAM] {filename}")
            payload = {
                "clip": filename,
                "transcript": ""
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            continue

        try:
            segments, info = model.transcribe(
                clip_path,
                beam_size=5,
                vad_filter=True
            )
            transcript = " ".join(seg.text.strip() for seg in segments)

        except Exception as e:
            print(f"[DECODE ERROR] {filename}: {e}")
            transcript = ""

        payload = {
            "clip": filename,
            "transcript": transcript
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        print(f"Saved -> {out_path}")


if __name__ == "__main__":
    transcribe_clips()
