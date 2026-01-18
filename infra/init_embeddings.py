import os
from sentence_transformers import SentenceTransformer
import chromadb

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
KB_DIR = os.path.join(BASE_DIR, "data", "kb")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ NEW Chroma client (FIXED)
client = chromadb.PersistentClient(path="./chromadb")

# Create / load collection
collection = client.get_or_create_collection(name="climate_guides")

def chunk_text(text, size=600, overlap=100):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += size - overlap
    return chunks

# Read KB files and create embeddings
for file in os.listdir(KB_DIR):
    if file.endswith(".txt"):
        with open(os.path.join(KB_DIR, file), "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()
            collection.add(
                ids=[f"{file}_{idx}"],
                documents=[chunk],
                metadatas=[{"source": file}],
                embeddings=[embedding]
            )

print("✅ RAG embeddings created successfully")
