from sentence_transformers import SentenceTransformer
import chromadb

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ NEW Chroma client (FIXED)
client = chromadb.PersistentClient(path="./chromadb")

collection = client.get_collection(name="climate_guides")

def retrieve(query, top_k=3):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    return list(zip(documents, metadatas))
