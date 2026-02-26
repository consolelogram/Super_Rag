import json
import argparse

# =========================
# CONFIG
# =========================
ALPHA = 0.6  # text weight
BETA = 0.4   # visual weight

OUT_DEFAULT = "processed_data/phase8_ranked_events.json"


# =========================
def load_candidates(path, key):
    if not path:
        return {}

    with open(path) as f:
        data = json.load(f)

    items = data.get(key, [])
    return {item["event_id"]: item["score"] for item in items}


# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query_plan", required=True)
    parser.add_argument("--phase6", required=True)
    parser.add_argument("--phase7", default=None)
    parser.add_argument("--out", default=OUT_DEFAULT)
    args = parser.parse_args()

    with open(args.query_plan) as f:
        plan = json.load(f)

    text_scores = load_candidates(args.phase6, "initial_candidates")

    visual_scores = {}
    if args.phase7 and plan.get("use_visual", False):
        visual_scores = load_candidates(args.phase7, "visual_candidates")

    all_events = set(text_scores.keys()) | set(visual_scores.keys())

    ranked = []

    for eid in all_events:
        t = text_scores.get(eid, 0.0)
        v = visual_scores.get(eid, 0.0)

        if plan.get("use_visual", False):
            final = ALPHA * t + BETA * v
        else:
            final = t

        ranked.append({
            "event_id": eid,
            "final_score": round(final, 4),
            "text_score": round(t, 4),
            "visual_score": round(v, 4)
        })

    ranked.sort(key=lambda x: x["final_score"], reverse=True)

    with open(args.out, "w") as f:
        json.dump({"ranked_events": ranked}, f, indent=2)

    print(f"[OK] Phase 8 complete — ranked {len(ranked)} events")


# =========================
if __name__ == "__main__":
    main()
