import os
from bs4 import BeautifulSoup
import requests
from readability import Document
from PyPDF2 import PdfReader

class VaultIndexer:
    def __init__(self, emb_manager):
        self.emb_manager = emb_manager

    def index_vault(self, vault_path: str):
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

    def index_pdf(self, pdf_path: str):
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        self.emb_manager.add_embedding(text, pdf_path)

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
        
        