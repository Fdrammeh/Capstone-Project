"""
Capstone Backend — RAG Pipeline 
=============================================
Implement retrieval (ChromaDB) and generation (Ollama or an API-based LLM)
here, then call these functions from your /ask (or equivalent) endpoint
in main.py.

Required:
    - Document ingestion: load ./docs, chunk, embed, store in ChromaDB
    - Retrieval: query ChromaDB, return top-N chunks with sources/distances
    - Generation: build a grounded prompt from retrieved context, call the LLM
    - At least one guardrail (confidence threshold, "I don't know" fallback,
      or similar) — see Module 9 grading rubric, "AI Integration"

TODO: implement ingest_documents(), retrieve(), and generate_answer().
"""

# TODO: import chromadb, requests (for Ollama), etc.

# TODO: def ingest_documents(docs_dir: str) -> int: ...
# TODO: def retrieve(question: str, n_results: int = 3) -> list: ...
# TODO: def generate_answer(question: str, context_chunks: list) -> str: ...


import os
import requests
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:1b")

# Find the main TravelWise project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Folder containing the travel documents
DOCS_DIR = PROJECT_DIR / "docs"

# Persistent ChromaDB storage folder
CHROMA_DIR = PROJECT_DIR / "chroma_data"

# Create the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to persistent ChromaDB storage
client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

# Create or connect to our travel collection
collection = client.get_or_create_collection(
    name="travel_documents"
)


def ingest_documents(docs_dir: str = None) -> int:
    """Load, chunk, embed, and store travel documents in ChromaDB."""

    documents = []
    metadatas = []
    ids = []

    # Use the supplied folder, or the project's docs folder by default.
    docs_path = Path(docs_dir) if docs_dir else DOCS_DIR

    if not docs_path.is_absolute():
        docs_path = PROJECT_DIR / docs_path

    for file_path in docs_path.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        chunk_size = 500
        overlap = 100
        start = 0
        chunk_number = 0

        while start < len(text):
            chunk = text[start:start + chunk_size]

            if chunk.strip():
                documents.append(chunk)
                metadatas.append({"source": file_path.name})
                ids.append(f"{file_path.stem}_{chunk_number}")

            start += chunk_size - overlap
            chunk_number += 1

    if not documents:
        return 0

    embeddings = embedding_model.encode(documents).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    return len(documents)



def retrieve(question: str, n_results: int = 3) -> list:
    """Return the most relevant chunks with sources and distances."""

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    question_embedding = embedding_model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=min(n_results, total_chunks),
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):
        chunks.append({
            "text": document,
            "source": (metadata or {}).get("source", "unknown"),
            "distance": distance,
        })

    return chunks


def generate_answer(question: str, context_chunks: list) -> str:
    """Generate a grounded answer using Ollama and retrieved chunks."""

    if not context_chunks:
        return "I could not find relevant information in the travel documents."

    context = "\n\n".join(
        chunk["text"] for chunk in context_chunks
    )

    prompt = f"""
You are TravelWise, a reliable travel assistant.

Answer the user's question using only the facts in the travel information below.

Follow these rules:
1. Answer every part of the question that the documents support.
2. Use attraction names exactly as written in the documents. Do not rename or invent attractions.
3. Use short headings and bullet points when answering questions about multiple topics.
4. Do not repeat attractions or transportation options.
5. Do not say information is missing when the documents already answer that part of the question.
6. If a specific detail is missing, identify only that detail. Still provide all relevant information that is available.
7. Do not use outside knowledge or invent facts.
8. Keep the answer clear, concise, and helpful. 
9. For questions about attractions, organize the answer into categories such as museums and cultural attractions, landmarks, and outdoor attractions when the context supports them. Include the relevant named attractions found in the provided context. Do not invent attraction names or details.


Travel information:
{context}

User question:
{question}

Answer:

"""

    
    try:
        response = requests.post(
            f"{OLLAMA_URL.rstrip('/')}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        return response.json()["response"].strip()

    except requests.exceptions.Timeout:
        return "The travel assistant took too long to respond. Please try again later."

    except requests.exceptions.RequestException:
        return "The travel assistant is temporarily unavailable. Please try again later."

    except (KeyError, ValueError):
        return "The travel assistant returned an invalid response. Please try again later."




def ask_travel_question(question: str):
    """Retrieve relevant travel information and return an answer with sources."""

    question_lower = question.lower()
    cities = ["chicago", "milwaukee", "minneapolis"]
    city = next((name for name in cities if name in question_lower), None)

    # Step 1: Retrieve relevant document chunks
    if (
        city
        and "attraction" in question_lower
        and "transport" in question_lower
    ):
        attraction_chunks = retrieve(
            f"{city} museums, cultural attractions, landmarks, parks, and tourist attractions",
            n_results=4,
        )

        transportation_chunks = retrieve(
            f"{city} public transportation, buses, light rail, transit, and transportation options",
            n_results=4,
        )

        combined_chunks = attraction_chunks + transportation_chunks

        # Remove duplicate chunks
        seen = set()
        chunks = []

        for chunk in combined_chunks:
            key = (chunk["source"], chunk["text"])

            if key not in seen:
                seen.add(key)
                chunks.append(chunk)

        chunks.sort(key=lambda chunk: chunk["distance"])

    else:
        chunks = retrieve(question, n_results=8)

    if not chunks:
        return {
            "answer": "I could not find relevant information in the travel documents.",
            "sources": []
        }

    # Step 2: Apply the relevance guardrail
    max_distance = float(os.getenv("MAX_DISTANCE", "1.0"))

    if chunks[0]["distance"] > max_distance:
        return {
            "answer": "I don't have enough relevant information in my travel documents to answer that question.",
            "sources": []
        }

    # Step 3: Generate the answer
    answer = generate_answer(question, chunks)

    # Step 4: Collect source filenames
    sources = sorted({
        chunk["source"]
        for chunk in chunks
        if chunk["source"] != "unknown"
    })

    return {
        "answer": answer,
        "sources": sources
    }
