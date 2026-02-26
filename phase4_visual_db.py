import os
import json
import subprocess
import tempfile
import numpy as np
from PIL import Image

import torch
from transformers import CLIPModel, CLIPProcessor
import networkx as nx

# =============================
# CONFIG
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CLIPS_DIR = os.path.join(BASE_DIR, "processed_data", "clips")
KG_PATH   = os.path.join(BASE_DIR, "processed_data", "knowledge_graph.gml")
OUT_DIR   = os.path.join(BASE_DIR, "processed_data", "embeddings")

CLIP_MODEL = "openai/clip-vit-large-patch14"

os.makedirs(OUT_DIR, exist_ok=True)

# =============================
# FRAME EXTRACTION (ROBUST)
# =============================
def extract_frames(video_path):
    """
    Extract a single representative frame using FFmpeg's thumbnail filter.
    This works on all MP4s and all FFmpeg builds.
    """
    images = []

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "frame.jpg")

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", "thumbnail",
            "-frames:v", "1",
            "-q:v", "2",
            out_path,
            "-y",
            "-loglevel", "error"
        ]

        try:
            subprocess.run(cmd, check=True)
            if os.path.exists(out_path):
                img = Image.open(out_path).convert("RGB")
                images.append(img)
        except Exception:
            pass

    return images

# =============================
# MAIN
# =============================
def build_visual_embeddings():
    print("[INFO] Loading Knowledge Graph...")
    G = nx.read_gml(KG_PATH)

    events = [
        (node, attrs)
        for node, attrs in G.nodes(data=True)
        if attrs.get("type") == "event"
    ]

    print(f"[INFO] Found {len(events)} events")

    if not events:
        print("[ERROR] No event nodes found.")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Loading CLIP on {device}...")

    model = CLIPModel.from_pretrained(CLIP_MODEL).to(device)
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL)
    model.eval()

    visual_embeddings = []
    event_ids = []

    for event_id, attrs in events:
        clip_base = attrs.get("clip")
        if not clip_base:
            print(f"[SKIP] {event_id}: no clip field")
            continue

        clip_name = clip_base if clip_base.endswith(".mp4") else clip_base + ".mp4"
        clip_path = os.path.join(CLIPS_DIR, clip_name)

        if not os.path.exists(clip_path):
            print(f"[SKIP] Missing file: {clip_name}")
            continue

        frames = extract_frames(clip_path)
        if not frames:
            print(f"[SKIP] No frames extracted: {clip_name}")
            continue

        inputs = processor(images=frames, return_tensors="pt").to(device)

        with torch.no_grad():
            vision_out = model.vision_model(
                pixel_values=inputs["pixel_values"]
            )
            image_features = vision_out.pooler_output
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        clip_embedding = image_features.mean(dim=0).cpu().numpy()

        visual_embeddings.append(clip_embedding)
        event_ids.append(event_id)

        print(f"[OK] Embedded {clip_name}")

    if not visual_embeddings:
        print("[ERROR] No visual embeddings generated. Check clips.")
        return

    visual_embeddings = np.vstack(visual_embeddings)

    np.save(
        os.path.join(OUT_DIR, "event_visual_embeddings.npy"),
        visual_embeddings
    )

    with open(os.path.join(OUT_DIR, "event_visual_index.json"), "w") as f:
        json.dump(event_ids, f, indent=2)

    print(f"[OK] Saved {visual_embeddings.shape[0]} visual embeddings")
    print("[DONE] Phase 4 (visual) complete")

# =============================
if __name__ == "__main__":
    build_visual_embeddings()
