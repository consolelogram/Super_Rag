Super RAG

A Modular Multi-Phase Retrieval-Augmented Generation (RAG) Engine
Built for multimodal reasoning, hybrid retrieval, and structured answer synthesis.

Overview

Super RAG is a fully modular Retrieval-Augmented Generation system that combines:

Text Retrieval

Knowledge Graph Reasoning

Vector Database Search

Visual Retrieval

Speech-to-Text Processing

Reranking & Answer Synthesis

Unlike traditional RAG systems that follow a simple embed → retrieve → generate flow, Super RAG introduces a structured, multi-layer pipeline designed for deeper reasoning and reduced hallucination.

Architecture
Input (Text / Audio / Visual)
        ↓
Phase 2: Perception Layer
    - Speech to Text
    - Vision Language Processing
        ↓
Phase 3: Knowledge Graph Construction
        ↓
Phase 4: Vector & Visual Retrieval
        ↓
Phase 5–7: Hybrid Retrieval Engine
        ↓
Phase 8: Reranking
        ↓
Phase 9: Answer Synthesis
Project Structure
Super_Rag/
│
├── app.py
├── app4.py
│
├── phase2a_stt.py
├── phase2b_vlm.py
│
├── phase3_kg.py
│
├── phase4_vector_db.py
├── phase4_visual_db.py
│
├── phase5_rag_engine.py
├── phase6_text_kg_retrieval.py
├── phase7_visual_retrieval.py
│
├── phase8_rerank.py
├── phase9_answer_synthesis.py
│
└── splicer.py

Each phase is modular and can be executed independently.

Features

Modular architecture

Multimodal input support

Knowledge graph integration

Hybrid text + structured retrieval

Reranking for improved precision

Structured answer synthesis

Easily extendable

Installation
1. Clone Repository
git clone https://github.com/consolelogram/Super_Rag.git
cd Super_Rag
2. Create Virtual Environment
python -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt

If requirements.txt is missing:

pip freeze > requirements.txt
Environment Configuration

Create a .env file in the root directory:

OPENAI_API_KEY=your_api_key
VECTOR_DB_URL=your_vector_database_url
KG_ENDPOINT=your_knowledge_graph_endpoint

Add any additional API keys required for speech or vision models.

Running the System
Run Main Application
python app.py

or

python app4.py
Running Individual Phases
Speech-to-Text
python phase2a_stt.py --input audio.wav
Knowledge Graph Construction
python phase3_kg.py --input text.txt
Vector Retrieval
python phase4_vector_db.py --query "Explain Super RAG"
Reranking
python phase8_rerank.py
Final Answer Synthesis
python phase9_answer_synthesis.py
Core Concepts
1. Multimodal Perception

Processes text, audio, and visual inputs.

2. Knowledge Graph Reasoning

Extracts entities and relationships for structured retrieval.

3. Semantic Vector Search

Uses embeddings for contextual similarity search.

4. Hybrid Retrieval

Combines:

Vector results

Knowledge graph results

Visual retrieval results

5. Reranking

Improves precision using scoring and cross-encoder logic.

6. Answer Synthesis

Generates structured, grounded responses using retrieved evidence.

Use Cases

Enterprise knowledge assistants

Research document reasoning

Multimodal AI systems

Hackathon demos

Advanced RAG experimentation

Video or visual RAG extensions

Extending the Project

You can:

Integrate FAISS, Pinecone, or Weaviate

gtihub readme

Here is a clean, professional GitHub-ready README.md formatted properly for GitHub rendering:

🚀 Super RAG

A Modular, Multi-Phase Retrieval-Augmented Generation (RAG) Engine

Super RAG is a structured, multi-layer RAG system that combines semantic search, knowledge graphs, multimodal processing, reranking, and answer synthesis into one extensible pipeline.

Unlike traditional RAG systems that follow a simple:

Embed → Retrieve → Generate

Super RAG introduces a multi-phase reasoning architecture:

Perception → Knowledge Structuring → Hybrid Retrieval → Reranking → Answer Synthesis
📌 Features

🧠 Modular multi-phase architecture

🔎 Vector database retrieval

🌐 Knowledge graph construction & traversal

🎙 Speech-to-text support

🖼 Vision-language processing

🏆 Reranking for higher precision

📚 Structured answer synthesis

🔧 Easily extensible

🏗 Architecture
Input (Text / Audio / Visual)
        ↓
Phase 2: Perception Layer
    - Speech to Text
    - Vision Language Model
        ↓
Phase 3: Knowledge Graph Construction
        ↓
Phase 4: Vector & Visual Retrieval
        ↓
Phase 5–7: Hybrid Retrieval Engine
        ↓
Phase 8: Reranking
        ↓
Phase 9: Answer Synthesis
📂 Project Structure
Super_Rag/
│
├── app.py
├── app4.py
│
├── phase2a_stt.py
├── phase2b_vlm.py
│
├── phase3_kg.py
│
├── phase4_vector_db.py
├── phase4_visual_db.py
│
├── phase5_rag_engine.py
├── phase6_text_kg_retrieval.py
├── phase7_visual_retrieval.py
│
├── phase8_rerank.py
├── phase9_answer_synthesis.py
│
└── splicer.py

Each phase is independently runnable and modular for experimentation.

⚙️ Installation
1️⃣ Clone the Repository
git clone https://github.com/consolelogram/Super_Rag.git
cd Super_Rag
2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt

If requirements.txt does not exist:

pip freeze > requirements.txt
🔐 Environment Setup

Create a .env file in the root directory:

OPENAI_API_KEY=your_api_key
VECTOR_DB_URL=your_vector_db_url
KG_ENDPOINT=your_kg_endpoint

Add any additional API keys required for speech or vision APIs.

▶️ Running the System
Run Full Application
python app.py

or

python app4.py
🧪 Running Individual Phases
Speech-to-Text
python phase2a_stt.py --input audio.wav
Knowledge Graph Construction
python phase3_kg.py --input text.txt
Vector Retrieval
python phase4_vector_db.py --query "Explain Super RAG"
Reranking
python phase8_rerank.py
Answer Synthesis
python phase9_answer_synthesis.py
🧠 Core Concepts
Multimodal Perception

Processes text, audio, and visual data.

Knowledge Graph Reasoning

Extracts entities and relationships for structured retrieval.

Semantic Search

Uses embeddings to retrieve contextually similar data.

Hybrid Retrieval

Combines vector search + knowledge graph + visual retrieval.

Reranking

Improves answer quality using scoring and filtering.

Answer Synthesis

Generates grounded, structured responses from retrieved evidence.

🚀 Use Cases

Enterprise knowledge assistants

Multimodal AI systems

Research document reasoning

Hackathon prototypes

Advanced RAG experimentation

🔧 Extending Super RAG

You can easily:

Replace vector DB with FAISS, Pinecone, or Weaviate

Integrate Neo4j for graph storage

Add local LLMs (LLaMA, Mistral, etc.)

Add streaming or agent-based reasoning

Each phase is isolated to support experimentation and research.

🤝 Contributing

Fork the repository

Create a new feature branch

Commit changes

Open a pull request

Please ensure:

Clean modular code

No hardcoded API keys

Updated documentation
