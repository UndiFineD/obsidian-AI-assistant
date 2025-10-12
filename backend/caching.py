import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional
from .utils import safe_call


class CacheManager:
    """
    Simple QA cache: question -> answer.
    Compatible with your existing code, but now with optional TTL.
    """

    def __init__(self, cache_dir: str = "./backend/cache", ttl: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "answers.json"
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}

        if self.cache_file.exists():

            def do_load():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)

            self.cache = safe_call(
                do_load, error_msg="[CacheManager] Error loading cache file", default={}
            )

    def _hash_question(self, question: str) -> str:
        """Create a consistent hash for a question string."""
        return hashlib.sha256(question.encode("utf-8")).hexdigest()

    def get_cached_answer(self, question: str, timeout: float = 2.0) -> Optional[str]:
        if question is None:
            return None
        key = self._hash_question(question)
        entry = self.cache.get(key)
        if not entry:
            return None
        if "timestamp" in entry and time.time() - entry["timestamp"] > self.ttl:
            return None
        return entry.get("answer")

    def store_answer(self, question: str, answer: str, timeout: float = 2.0):
        key = self._hash_question(question)
        self.cache[key] = {"answer": answer, "timestamp": time.time()}

        def do_store():
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)

        safe_call(do_store, error_msg="[CacheManager] Error writing cache")


class EmbeddingCache:
    """
    Cache for embeddings: text -> embedding vector.
    Prevents recomputing embeddings for the same text chunks.
    """

    def __init__(self, cache_dir: str = "./backend/cache"):
        self.cache_file = Path(cache_dir) / "embeddings.json"
        self.data: Dict[str, list] = {}

        if self.cache_file.exists():

            def do_load():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)

            self.data = safe_call(
                do_load,
                error_msg="[EmbeddingCache] Error loading cache file",
                default={},
            )

    def _hash_key(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def get_or_compute(self, text: str, embed_fn) -> list:
        key = self._hash_key(text)
        if key in self.data:
            return self.data[key]
        embedding = safe_call(
            embed_fn,
            text,
            error_msg="[EmbeddingCache] Error computing embedding",
            default=[],
        )
        self.data[key] = embedding

        def do_store():
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f)

        safe_call(do_store, error_msg="[EmbeddingCache] Error writing cache")
        return embedding


class FileHashCache:
    """
    Cache for file hashes: used to skip re-indexing unchanged files.
    Supports .md, .pdf, and any other file type.
    """

    def __init__(self, cache_dir: str = "./backend/cache"):
        self.cache_file = Path(cache_dir) / "filehashes.json"
        self.data: Dict[str, str] = {}

        if self.cache_file.exists():

            def do_load():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)

            self.data = safe_call(
                do_load,
                error_msg="[FileHashCache] Error loading cache file",
                default={},
            )

    def _hash_file(self, path: Path) -> str:
        def do_hash():
            if not path.is_file():
                return ""
            h = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()

        return safe_call(
            do_hash, error_msg=f"[FileHashCache] Error hashing file {path}", default=""
        )

    def is_changed(self, path: Path) -> bool:
        new_hash = self._hash_file(path)
        old_hash = self.data.get(str(path))
        if new_hash != old_hash:
            self.data[str(path)] = new_hash

            def do_store():
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(self.data, f)

            safe_call(do_store, error_msg="[FileHashCache] Error writing cache")
            return True
        return False
