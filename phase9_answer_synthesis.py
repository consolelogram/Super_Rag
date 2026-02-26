import os
import json
import argparse
import networkx as nx

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KG_PATH = os.path.join(BASE_DIR, "processed_data", "knowledge_graph.gml")
OUT_DEFAULT = os.path.join(BASE_DIR, "processed_data", "final_answer.json")

TOP_N = 3  # number of events to show as evidence


# =========================
def format_timestamp(clip_name):
    """
    clip_0020_0030 -> 00:20–00:30
    """
    try:
        parts = clip_name.replace("clip_", "").replace(".mp4", "").split("_")
        start = int(parts[0])
        end = int(parts[1])
        return f"{start//60:02d}:{start%60:02d}–{end//60:02d}:{end%60:02d}"
    except Exception:
        return "unknown"


def extract_event_evidence(event_id, attrs, G):
    evidence = []

    if attrs.get("caption"):
        evidence.append(attrs["caption"])

    if attrs.get("transcript"):
        evidence.append(f'Dialogue: "{attrs["transcript"]}"')

    # Entities involved
    entities = []
    for nbr in G.neighbors(event_id):
        n_attrs = G.nodes[nbr]
        if n_attrs.get("type") == "entity":
            label = n_attrs.get("label") or nbr
            entities.append(label)

    if entities:
        evidence.append("Entities: " + ", ".join(entities))

    return " | ".join(evidence)


# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query_plan", required=True)
    parser.add_argument("--phase8", required=True)
    parser.add_argument("--out", default=OUT_DEFAULT)
    args = parser.parse_args()

    with open(args.query_plan) as f:
        plan = json.load(f)

    with open(args.phase8) as f:
        ranked = json.load(f)["ranked_events"]

    G = nx.read_gml(KG_PATH)

    top_events = ranked[:TOP_N]

    results = []
    for e in top_events:
        event_id = e["event_id"]
        if event_id not in G:
            continue

        attrs = G.nodes[event_id]
        clip = attrs.get("clip", "")
        timestamp = format_timestamp(clip)

        evidence = extract_event_evidence(event_id, attrs, G)

        results.append({
            "event_id": event_id,
            "timestamp": timestamp,
            "score": e["final_score"],
            "evidence": evidence
        })

    answer_payload = {
        "query": plan["original_query"],
        "answer": "Relevant events are listed below based on multimodal evidence.",
        "supporting_events": results
    }

    with open(args.out, "w") as f:
        json.dump(answer_payload, f, indent=2)

    print("[OK] Phase 9 complete — final answer generated")


# =========================
if __name__ == "__main__":
    main()
