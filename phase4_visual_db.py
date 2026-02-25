import os
import cv2
import torch
from PIL import Image
import chromadb
from transformers import CLIPProcessor, CLIPModel

def build_visual_embeddings():
    """Extracts frames from clips and embeds them into ChromaDB using CLIP."""
    clips_dir = os.path.join("processed_data", "clips")
    db_dir = os.path.join("processed_data", "chroma_db")
    
    print("Loading CLIP model (this will download weights the first time)...")
    model_id = "openai/clip-vit-base-patch32"
    processor = CLIPProcessor.from_pretrained(model_id)
    model = CLIPModel.from_pretrained(model_id)
    
    # Connect to your existing local Chroma database
    client = chromadb.PersistentClient(path=db_dir)
    
    # We create a separate collection purely for visual vectors
    collection = client.get_or_create_collection(name="visual_embeddings")
    
    clips = sorted([f for f in os.listdir(clips_dir) if f.endswith(".mp4")])
    if not clips:
        print(f"No clips found in {clips_dir}.")
        return

    embeddings = []
    metadatas = []
    ids = []
    
    print(f"Processing {len(clips)} clips for pure visual embeddings...")
    
    for filename in clips:
        clip_path = os.path.join(clips_dir, filename)
        base_name = filename.replace(".mp4", "")
        
        # Open video and extract the middle frame
        cap = cv2.VideoCapture(clip_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            continue
            
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total_frames / 2))
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print(f"Failed to read frame from {filename}")
            continue
            
        # Convert OpenCV BGR frame to PIL RGB image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        
        # The Hack: Provide dummy text so the CLIP forward pass doesn't crash
        inputs = processor(text=[""], images=pil_image, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            # Explicitly grab the final image embeddings and convert to list
            vector = outputs.image_embeds[0].tolist()
        
        embeddings.append(vector)
        metadatas.append({"clip_name": filename, "type": "pure_visual"})
        ids.append(base_name)
        
    if embeddings:
        collection.upsert(
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully embedded {len(embeddings)} visual frames into ChromaDB!")

def test_visual_search(query_text, n_results=2):
    """Tests the visual embedding space by searching with text."""
    db_dir = os.path.join("processed_data", "chroma_db")
    client = chromadb.PersistentClient(path=db_dir)
    collection = client.get_collection(name="visual_embeddings")
    
    # To search, we must process the text query through the EXACT SAME CLIP model
    model_id = "openai/clip-vit-base-patch32"
    processor = CLIPProcessor.from_pretrained(model_id)
    model = CLIPModel.from_pretrained(model_id)
    
    # The Hack: Create a dummy blank image so the CLIP forward pass doesn't crash
    dummy_image = Image.new('RGB', (224, 224), (0, 0, 0))
    inputs = processor(text=[query_text], images=dummy_image, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        # Explicitly grab the final text embeddings and convert to list
        query_vector = outputs.text_embeds[0].tolist()
    
    print(f"\n--- Testing Pure Visual Search ---")
    print(f"Query: '{query_text}'")
    
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results
    )
    
    for i in range(len(results['ids'][0])):
        clip_id = results['ids'][0][i]
        distance = results['distances'][0][i]
        print(f"Match {i+1}: {clip_id} (Distance/Score: {distance:.4f})")

if __name__ == "__main__":
    build_visual_embeddings()
    
    # Change this text to something visually identifiable in your video!
    test_visual_search("a man standing in a corporate lobby")