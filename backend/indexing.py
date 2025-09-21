import os
import hashlib
from pathlib import Path
from typing import Dict, Optional
from bs4 import BeautifulSoup
import requests
from readability import Document
from PyPDF2 import PdfReader

from backend.embeddings_manager import EmbeddingsManager

class VaultIndexer:
    def __init__(
        self, emb_mgr: Optional[EmbeddingsManager] = None, 
        cache_dir: str = "cache"
        ):
            
        self.emb_mgr = emb_mgr or EmbeddingsManager()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # -------------------
    # Helper Functions
    # -------------------

    def _hash_url(self, url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def _cache_file(self, key: str, text: str):
        """Save text to cache file."""
        cache_path = self.cache_dir / f"{key}.txt"
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)
        return cache_path

    # -------------------
    # Markdown Files
    # -------------------

    def index_vault(self, vault_path: str) -> Dict[str, int]:
        """Index all .md files in a vault."""
        vault = Path(vault_path)
        updated_files = []
        for root, _, files in os.walk(vault_path):
            for file in files:
                full_path = os.path.join(root, file)
                if file.endswith(".md"):
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.emb_manager.add_embedding(content, full_path)
                        updated_files.append(full_path)
                elif file.endswith(".pdf"):
                    self.index_pdf(full_path)
                    updated_files.append(full_path)
        return updated_files

    def fetch_webpage(self, url: str):
        r = requests.get(url, timeout=10)
        doc = Document(r.text)
        content = BeautifulSoup(doc.summary(), "html.parser").get_text()
        return content

    def reindex_all(self):
        # Re-scan all files in the vector DB’s known vault
        # For simplicity, assumes a saved vault path
        # Could store in config.yaml
        return self.index_vault("./vault")
        
    # -------------------
    # PDFs
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
        """Extract + embed a PDF."""
        text = self.extract_pdf_text(pdf_path)
        if not text:
            return 0

        cache_key = self._hash_url(pdf_path)
        cache_path = self._cache_file(cache_key, text)

        return self.emb_mgr.index_file(str(cache_path))

    # -------------------
    # Web Pages
    # -------------------

    def fetch_web_page(self, url: str, force: bool = False) -> Optional[str]:
        """Fetch + sanitize web page with caching."""
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
        """Fetch + embed a web page."""
        text = self.fetch_web_page(url, force=force)
        if not text:
            return 0

        cache_key = self._hash_url(url)
        cache_path = self._cache_file(cache_key, text)

        return self.emb_mgr.index_file(str(cache_path))  