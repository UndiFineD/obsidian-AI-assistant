from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

from llm_router import HybridLLMRouter
from embeddings import EmbeddingManager
from indexing import VaultIndexer
from caching import CacheManager
from security import encrypt_data, decrypt_data

app = FastAPI(title="Obsidian LLM Backend")

# Allow CORS from Obsidian plugin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialize components ---
LLAMA_MODEL_PATH = "./models/llama-7b-q4.bin"
GPT4ALL_MODEL_PATH = "./models/gpt4all-lora.bin"

llm_router = HybridLLMRouter(LLAMA_MODEL_PATH, GPT4ALL_MODEL_PATH)
emb_manager = EmbeddingManager(db_path="./vector_db")
vault_indexer = VaultIndexer(emb_manager)
cache_manager = CacheManager("./cache")

# --- Data models ---
class AskRequest(BaseModel):
    question: str
    context_paths: Optional[List[str]] = None
    prefer_fast: Optional[bool] = True

class NoteEditRequest(BaseModel):
    note_path: str
    content: str

class FetchURLRequest(BaseModel):
    url: str

# --- API endpoints ---

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/ask")
async def ask(request: AskRequest):
    # Retrieve context from vector DB if provided
    context_text = ""
    if request.context_paths:
        context_chunks = []
        for path in request.context_paths:
            retrieved = emb_manager.get_embedding_text(path)
            context_chunks.append(retrieved)
        context_text = "\n".join(context_chunks)
    
    # Check cache first
    cached_answer = cache_manager.get_cached_answer(request.question)
    if cached_answer:
        return {"answer": cached_answer, "cached": True}

    answer = llm_router.query(
        request.question, 
        context=context_text, 
        prefer_fast=request.prefer_fast
    )

    cache_manager.store_answer(request.question, answer)
    return {"answer": answer, "cached": False}

@app.post("/api/format_note")
async def format_note(edit: NoteEditRequest):
    # Load note content
    if not os.path.exists(edit.note_path):
        return {"error": "note not found"}

    with open(edit.note_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # LLM-generated summary/suggestions
    summary = llm_router.query(
        f"Summarize and improve this note:\n{content}",
        prefer_fast=False
    )

    return {"note_path": edit.note_path, "suggestions": summary}

@app.post("/api/link_notes")
async def link_notes(edit: NoteEditRequest):
    # Find semantically related notes
    related_notes = emb_manager.search(edit.content, top_k=5)
    links = [r["id"] for r in related_notes if r["id"] != edit.note_path]
    return {"note_path": edit.note_path, "related_notes": links}

@app.post("/api/save_note_changes")
async def save_note_changes(edit: NoteEditRequest):
    os.makedirs(os.path.dirname(edit.note_path), exist_ok=True)
    with open(edit.note_path, "w", encoding="utf-8") as f:
        f.write(edit.content)

    # Re-embed updated content
    emb_manager.add_embedding(edit.content, edit.note_path)
    return {"status": "saved", "note_path": edit.note_path}

@app.post("/api/scan_vault")
async def scan_vault(vault_path: str):
    updated_files = vault_indexer.index_vault(vault_path)
    return {"indexed_files": updated_files}

@app.post("/api/fetch_url")
async def fetch_url(request: FetchURLRequest):
    text_content = vault_indexer.fetch_webpage(request.url)
    emb_manager.add_embedding(text_content, request.url)
    return {"url": request.url, "status": "fetched"}

@app.post("/api/reindex")
async def reindex():
    emb_manager.reset_db()
    updated_files = vault_indexer.reindex_all()
    return {"status": "reindexed", "indexed_files": updated_files}

# --- Run server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    