import os
import json
import networkx as nx
from pyvis.network import Network
import ollama

def extract_entities_and_relations(text):
    """Uses a local LLM to extract nodes and edges from text with strict JSON schema."""
    # Updated prompt to force a top-level dictionary, which local LLMs handle much better
    prompt = f"""
    Analyze the following video clip description. Extract key entities (people, objects, concepts) and their relationships.
    You must reply with ONLY a valid JSON object matching this exact format:
    {{
        "triplets": [
            {{"node_1": "Entity A", "edge": "relationship", "node_2": "Entity B"}}
        ]
    }}
    
    Text: {text}
    """
    
    try:
        response = ollama.chat(
            model='llama3.2', # Make sure this matches the model you successfully pulled
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        
        content = response['message']['content']
        data = json.loads(content)
        
        # Safely extract the list from the dictionary
        if "triplets" in data:
            return data["triplets"]
        else:
            print(f"  -> Skipped: LLM didn't return 'triplets'. Raw output: {content}")
            return []
            
    except Exception as e:
        print(f"  -> Extraction failed. Error: {e}")
        return []

def build_knowledge_graph():
    """Reads metadata, extracts entities, and builds an interactive HTML graph."""
    meta_dir = os.path.join("processed_data", "metadata")
    files = os.listdir(meta_dir)
    base_names = sorted(list(set([f.replace("_stt.json", "").replace("_vlm.json", "") for f in files if f.endswith(".json")])))
    
    # Initialize a directed graph
    G = nx.DiGraph()
    
    print(f"Building Knowledge Graph from {len(base_names)} clips...")
    
    for base_name in base_names:
        stt_path = os.path.join(meta_dir, f"{base_name}_stt.json")
        vlm_path = os.path.join(meta_dir, f"{base_name}_vlm.json")
        
        transcript = ""
        caption = ""
        
        if os.path.exists(stt_path):
            with open(stt_path, "r") as f:
                transcript = json.load(f).get("transcript", "")
                
        if os.path.exists(vlm_path):
            with open(vlm_path, "r") as f:
                caption = json.load(f).get("caption", "")
                
        fused_text = f"{caption} {transcript}".strip()
        
        if not fused_text or fused_text == "No dialogue.":
            continue
            
        print(f"Extracting entities from {base_name}...")
        triplets = extract_entities_and_relations(fused_text)
        
# Add nodes and edges to the NetworkX graph safely
        for triplet in triplets:
            # Ensure the keys exist AND their values are actual strings (not None/null)
            if triplet.get("node_1") and triplet.get("node_2") and triplet.get("edge"):
                n1 = str(triplet["node_1"]).strip().title()
                n2 = str(triplet["node_2"]).strip().title()
                edge = str(triplet["edge"]).strip().lower()
                
                # Add nodes with the clip origin as a property
                G.add_node(n1, source_clip=base_name)
                G.add_node(n2, source_clip=base_name)
                G.add_edge(n1, n2, title=edge, label=edge)
            else:
                print(f"  -> Skipped invalid triplet: {triplet}")

    # Export to PyVis for the flashy interactive HTML file
    print(f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    net.from_nx(G)
    
    # Add some physics settings to make it bouncy and cool for the demo
    net.repulsion(node_distance=150, central_gravity=0.1, spring_length=100, spring_strength=0.05)
    
    output_path = os.path.join("processed_data", "knowledge_graph.html")
    nx.write_graphml(G, os.path.join("processed_data", "knowledge_graph.graphml"))
    net.write_html(output_path)
    print(f"Interactive graph saved to: {output_path}")

if __name__ == "__main__":
    build_knowledge_graph()