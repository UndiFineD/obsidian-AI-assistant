# backend/embeddings.py
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

from sentence_transformers import SentenceTransformer

from chromadb import PersistentClient
from chromadb.utils import embedding_functions


class EmbeddingsManager:
    """Manages embeddings for vault content using Chroma + SentenceTransformers."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        top_k: int = 5,
        db_path: str = "./vector_db",
        collection_name: str = "obsidian_notes",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.top_k = top_k
        self.db_path = db_path
        self.collection_name = collection_name
        self.model_name = model_name

        # Load embedding model
        self.model = SentenceTransformer(model_name)

        # Initialize persistent Chroma client
        self.chroma_client = PersistentClient(path=self.db_path)

        # Create or get collection using the **model name**, not the model object
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name)
        )

    # ----------------------
    # Core embedding methods
    # ----------------------

    def compute_embedding(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def add_embedding(self, text: str, note_path: str):
        vec = self.compute_embedding(text)
        self.collection.upsert([{
            "id": note_path,
            "embedding": vec,
            "metadata": {"note_path": note_path}
        }])

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        if top_k is None:
            top_k = self.top_k
        query_vec = self.compute_embedding(query)
        results = self.collection.query(query_embeddings=[query_vec], n_results=top_k)
        hits = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            hits.append({"text": doc, "source": meta.get("note_path", "")})
        return hits

    def get_embedding_text(self, note_path: str) -> str:
        results = self.collection.query(ids=[note_path])
        embeddings = results["embeddings"][0]
        if embeddings:
            return embeddings[0]
        return ""

    def reset_db(self):
        self.chroma_client.delete_collection(self.collection_name)
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(self.model_name)
        )

    # ----------------------
    # Utilities
    # ----------------------

    def _hash_text(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def chunk_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunks.append(" ".join(words[start:end]))
            start += self.chunk_size - self.overlap
        return chunks

    # ----------------------
    # Indexing helpers
    # ----------------------

    def index_file(self, file_path: str) -> int:
        if not os.path.exists(file_path):
            return 0
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = self.chunk_text(text)
        ids = [f"{os.path.basename(file_path)}-{i}" for i in range(len(chunks))]
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=[{"note_path": file_path} for _ in chunks]
        )
        self.chroma_client.persist()
        return len(chunks)

    def index_vault(self, vault_path: str) -> Dict[str, int]:
        vault = Path(vault_path)
        results = {}
        for md_file in vault.rglob("*.md"):
            results[str(md_file)] = self.index_file(str(md_file))
        return results

    def reindex(self, vault_path: str) -> Dict[str, int]:
        self.reset_db()
        return self.index_vault(vault_path)
