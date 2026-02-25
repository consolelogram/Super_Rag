import os
import json
import chromadb
from chromadb.utils import embedding_functions

def build_vector_db():
    """Fuses multi-modal metadata and embeds it into a local vector database."""
    meta_dir = os.path.join("processed_data", "metadata")
    db_dir = os.path.join("processed_data", "chroma_db")
    
    # Initialize persistent ChromaDB client
    client = chromadb.PersistentClient(path=db_dir)
    
    # Use default sentence-transformer model (downloads automatically, runs locally)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Create or grab the collection
    collection = client.get_or_create_collection(
        name="video_clips",
        embedding_function=sentence_transformer_ef
    )
    
    # Gather all unique clip base names
    files = os.listdir(meta_dir)
    base_names = set([f.replace("_stt.json", "").replace("_vlm.json", "") for f in files if f.endswith(".json")])
    
    documents = []
    metadatas = []
    ids = []
    
    print(f"Found {len(base_names)} clips to embed. Fusing and indexing...")
    
    for base_name in base_names:
        stt_path = os.path.join(meta_dir, f"{base_name}_stt.json")
        vlm_path = os.path.join(meta_dir, f"{base_name}_vlm.json")
        
        transcript = "No dialogue."
        caption = "No visual description."
        
        if os.path.exists(stt_path):
            with open(stt_path, "r") as f:
                transcript = json.load(f).get("transcript", transcript)
                
        if os.path.exists(vlm_path):
            with open(vlm_path, "r") as f:
                caption = json.load(f).get("caption", caption)
                
        # The Fusion: Combine audio and visual context into one dense document
        fused_text = f"Visuals: {caption} | Audio: {transcript}"
        
        documents.append(fused_text)
        metadatas.append({"clip_name": f"{base_name}.mp4", "type": "fused_multimodal"})
        ids.append(base_name)
        
    if documents:
        # Upsert handles both insert and update
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully embedded {len(documents)} clips into ChromaDB!")
    else:
        print("No metadata found to embed.")

def test_search(query_text, n_results=2):
    """A quick test function to prove the database is searchable."""
    db_dir = os.path.join("processed_data", "chroma_db")
    client = chromadb.PersistentClient(path=db_dir)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_collection(name="video_clips", embedding_function=sentence_transformer_ef)
    
    print(f"\n--- Testing Search ---")
    print(f"Query: '{query_text}'")
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    for i in range(len(results['ids'][0])):
        clip_id = results['ids'][0][i]
        distance = results['distances'][0][i]
        text = results['documents'][0][i]
        print(f"\nMatch {i+1}: {clip_id} (Distance/Score: {distance:.4f})")
        print(f"Context: {text}")

if __name__ == "__main__":
    build_vector_db()
    # Edit this string to test searching for something specific that actually happens in your video
    test_search("Describe an event or object you know is in the video")