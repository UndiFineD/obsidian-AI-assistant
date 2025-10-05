# backend/indexing.py
import os
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
import requests
from readability import Document
from PyPDF2 import PdfReader
from .utils import safe_call

try:
    from .embeddings import EmbeddingsManager
except ImportError:
    # Fallback for testing when importing as top-level module
    try:
        from embeddings import EmbeddingsManager
    except ImportError:
        # During testing, we'll mock this
        EmbeddingsManager = None


class VaultIndexer:
    """Indexes Markdown, PDF, and web content into embeddings DB."""

    def __init__(self, emb_mgr: Optional[EmbeddingsManager] = None, cache_dir: str = "cache"):
        self.emb_mgr = emb_mgr or EmbeddingsManager()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # -------------------
    # Helper functions
    # -------------------

    def _hash_url(self, url: str) -> str:
        return hashlib.md5(url.encode("utf-8"), usedforsecurity=False).hexdigest()

    def _cache_file(self, key: str, text: str) -> Path:
        """Save text to a cache file."""
        cache_path = self.cache_dir / f"{key}.txt"
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)
        return cache_path

    def _load_cached(self, key: str) -> Optional[str]:
        """Load cached text if present; return None if missing or read fails."""
        cache_path = self.cache_dir / f"{key}.txt"
        if not cache_path.exists():
            return None
        def do_read():
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        return safe_call(do_read, error_msg=f"[VaultIndexer] Error reading cache for {key}", default=None)

    def _read_markdown(self, md_path: str) -> Optional[str]:
        """Read a Markdown file to string, returning None on failure.

        Uses builtins.open so tests patching open() can intercept.
        """
        path = Path(md_path)
        if not path.exists():
            return None

        def do_read_md():
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        return safe_call(do_read_md, error_msg=f"[VaultIndexer] Error reading markdown {md_path}", default=None)

    def _read_pdf(self, pdf_path: str) -> Optional[str]:
        """Read and extract text from a PDF file; return None on failure or if missing.

        Joins per-page text with newlines.
        """
        path = Path(pdf_path)
        if not path.exists():
            return None

        def do_read_pdf():
            reader = PdfReader(str(path))
            pieces = []
            for page in reader.pages:
                txt = page.extract_text() or ""
                txt = txt.strip()
                if txt:
                    pieces.append(txt)
            return "\n".join(pieces)

        return safe_call(do_read_pdf, error_msg=f"[VaultIndexer] Error reading PDF {pdf_path}", default=None)

    def _fetch_web_content(self, url: str) -> Optional[str]:
        """Fetch a URL and extract readable text using readability + BeautifulSoup.

        Returns None on any error.
        """

        def do_fetch():
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            doc = Document(resp.text)
            summary_html = doc.summary()
            soup = BeautifulSoup(summary_html, "html.parser")
            text = soup.get_text()
            return text or None

        return safe_call(do_fetch, error_msg=f"[VaultIndexer] Error fetching web content from {url}", default=None)

    # -------------------
    # Vault / Markdown
    # -------------------

    def index_vault(self, vault_path: str) -> Dict[str, int]:
        """Index all Markdown and PDF files in a vault directory."""
        results = {}
        for root, _, files in os.walk(vault_path):
            for file in files:
                full_path = os.path.join(root, file)
                def do_index(file=file, full_path=full_path):
                    if file.endswith(".md"):
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            self.emb_mgr.add_embedding(content, full_path)
                            results[full_path] = 1
                    elif file.endswith(".pdf"):
                        count = self.index_pdf(full_path)
                        results[full_path] = count
                safe_call(do_index, error_msg=f"[VaultIndexer] Error indexing {full_path}")
        return results

    def reindex_all(self, vault_path: str = "./vault") -> Dict[str, int]:
        """Re-scan all files in the vault."""
        return self.index_vault(vault_path)

    def reindex(self, vault_path: str) -> Dict[str, int]:
        """Clear collection and index all Markdown and PDF files in a vault directory.

        Returns a summary dict: {"files": <count>, "chunks": <count>}.
        """
        summary = {"files": 0, "chunks": 0}

        # Always attempt to clear collection even if directory doesn't exist
        if getattr(self.emb_mgr, "clear_collection", None):
            safe_call(self.emb_mgr.clear_collection, error_msg="[VaultIndexer] Error clearing collection")

        if not os.path.isdir(vault_path):
            return summary

        for root, _, files in os.walk(vault_path):
            for file in files:
                full_path = os.path.join(root, file)

                def do_index():
                    if file.endswith(".md"):
                        content = self._read_markdown(full_path)
                    elif file.endswith(".pdf"):
                        content = self._read_pdf(full_path)
                    else:
                        return 0  # unsupported

                    if not content:
                        return 0

                    chunks = self.emb_mgr.chunk_text(content) if getattr(self.emb_mgr, "chunk_text", None) else [content]
                    if not chunks:
                        return 0

                    if getattr(self.emb_mgr, "add_documents", None):
                        self.emb_mgr.add_documents(chunks)

                    summary["files"] += 1
                    summary["chunks"] += len(chunks)
                    return len(chunks)

                safe_call(do_index, error_msg=f"[VaultIndexer] Error indexing {full_path}")

        return summary

    # -------------------
    # PDF
    # -------------------

    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        def do_extract():
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        return safe_call(do_extract, error_msg=f"[VaultIndexer] PDF parsing failed for {pdf_path}", default="")

    def index_pdf(self, pdf_path: str) -> int:
        """Extract and embed a PDF."""
        def do_index_pdf():
            text = self.extract_pdf_text(pdf_path)
            if not text:
                return 0
            cache_key = self._hash_url(pdf_path)
            self._cache_file(cache_key, text)
            return self.emb_mgr.index_file(str(cache_key))
        return safe_call(do_index_pdf, error_msg=f"[VaultIndexer] Error indexing PDF {pdf_path}", default=0)

    # -------------------
    # Web pages
    # -------------------

    def fetch_web_page(self, url: str, force: bool = False) -> Optional[str]:
        """Fetch and sanitize a web page with caching."""
        cache_key = self._hash_url(url)
        cache_path = self.cache_dir / f"{cache_key}.txt"

        if cache_path.exists() and not force:
            def do_read():
                return cache_path.read_text(encoding="utf-8")
            return safe_call(do_read, error_msg=f"[VaultIndexer] Error reading cached web page {url}", default=None)

        def do_fetch():
            resp = requests.get(url, timeout=10, headers={"User-Agent": "ObsidianAssistant/1.0"})
            resp.raise_for_status()
            doc = Document(resp.text)
            summary_html = doc.summary()
            soup = BeautifulSoup(summary_html, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            if text:
                self._cache_file(cache_key, text)
                return text
            return None
        return safe_call(do_fetch, error_msg=f"[VaultIndexer] Failed to fetch {url}", default=None)

    def index_web_page(self, url: str, force: bool = False) -> int:
        """Fetch and embed a web page."""
        def do_index_web():
            text = self.fetch_web_page(url, force=force)
            if not text:
                return 0
            cache_key = self._hash_url(url)
            self._cache_file(cache_key, text)
            return self.emb_mgr.index_file(str(cache_key))
        return safe_call(do_index_web, error_msg=f"[VaultIndexer] Error indexing web page {url}", default=0)

    def index_web_content(self, url: str) -> Dict[str, Any]:
        """Fetch or load cached web content, chunk it, and add documents.

        Returns {"url": url, "chunks": n} and includes an "error" key on failure.
        """
        url_hash = self._hash_url(url)
        cached = self._load_cached(f"web_{url_hash}")
        content = cached if cached is not None else self._fetch_web_content(url)

        if not content:
            return {"url": url, "chunks": 0, "error": "Failed to fetch content"}

        chunks = self.emb_mgr.chunk_text(content) if getattr(self.emb_mgr, "chunk_text", None) else [content]
        if chunks and getattr(self.emb_mgr, "add_documents", None):
            self.emb_mgr.add_documents(chunks)

        return {"url": url, "chunks": len(chunks or [])}


class IndexingService:
    """
    Wrapper service that manages embeddings and vault indexing.
    Provides a single entry point for backend.py.
    """

    def __init__(self, emb_mgr: Optional[EmbeddingsManager] = None, cache_dir: str = "cache"):
        self.emb_mgr = emb_mgr or EmbeddingsManager()
        self.vault_indexer = VaultIndexer(emb_mgr=self.emb_mgr, cache_dir=cache_dir)

    def index_file(self, file_path: str) -> int:
        return self.vault_indexer.index_file(file_path)

    def index_vault(self, vault_path: str) -> Dict[str, int]:
        return self.vault_indexer.index_vault(vault_path)

    def index_pdf(self, pdf_path: str) -> int:
        return self.vault_indexer.index_pdf(pdf_path)

    def index_web_page(self, url: str, force: bool = False) -> int:
        return self.vault_indexer.index_web_page(url, force=force)

    def reindex_all(self, vault_path: str = "./vault") -> Dict[str, int]:
        return self.vault_indexer.reindex_all(vault_path)
