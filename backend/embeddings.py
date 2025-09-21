
import os
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

import chromadb
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from sentence_transformers import SentenceTransformer

# Optional FAISS fallback
try:
    import faiss
except ImportError:
    faiss = None

class EmbeddingManager:
     def __init__(
        self,
        db_path: str = "vector_db",
        collection_name: str = "obsidian_notes",
        model_name: str = "all-MiniLM-L6-v2"
        chunk_size: int = 500,
        overlap: int = 50,
        top_k: int = 5,
        chroma_db_impl: str = "duckdb+parquet"
    ):
        """
        Embeddings Manager for vault content.
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.top_k = top_k
        self.chroma_db_impl = chroma_db_impl
        
        client = Client(Settings(self.chroma_db_impl, 
            persist_directory=self.db_path))

        # Load embedding model
        self.model = SentenceTransformer(model_name)

        # Try Chroma first
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=db_path,
            anonymized_telemetry=False
        ))

        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name)
        )
        
        
    def compute_embedding(self, text: str):
        return self.model.encode(text).tolist()

    def add_embedding(self, text: str, note_path: str):
        vec = self.compute_embedding(text)
        self.collection.upsert([{
            "id": note_path,
            "embedding": vec,
            "metadata": {"note_path": note_path}
        }])

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Retrieve top-k results for a query."""
        if top_k is None:
            top_k = self.top_k
        query_vec = self.compute_embedding(query)
        results = self.collection.query(query_vec, n_results=top_k)
        hits = []
        for doc, meta in zip(
            results["documents"][0], 
            results["metadatas"][0]):
            hits.append({"text": doc, "source": meta["source"]})
        return results["results"][0]["ids"]

    def get_embedding_text(self, note_path: str):
        results = self.collection.query(ids=[note_path])
        if results["results"][0]["embeddings"]:
            return results["results"][0]["embeddings"][0]
        return ""

    def reset_db(self):
        self.client.delete_collection("notes")
        self.collection = self.client.get_or_create_collection(name="notes")
        
    def _hash_text(self, text: str) -> str:
        """Generate unique ID for a text chunk."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()
        
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += self.chunk_size - self.overlap
        return chunks
    
    def index_file(self, file_path: str) -> int:
        """Index a single file into the DB."""
        if not os.path.exists(file_path):
            return 0
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = self.chunk_text(text)
        ids = [f"{os.path.basename(file_path)}-{i}" for i in range(len(chunks))]

        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=[{"source": file_path} for _ in chunks],
        )
        self.chroma_client.persist()
        return len(chunks)
    
    def index_vault(self, vault_path: str) -> Dict[str, int]:
        """Index all .md files in a vault directory."""
        vault = Path(vault_path)
        results = {}
        for md_file in vault.rglob("*.md"):
            count = self.index_file(str(md_file))
            results[str(md_file)] = count
        return results
        
    def reindex(self, vault_path: str) -> Dict[str, int]:
        """Drop and rebuild DB from scratch."""
        self.chroma_client.delete_collection(self.collection_name)
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(self.model)
        )
        return self.index_vault(vault_path)
        