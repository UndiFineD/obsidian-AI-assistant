# backend/indexing.py
import os
import hashlib
from pathlib import Path
from typing import Dict, Optional
from bs4 import BeautifulSoup
import requests
from readability import Document
from PyPDF2 import PdfReader

try:
    from .embeddings import EmbeddingsManager
except ImportError:
    from embeddings import EmbeddingsManager


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
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def _cache_file(self, key: str, text: str) -> Path:
        """Save text to a cache file."""
        cache_path = self.cache_dir / f"{key}.txt"
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)
        return cache_path

    # -------------------
    # Vault / Markdown
    # -------------------

    def index_vault(self, vault_path: str) -> Dict[str, int]:
        """Index all Markdown and PDF files in a vault directory."""
        vault = Path(vault_path)
        results = {}
        for root, _, files in os.walk(vault_path):
            for file in files:
                full_path = os.path.join(root, file)
                if file.endswith(".md"):
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.emb_mgr.add_embedding(content, full_path)
                        results[full_path] = 1
                elif file.endswith(".pdf"):
                    count = self.index_pdf(full_path)
                    results[full_path] = count
        return results

    def reindex_all(self, vault_path: str = "./vault") -> Dict[str, int]:
        """Re-scan all files in the vault."""
        return self.index_vault(vault_path)

    # -------------------
    # PDF
    # -------------------

    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            print(f"PDF parsing failed for {pdf_path}: {e}")
            return ""

    def index_pdf(self, pdf_path: str) -> int:
        """Extract and embed a PDF."""
        text = self.extract_pdf_text(pdf_path)
        if not text:
            return 0
        cache_key = self._hash_url(pdf_path)
        self._cache_file(cache_key, text)
        return self.emb_mgr.index_file(str(cache_key))

    # -------------------
    # Web pages
    # -------------------

    def fetch_web_page(self, url: str, force: bool = False) -> Optional[str]:
        """Fetch and sanitize a web page with caching."""
        cache_key = self._hash_url(url)
        cache_path = self.cache_dir / f"{cache_key}.txt"

        if cache_path.exists() and not force:
            return cache_path.read_text(encoding="utf-8")

        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "ObsidianAssistant/1.0"})
            resp.raise_for_status()
            doc = Document(resp.text)
            summary_html = doc.summary()
            soup = BeautifulSoup(summary_html, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            if text:
                self._cache_file(cache_key, text)
                return text
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def index_web_page(self, url: str, force: bool = False) -> int:
        """Fetch and embed a web page."""
        text = self.fetch_web_page(url, force=force)
        if not text:
            return 0
        cache_key = self._hash_url(url)
        self._cache_file(cache_key, text)
        return self.emb_mgr.index_file(str(cache_key))


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
