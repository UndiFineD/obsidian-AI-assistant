from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

class EmbeddingManager:
    def __init__(self, db_path="vector_db"):
        self.client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=db_path))
        self.collection = self.client.get_or_create_collection(name="notes")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def compute_embedding(self, text: str):
        return self.model.encode(text).tolist()

    def add_embedding(self, text: str, note_path: str):
        vec = self.compute_embedding(text)
        self.collection.upsert([{
            "id": note_path,
            "embedding": vec,
            "metadata": {"note_path": note_path}
        }])

    def search(self, query: str, top_k: int = 5):
        query_vec = self.compute_embedding(query)
        results = self.collection.query(query_vec, n_results=top_k)
        return results["results"][0]["ids"]

    def get_embedding_text(self, note_path: str):
        results = self.collection.query(ids=[note_path])
        if results["results"][0]["embeddings"]:
            return results["results"][0]["embeddings"][0]
        return ""

    def reset_db(self):
        self.client.delete_collection("notes")
        self.collection = self.client.get_or_create_collection(name="notes")
        
        