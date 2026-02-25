import os
import json
import torch
import networkx as nx
import chromadb
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import ollama

def phase5_query_parsing(raw_query):
    """Phase 5: Reformulates query into declarative text and visual scene."""
    print("\n[Phase 5] Parsing and reformulating queries...")
    
    text_prompt = f"Reformulate this question into a declarative sentence optimized for entity matching. Return ONLY the sentence.\nQuestion: {raw_query}"
    text_response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': text_prompt}])
    q_text = text_response['message']['content'].strip()
    
    vis_prompt = f"Distill this question into a core visual scene description. Describe what it would look like on camera. Return ONLY the scene description.\nQuestion: {raw_query}"
    vis_response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': vis_prompt}])
    q_visual = vis_response['message']['content'].strip()
    
    print(f"  -> Reformulated Text Query: {q_text}")
    print(f"  -> Extracted Visual Scene: {q_visual}")
    return q_text, q_visual

def phase6_text_retrieval(q_text, G, top_k_entities=3):
    """Phase 6: GraphRAG traversal for S^t_q."""
    print("\n[Phase 6] Traversing Knowledge Graph for entity matching...")
    
    # Step 1 & 2: Match query to graph entities using LLM
    nodes_list = list(G.nodes())
    if not nodes_list:
        return []
        
    prompt = f"""
    Given this declarative query: '{q_text}'
    Select the top {top_k_entities} most relevant entities from this list: {nodes_list[:100]}...
    Return ONLY a comma-separated list of the exact entity names.
    """
    response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
    matched_entities = [e.strip() for e in response['message']['content'].split(',')]
    
    # Step 3 & 4: Extract the associated video clips for those nodes
    s_t_q = set()
    for entity in matched_entities:
        if entity in G.nodes:
            clip = G.nodes[entity].get('source_clip')
            if clip:
                s_t_q.add(clip)
                
    print(f"  -> Graph Entities Matched: {matched_entities}")
    print(f"  -> Textual Retrieval Set (S^t_q): {list(s_t_q)}")
    return list(s_t_q)

def phase7_visual_retrieval(q_visual, vis_col, processor, model, top_k=5):
    """Phase 7: Embed-based Visual Retrieval for S^v_q."""
    print("\n[Phase 7] Projecting query into visual feature space...")
    dummy_image = Image.new('RGB', (224, 224), (0, 0, 0))
    inputs = processor(text=[q_visual], images=dummy_image, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        query_vector = outputs.text_embeds[0].tolist()
        
    results = vis_col.query(query_embeddings=[query_vector], n_results=top_k)
    s_v_q = results['ids'][0]
    
    print(f"  -> Visual Retrieval Set (S^v_q): {s_v_q}")
    return s_v_q

def phase8_llm_judge(intersection_clips, raw_query):
    """Phase 8: Binary relevance filtering on intersection."""
    print(f"\n[Phase 8] LLM Judge evaluating {len(intersection_clips)} intersecting clips...")
    final_context = []
    
    meta_dir = os.path.join("processed_data", "metadata")
    
    for clip_id in intersection_clips:
        # Reconstruct V^t_S (Fused Context)
        stt_path = os.path.join(meta_dir, f"{clip_id}_stt.json")
        vlm_path = os.path.join(meta_dir, f"{clip_id}_vlm.json")
        
        context = ""
        if os.path.exists(vlm_path):
            with open(vlm_path, "r") as f: context += json.load(f).get("caption", "") + " | "
        if os.path.exists(stt_path):
            with open(stt_path, "r") as f: context += json.load(f).get("transcript", "")
            
        prompt = f"""
        You are a binary relevance classifier. 
        Determine if this video clip context contains information vital to answering the query.
        Return ONLY '1' if it is relevant, or '0' if it is irrelevant.
        
        Query: {raw_query}
        Context: {context}
        """
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
        decision = response['message']['content'].strip()
        
        if '1' in decision:
            final_context.append(f"[Clip: {clip_id}] {context}")
            print(f"  -> {clip_id}: Passed (1)")
        else:
            print(f"  -> {clip_id}: Failed (0)")
            
    return final_context

def run_strict_pipeline(raw_query):
    # Load Databases
    G = nx.read_graphml(os.path.join("processed_data", "knowledge_graph.graphml"))
    
    client = chromadb.PersistentClient(path=os.path.join("processed_data", "chroma_db"))
    vis_col = client.get_collection(name="visual_embeddings")
    
    model_id = "openai/clip-vit-base-patch32"
    processor = CLIPProcessor.from_pretrained(model_id)
    clip_model = CLIPModel.from_pretrained(model_id)
    
    # Execute Pipeline
    q_text, q_visual = phase5_query_parsing(raw_query)
    s_t_q = phase6_text_retrieval(q_text, G)
    s_v_q = phase7_visual_retrieval(q_visual, vis_col, processor, clip_model)
    
    # Strict Intersection
    intersection = list(set(s_t_q).intersection(set(s_v_q)))
    print(f"\n[Strict Intersection] S^t_q \u2229 S^v_q = {intersection}")
    
    if not intersection:
        return "Strict Mode Halt: The graph traversal and visual search found no overlapping clips."
        
    final_context = phase8_llm_judge(intersection, raw_query)
    
    if not final_context:
        return "Strict Mode Halt: The LLM Judge rejected all overlapping clips as irrelevant (scored 0)."
        
    print("\n[Phase 9] Generating final synthesized response...")
    synth_prompt = f"Answer the query using ONLY this validated context.\nQuery: {raw_query}\nContext: {' '.join(final_context)}"
    response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': synth_prompt}])
    return response['message']['content']

if __name__ == "__main__":
    query = input("\nAsk a question about the video: ")
    answer = run_strict_pipeline(query)
    print("\n--- FINAL ANSWER ---")
    print(answer)