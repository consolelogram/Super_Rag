import os
import json
import cv2
import base64
import ollama

# =========================================================
# CONFIG
# =========================================================
NUM_FRAMES = 5   # adjust freely

CLIPS_DIR = os.path.join("processed_data", "clips")
META_DIR = os.path.join("processed_data", "metadata")

# =========================================================
# FRAME EXTRACTION (ROBUST)
# =========================================================
def extract_frames(video_path, num_frames=NUM_FRAMES):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_b64 = []

    if total_frames <= 0 or num_frames <= 0:
        cap.release()
        return frames_b64

    indices = [
        int((i + 1) * total_frames / (num_frames + 1))
        for i in range(num_frames)
    ]

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue

        h, w, _ = frame.shape
        # Critical guard: prevents GGML tensor crashes
        if h < 64 or w < 64:
            continue

        _, buffer = cv2.imencode(".jpg", frame)
        frames_b64.append(base64.b64encode(buffer).decode("utf-8"))

    cap.release()
    return frames_b64

# =========================================================
# JSON EXTRACTION (FIXED)
# =========================================================
def extract_json(text: str):
    text = text.strip()

    # Remove markdown fences if present
    if text.startswith("```"):
        text = text.strip("`")
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:].strip()

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("No JSON found")

    return json.loads(text[start:end])

# =========================================================
# MAIN PIPELINE
# =========================================================
def run_phase2b():
    clips = sorted(f for f in os.listdir(CLIPS_DIR) if f.endswith(".mp4"))

    for filename in clips:
        base = filename.replace(".mp4", "")
        stt_path = os.path.join(META_DIR, f"{base}_stt.json")
        vlm_path = os.path.join(META_DIR, f"{base}_vlm.json")

        if os.path.exists(vlm_path):
            print(f"[SKIP] {filename} already processed")
            continue

        if not os.path.exists(stt_path):
            print(f"[SKIP] Missing STT for {filename}")
            continue

        print(f"[VLM] Processing {filename}")

        # ---------------- Load transcript ----------------
        with open(stt_path, "r", encoding="utf-8") as f:
            stt_data = json.load(f)
            transcript = stt_data.get("transcript", "No dialogue.")

        # ---------------- Frames ----------------
        clip_path = os.path.join(CLIPS_DIR, filename)
        images_b64 = extract_frames(clip_path)

        if not images_b64:
            print(f"[WARN] No valid frames for {filename}")
            continue

        # ---------------- Prompt ----------------
        prompt = (
            "You are analyzing a 10-second video clip using sequential frames.\n\n"
            f"Dialogue (context only): \"{transcript}\"\n\n"
            "You MUST return a JSON object with ALL fields filled.\n\n"
            "Rules:\n"
            "- Entities must be concrete, visible nouns (people, objects, locations).\n"
            "- Do NOT leave the entities list empty.\n"
            "- If unsure, list the most likely visible entity.\n\n"
            "Return STRICT JSON only:\n"
            "{\n"
            "  \"entities\": [\"person\", \"object\", \"location\"],\n"
            "  \"actions\": [\"...\"],\n"
            "  \"temporal_phases\": {\n"
            "    \"start\": \"...\",\n"
            "    \"middle\": \"...\",\n"
            "    \"end\": \"...\"\n"
            "  }\n"
            "}"
        )

        # ---------------- Model call ----------------
        try:
            response = ollama.chat(
                model="qwen2.5vl:7b",
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": images_b64
                }]
            )

            raw = response["message"]["content"].strip()

            try:
                parsed = extract_json(raw)
            except Exception:
                parsed = {
                    "error": "JSON_PARSE_FAILED",
                    "raw_output": raw
                }

            with open(vlm_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)

            print(f"[OK] Saved {vlm_path}")

        except Exception as e:
            print(f"[ERROR] {filename}: {e}")

# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":
    run_phase2b()
