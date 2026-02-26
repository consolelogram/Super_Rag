import os
import json
import argparse
import numpy as np
import torch
from transformers import CLIPModel, CLIPProcessor
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMB_DIR = os.path.join(BASE_DIR, "processed_data", "embeddings")

VIS_EMB_PATH = os.path.join(EMB_DIR, "event_visual_embeddings.npy")
VIS_INDEX_PATH = os.path.join(EMB_DIR, "event_visual_index.json")

OUT_PATH = os.path.join(BASE_DIR, "processed_data", "phase7_visual_candidates.json")

CLIP_MODEL = "openai/clip-vit-large-patch14"
TOP_K = 10

# =========================
def load_visual_embeddings():
    emb = np.load(VIS_EMB_PATH)
    with open(VIS_INDEX_PATH) as f:
        index = json.load(f)
    return emb, index


def embed_query_clip(query, model, processor, device):
    inputs = processor(
        text=[query],
        return_tensors="pt",
        padding=True
    ).to(device)

    with torch.no_grad():
        text_out = model.text_model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )
        text_features = text_out.pooler_output
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    return text_features.cpu().numpy()


# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query_plan", required=True)
    parser.add_argument("--phase6", required=True)
    parser.add_argument("--out", default=OUT_PATH)
    args = parser.parse_args()

    with open(args.query_plan) as f:
        plan = json.load(f)

    if not plan.get("use_visual", False):
        print("[INFO] Visual retrieval not required by router.")
        with open(args.out, "w") as f:
            json.dump({"visual_candidates": []}, f, indent=2)
        return

    print("[INFO] Loading CLIP...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained(CLIP_MODEL).to(device)
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL)
    model.eval()

    print("[INFO] Loading visual embeddings...")
    vis_emb, vis_index = load_visual_embeddings()

    # Optional: restrict search space using Phase 6
    with open(args.phase6) as f:
        phase6 = json.load(f)

    allowed = set()
    for c in phase6.get("initial_candidates", []):
        allowed.add(c["event_id"])

    # Filter embeddings
    if allowed:
        filtered_emb = []
        filtered_ids = []
        for emb, eid in zip(vis_emb, vis_index):
            if eid in allowed:
                filtered_emb.append(emb)
                filtered_ids.append(eid)

        vis_emb = np.vstack(filtered_emb)
        vis_index = filtered_ids

    print(f"[INFO] Visual search space size: {len(vis_index)}")

    print("[INFO] Embedding visual query...")
    query_vec = embed_query_clip(
        plan["visual_query"],
        model,
        processor,
        device
    )

    sims = cosine_similarity(query_vec, vis_emb)[0]
    ranked = np.argsort(sims)[::-1][:TOP_K]

    results = []
    for i in ranked:
        results.append({
            "event_id": vis_index[i],
            "score": float(sims[i])
        })

    with open(args.out, "w") as f:
        json.dump({"visual_candidates": results}, f, indent=2)

    print(f"[OK] Phase 7 complete — {len(results)} visual candidates")


# =========================
if __name__ == "__main__":
    main()
