import os
import json
import numpy as np
import networkx as nx
from sentence_transformers import SentenceTransformer

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KG_PATH = os.path.join(BASE_DIR, "processed_data", "knowledge_graph.gml")
OUT_DIR = os.path.join(BASE_DIR, "processed_data", "embeddings")

TEXT_MODEL = "BAAI/bge-m3"

os.makedirs(OUT_DIR, exist_ok=True)

# =========================
def build_text_embeddings():
    print("[INFO] Loading Knowledge Graph...")
    G = nx.read_gml(KG_PATH)

    events = [
        (node, attrs)
        for node, attrs in G.nodes(data=True)
        if attrs.get("type") == "event"
    ]

    if not events:
        raise RuntimeError("No event nodes found in KG")

    print(f"[INFO] Found {len(events)} events")

    texts = []
    event_ids = []

    for event_id, attrs in events:
        parts = []

        if "caption" in attrs and attrs["caption"]:
            parts.append(attrs["caption"])

        if "transcript" in attrs and attrs["transcript"]:
            parts.append(attrs["transcript"])

        for event_id, attrs in events:
            parts = []

            # 1. Caption from VLM
            if attrs.get("caption"):
                parts.append(attrs["caption"])

            # 2. Transcript from ASR
            if attrs.get("transcript"):
                parts.append(attrs["transcript"])

            # 3. Fallback: derive text from KG relations
            if not parts:
                neighbors = list(G.neighbors(event_id))
                entity_texts = []

                for n in neighbors:
                    n_attrs = G.nodes[n]
                    if n_attrs.get("type") == "entity":
                        label = n_attrs.get("label") or n
                        entity_texts.append(label)

                if entity_texts:
                    parts.append("Entities involved: " + ", ".join(entity_texts))

            # Final check
            if not parts:
                continue

    combined = " ".join(parts).strip()
    texts.append(combined)
    event_ids.append(event_id)

    print(f"[INFO] Embedding {len(texts)} event texts")

    embedder = SentenceTransformer(TEXT_MODEL)
    embeddings = embedder.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    np.save(
        os.path.join(OUT_DIR, "event_text_embeddings.npy"),
        embeddings
    )

    with open(os.path.join(OUT_DIR, "event_text_index.json"), "w") as f:
        json.dump(event_ids, f, indent=2)

    print("[OK] Text embeddings saved")
    print("[DONE] Phase 4 (text) complete")


# =========================
if __name__ == "__main__":
    build_text_embeddings()
