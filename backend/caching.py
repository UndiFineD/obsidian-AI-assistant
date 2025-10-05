import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

class CacheManager:
    """
    Simple QA cache: question -> answer.
    Compatible with your existing code, but now with optional TTL.
    """
    def __init__(self, cache_dir: str = "./cache", ttl: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "answers.json"
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}

        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def get_cached_answer(self, question: str) -> Optional[str]:
        entry = self.cache.get(question)
        if not entry:
            return None
        if "timestamp" in entry and time.time() - entry["timestamp"] > self.ttl:
            return None
        return entry["answer"]

    def store_answer(self, question: str, answer: str):
        self.cache[question] = {"answer": answer, "timestamp": time.time()}
        with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)


class EmbeddingCache:
    """
    Cache for embeddings: text -> embedding vector.
    Prevents recomputing embeddings for the same text chunks.
    """
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_file = Path(cache_dir) / "embeddings.json"
        self.data: Dict[str, list] = {}

        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

    def _hash_key(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def get_or_compute(self, text: str, embed_fn) -> list:
        key = self._hash_key(text)
        if key in self.data:
            return self.data[key]
        embedding = embed_fn(text)
        self.data[key] = embedding
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f)
        return embedding


class FileHashCache:
    """
    Cache for file hashes: used to skip re-indexing unchanged files.
    Supports .md, .pdf, and any other file type.
    """
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_file = Path(cache_dir) / "filehashes.json"
        self.data: Dict[str, str] = {}

        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

    def _hash_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def is_changed(self, path: Path) -> bool:
        new_hash = self._hash_file(path)
        old_hash = self.data.get(str(path))
        if new_hash != old_hash:
            self.data[str(path)] = new_hash
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f)
            return True
        return False
