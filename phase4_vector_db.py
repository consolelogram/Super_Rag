import os
import json
import numpy as np
import networkx as nx
from sentence_transformers import SentenceTransformer
import torch

# =========================================================
# CONFIG
# =========================================================
GRAPH_PATH = os.path.join("processed_data", "knowledge_graph.gml")
META_DIR = os.path.join("processed_data", "metadata")
OUT_DIR = os.path.join("processed_data", "vectors")

MODEL_NAME = "BAAI/bge-m3"
BATCH_SIZE = 64   # 4090 can handle this easily

os.makedirs(OUT_DIR, exist_ok=True)

# =========================================================
# LOAD MODEL (GPU)
# =========================================================
print("[INFO] Loading BGE-M3 on GPU...")
embedder = SentenceTransformer(
    MODEL_NAME,
    device="cuda"
)
embedder.max_seq_length = 2048
print("[OK] Model loaded")

# =========================================================
# HELPERS
# =========================================================
def load_stt_text(clip_name):
    path = os.path.join(META_DIR, f"{clip_name}_stt.json")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("transcript", "")

def load_vlm_text(clip_name):
    path = os.path.join(META_DIR, f"{clip_name}_vlm.json")
    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    actions = " ".join(data.get("actions", []))
    phases = data.get("temporal_phases", {})
    temporal = " ".join(phases.values())

    return f"{actions}. {temporal}".strip()

# =========================================================
# MAIN
# =========================================================
def build_embeddings():
    G = nx.read_gml(GRAPH_PATH)

    event_visual_texts = []
    event_audio_texts = []
    entity_texts = []

    event_visual_nodes = []
    event_audio_nodes = []
    entity_nodes = []

    # ---------------- EVENTS ----------------
    for node, attrs in G.nodes(data=True):
        if attrs.get("type") != "event":
            continue

        clip = attrs["clip"]

        visual_text = load_vlm_text(clip)
        audio_text = load_stt_text(clip)

        if visual_text:
            event_visual_texts.append(visual_text)
            event_visual_nodes.append(node)

        if audio_text:
            event_audio_texts.append(audio_text)
            event_audio_nodes.append(node)

    # ---------------- ENTITIES ----------------
    for node, attrs in G.nodes(data=True):
        if attrs.get("type") != "entity":
            continue

        name = attrs.get("name", "")
        if name:
            entity_texts.append(name)
            entity_nodes.append(node)

    print(f"[INFO] Embedding {len(event_visual_texts)} event-visual texts")
    print(f"[INFO] Embedding {len(event_audio_texts)} event-audio texts")
    print(f"[INFO] Embedding {len(entity_texts)} entities")

    # ---------------- EMBEDDING (GPU) ----------------
    event_visual_vecs = embedder.encode(
        event_visual_texts,
        batch_size=BATCH_SIZE,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    event_audio_vecs = embedder.encode(
        event_audio_texts,
        batch_size=BATCH_SIZE,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    entity_vecs = embedder.encode(
        entity_texts,
        batch_size=BATCH_SIZE,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # ---------------- SAVE ----------------
    np.save(os.path.join(OUT_DIR, "event_visual.npy"), event_visual_vecs)
    np.save(os.path.join(OUT_DIR, "event_audio.npy"), event_audio_vecs)
    np.save(os.path.join(OUT_DIR, "entity.npy"), entity_vecs)

    index = {
        "event_visual": event_visual_nodes,
        "event_audio": event_audio_nodes,
        "entity": entity_nodes
    }

    with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print("[OK] Phase 4 embeddings saved")

# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":
    torch.cuda.empty_cache()
    build_embeddings()
