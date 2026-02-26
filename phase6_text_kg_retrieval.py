import os
import json
import argparse
import numpy as np
import networkx as nx
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMB_DIR = os.path.join(BASE_DIR, "processed_data", "embeddings")
KG_PATH = os.path.join(BASE_DIR, "processed_data", "knowledge_graph.gml")

TEXT_EMB_PATH = os.path.join(EMB_DIR, "event_text_embeddings.npy")
TEXT_INDEX_PATH = os.path.join(EMB_DIR, "event_text_index.json")

OUT_PATH = os.path.join(BASE_DIR, "processed_data", "phase6_candidates.json")

TEXT_MODEL = "BAAI/bge-m3"

TOP_K = 10

# =========================
# LOADERS
# =========================
def load_embeddings():
    print("[DEBUG] Current working directory:", os.getcwd())
    print("[DEBUG] Expected embeddings dir:", EMB_DIR)

    if not os.path.exists(EMB_DIR):
        raise RuntimeError(f"Embeddings directory does not exist: {EMB_DIR}")

    files = os.listdir(EMB_DIR)
    print("[DEBUG] Files found in embeddings dir:", files)

    # Locate text embedding file dynamically
    text_emb_file = None
    index_file = None

    for f in files:
        if "text" in f and f.endswith(".npy"):
            text_emb_file = os.path.join(EMB_DIR, f)
        if "text" in f and f.endswith(".json"):
            index_file = os.path.join(EMB_DIR, f)

    if text_emb_file is None:
        raise RuntimeError("No text embedding .npy file found in embeddings dir")

    if index_file is None:
        raise RuntimeError("No text index .json file found in embeddings dir")

    print("[INFO] Using text embeddings:", text_emb_file)
    print("[INFO] Using text index:", index_file)

    emb = np.load(text_emb_file)
    with open(index_file) as f:
        index = json.load(f)

    return emb, index

def load_kg():
    return nx.read_gml(KG_PATH)


# =========================
# RETRIEVAL
# =========================
def retrieve_text_candidates(query, embedder, embeddings, index):
    query_vec = embedder.encode([query], normalize_embeddings=True)
    sims = cosine_similarity(query_vec, embeddings)[0]

    ranked = np.argsort(sims)[::-1][:TOP_K]

    results = []
    for i in ranked:
        results.append({
            "event_id": index[i],
            "score": float(sims[i])
        })
    return results


def expand_via_kg(events, G, hops=1):
    """
    Optional KG expansion: include neighbors of retrieved events.
    """
    expanded = set(e["event_id"] for e in events)

    for e in events:
        node = e["event_id"]
        if node not in G:
            continue
        for nbr in nx.single_source_shortest_path_length(G, node, cutoff=hops):
            expanded.add(nbr)

    return list(expanded)


# =========================
# MAIN
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query_plan", required=True)
    parser.add_argument("--out", default=OUT_PATH)
    args = parser.parse_args()

    with open(args.query_plan) as f:
        plan = json.load(f)

    if not plan.get("use_text", False):
        print("[INFO] Text retrieval not required by router.")
        with open(args.out, "w") as f:
            json.dump({"candidates": []}, f, indent=2)
        return

    print("[INFO] Loading text embedder...")
    embedder = SentenceTransformer(TEXT_MODEL)

    print("[INFO] Loading embeddings...")
    embeddings, index = load_embeddings()

    print("[INFO] Loading KG...")
    G = load_kg()

    print("[INFO] Retrieving candidates...")
    initial = retrieve_text_candidates(
        plan["text_query"],
        embedder,
        embeddings,
        index
    )

    expanded = expand_via_kg(initial, G)

    output = {
        "query": plan["text_query"],
        "initial_candidates": initial,
        "expanded_candidates": expanded
    }

    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[OK] Phase 6 complete — {len(initial)} initial candidates")


if __name__ == "__main__":
    main()
