# agent/embeddings.py

import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:
    SentenceTransformer = None  # type: ignore

try:
    from chromadb import PersistentClient  # type: ignore
    from chromadb.utils import embedding_functions  # type: ignore
except Exception:
    PersistentClient = None  # type: ignore
    embedding_functions = None  # type: ignore
from .settings import get_settings
from .utils import safe_call


class EmbeddingsManager:
    """Manages embeddings for vault content using Chroma + SentenceTransformers."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        top_k: int = 5,
        db_path: str = "./agent/vector_db",
        collection_name: str = "obsidian_notes",
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.top_k = top_k
        self.db_path = db_path
        self.collection_name = collection_name
        self.model_name = model_name

        # Load embedding model if available; swallow errors
        if SentenceTransformer is None:
            logging.warning(
                "[EmbeddingsManager] sentence_transformers not available; embeddings disabled"
            )
            self.model = None
        else:
            self.model = safe_call(
                SentenceTransformer,
                model_name,
                error_msg="[EmbeddingsManager] Error loading embedding model",
                default=None,
            )

        # If model failed to load, skip DB initialization to avoid file locks
        if self.model is None:
            self.chroma_client = None
            self.collection = None
            return

        # Initialize persistent Chroma client; swallow errors
        if PersistentClient is None:
            self.chroma_client = None
        else:
            self.chroma_client = safe_call(
                PersistentClient,
                path=self.db_path,
                error_msg="[EmbeddingsManager] Error initializing Chroma client",
                default=None,
            )

        # Create or get collection using the **model name**, not the model object
        if self.chroma_client and embedding_functions is not None:
            try:
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                        model_name
                    ),
                )
            except Exception:
                logging.error("[EmbeddingsManager] Error creating/getting collection")
                self.collection = None
        else:
            self.collection = None

    @classmethod
    def from_settings(cls) -> "EmbeddingsManager":
        """Build an EmbeddingsManager using centralized settings.

        Does not alter the default constructor behavior used by tests; this is
        a convenience for the runtime backend to honor user config without
        changing test expectations.
        """
        s = get_settings()
        # Derive a persistent vector DB path under project root unless the
        # caller later supplies a different location. Keep the collection name
        # stable.
        # Tests expect the vector DB to live under ./agent/vector_db relative to project root
        vector_db_path = str(Path(s.project_root) / "backend" / "vector_db")
        return cls(
            chunk_size=s.chunk_size,
            overlap=s.chunk_overlap,
            top_k=s.top_k,
            db_path=vector_db_path,
            collection_name="obsidian_notes",
            model_name=s.embed_model,
        )

    # ----------------------
    # Core embedding methods
    # ----------------------

    def compute_embedding(self, text: str, timeout: float = 5.0) -> List[float]:
        if self.model is None:
            logging.error("[EmbeddingsManager] No embedding model loaded.")
            return []
        return safe_call(
            lambda t: self.model.encode(t).tolist(),
            text,
            error_msg="[EmbeddingsManager] Error computing embedding",
            default=[],
        )

    def add_embedding(self, text: str, note_path: str):
        vec = self.compute_embedding(text)
        if self.collection is None:
            logging.error("[EmbeddingsManager] No collection available for upsert.")
            return
        # Use the standard ChromaDB upsert format for efficiency and correctness.
        safe_call(
            lambda: self.collection.upsert(
                ids=[note_path],
                embeddings=[vec],
                metadatas=[
                    {"note_path": note_path, "source": os.path.basename(note_path)}
                ],
            ),
            error_msg="[EmbeddingsManager] Error upserting embedding",
        )

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        if top_k is None:
            top_k = self.top_k
        query_vec = self.compute_embedding(query)
        if self.collection is None:
            logging.error("[EmbeddingsManager] No collection available for search.")
            return []

        def do_search():
            results = self.collection.query(
                query_embeddings=[query_vec], n_results=top_k
            )
            hits = []
            for doc, meta in zip(
                results["documents"][0], results["metadatas"][0], strict=True
            ):
                hits.append({"text": doc, "source": meta.get("note_path", "")})
            return hits

        return safe_call(
            do_search, error_msg="[EmbeddingsManager] Error during search", default=[]
        )

    def get_embedding_by_id(self, note_id: str) -> List[float]:
        """Retrieve an embedding vector by its ID (note_path)."""
        if self.collection is None:
            logging.error(
                "[EmbeddingsManager] No collection available for get_embedding_by_id."
            )
            return []

        def do_get():
            results = self.collection.get(ids=[note_id], include=["embeddings"])
            # The 'get' method returns a list of embeddings, one for each ID.
            # If the ID is found, the list will contain one item.
            if results and results["embeddings"]:
                return results["embeddings"][0]
            return []

        return safe_call(
            do_get,
            error_msg=f"[EmbeddingsManager] Error getting embedding for id {note_id}",
            default=[],
        )

    def reset_db(self):
        if self.chroma_client is None:
            logging.error(
                "[EmbeddingsManager] No Chroma client available for reset_db."
            )
            return

        def do_reset():
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    self.model_name
                ),
            )

        safe_call(do_reset, error_msg="[EmbeddingsManager] Error resetting DB")

    def clear_collection(self):
        """Alias for reset_db to maintain backward compatibility with tests."""
        self.reset_db()

    def add_documents(self, chunks: List[str], metadatas: Optional[List[Dict]] = None):
        """Add multiple document chunks to the collection.

        Expected by tests and indexing workflows for batch document insertion.
        """
        if not chunks or self.collection is None:
            return

        # Generate IDs for chunks
        ids = [self._hash_text(chunk) for chunk in chunks]
        # Use provided metadata or generate basic metadata
        final_metadatas = (
            metadatas
            if metadatas is not None
            else [{"chunk_index": i} for i in range(len(chunks))]
        )

        def do_add():
            self.collection.add(documents=chunks, ids=ids, metadatas=final_metadatas)

        safe_call(do_add, error_msg="[EmbeddingsManager] Error adding documents")

    def close(self):
        """Attempt to release any resources held by the Chroma client.

        Chroma's PersistentClient does not expose an explicit close, but clearing
        references may help Windows file lock issues in tests.
        """
        try:
            # Best-effort cleanup
            self.collection = None
            self.chroma_client = None
            self.model = None
        except Exception as e:
            import logging

            logging.warning(f"Failed to set model to None: {e}")

    # ----------------------
    # Utilities
    # ----------------------

    def get_collection_info(self) -> Dict[str, Optional[object]]:
        """Return basic info about the current collection.

        Includes collection name, total document count, and model name.
        Safe for cases where the collection is None.
        """
        count = 0
        if self.collection is not None:
            count = safe_call(
                self.collection.count,
                error_msg="[EmbeddingsManager] Error getting collection count",
                default=0,
            )
        return {
            "name": self.collection_name,
            "count": count,
            "model": self.model_name,
        }

    def _hash_text(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8"), usedforsecurity=False).hexdigest()

    def chunk_text(self, text: str) -> List[str]:
        if not text:
            return []
        words = text.split()
        step = self.chunk_size - self.overlap
        return [
            " ".join(words[i : i + self.chunk_size]) for i in range(0, len(words), step)
        ]

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
            metadatas=[{"note_path": file_path} for _ in chunks],
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
