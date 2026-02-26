import os
import json
import networkx as nx
import re

# =========================================================
# CONFIG
# =========================================================
META_DIR = os.path.join("processed_data", "metadata")
OUT_GRAPH = os.path.join("processed_data", "knowledge_graph.gml")
CLIP_DURATION = 10  # seconds

# =========================================================
# NORMALIZATION
# =========================================================
def normalize_entity(name: str) -> str:
    """
    Normalize entity strings so the graph is stable.
    Minimal on purpose (reviewer-safe).
    """
    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    return name

def event_node_id(clip_name: str) -> str:
    return f"EVENT::{clip_name}"

def entity_node_id(entity_name: str) -> str:
    return f"ENTITY::{entity_name}"

# =========================================================
# MAIN
# =========================================================
def build_knowledge_graph():
    G = nx.DiGraph()

    vlm_files = sorted(
        f for f in os.listdir(META_DIR)
        if f.endswith("_vlm.json")
    )

    previous_event = None

    for idx, fname in enumerate(vlm_files):
        clip_name = fname.replace("_vlm.json", "")
        meta_path = os.path.join(META_DIR, fname)

        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ---------------- EVENT NODE ----------------
        start_time = idx * CLIP_DURATION
        end_time = start_time + CLIP_DURATION

        event_id = event_node_id(clip_name)

        G.add_node(
            event_id,
            type="event",
            clip=clip_name,
            start_time=start_time,
            end_time=end_time,
            temporal_phases=data.get("temporal_phases", {}),
            actions=data.get("actions", [])
        )

        # ---------------- TEMPORAL EDGE ----------------
        if previous_event is not None:
            G.add_edge(
                previous_event,
                event_id,
                relation="HAPPENS_BEFORE"
            )

        previous_event = event_id

        # ---------------- ENTITY PROMOTION ----------------
        raw_entities = data.get("entities", [])

        for raw_ent in raw_entities:
            ent = normalize_entity(raw_ent)

            if not ent:
                continue

            ent_id = entity_node_id(ent)

            if not G.has_node(ent_id):
                G.add_node(
                    ent_id,
                    type="entity",
                    name=ent
                )

            G.add_edge(
                event_id,
                ent_id,
                relation="HAS_ENTITY"
            )

    return G

# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":
    graph = build_knowledge_graph()
    nx.write_gml(graph, OUT_GRAPH)
    print(f"[OK] Knowledge graph rebuilt → {OUT_GRAPH}")
