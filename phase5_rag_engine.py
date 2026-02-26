import json
import re
import argparse
import ollama

# =========================
# CONFIG
# =========================
ROUTER_MODEL = "llama3"   # or mistral, qwen, etc.

# =========================
# SIMPLE INTENT HEURISTICS
# =========================
VISUAL_KEYWORDS = [
    "see", "look", "appear", "wearing", "holding", "color", "object",
    "person", "man", "woman", "car", "sign", "room", "scene", "visual"
]

TEMPORAL_KEYWORDS = [
    "before", "after", "during", "while", "then", "earlier", "later",
    "sequence", "timeline", "first", "next", "last"
]

# =========================
# ROUTER LOGIC
# =========================
def detect_modalities(query: str):
    q = query.lower()

    use_visual = any(k in q for k in VISUAL_KEYWORDS)
    use_temporal = any(k in q for k in TEMPORAL_KEYWORDS)

    # text is always available (dialogue, captions, KG)
    use_text = True

    return {
        "use_text": use_text,
        "use_visual": use_visual,
        "use_temporal": use_temporal
    }


def normalize_query(query: str):
    """
    Light cleanup so downstream embedders are stable.
    """
    query = query.strip()
    query = re.sub(r"\s+", " ", query)
    return query


def split_query(query: str):
    """
    Split into text-semantic and visual-semantic components.
    For now, we keep them identical but explicit.
    """
    return {
        "text_query": query,
        "visual_query": query
    }


def phase5_route_query(user_query: str):
    user_query = normalize_query(user_query)

    modalities = detect_modalities(user_query)
    queries = split_query(user_query)

    payload = {
        "original_query": user_query,
        "text_query": queries["text_query"],
        "visual_query": queries["visual_query"],
        "use_text": modalities["use_text"],
        "use_visual": modalities["use_visual"],
        "use_temporal": modalities["use_temporal"]
    }

    return payload


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="User natural language query")
    parser.add_argument("--out", default="processed_data/query_plan.json")
    args = parser.parse_args()

    plan = phase5_route_query(args.query)

    with open(args.out, "w") as f:
        json.dump(plan, f, indent=2)

    print("[OK] Phase 5 routing complete")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
