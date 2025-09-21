import uvicorn
import os
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.llm_router import HybridLLMRouter
from backend.indexing import IndexingService
from embeddings import EmbeddingManager
from indexing import VaultIndexer
from caching import CacheManager
from security import encrypt_data, decrypt_data

app = FastAPI(title="Obsidian AI Assistant")

# Allow CORS from Obsidian plugin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialize services ---
router = HybridLLMRouter(
    llama_model_path="models/llama-7b-q4.bin",
    gpt4all_model_path="models/gpt4all-lora-quantized.bin",
    prefer_fast=True,
    memory_limit=8 * 1024 ** 3  # 8GB
)
emb_manager = EmbeddingManager(db_path="./vector_db")
vault_indexer = VaultIndexer(emb_manager)
cache_manager = CacheManager("./cache")
indexer = IndexingService(emb_mgr=emb_manager)

# --- Data models ---
class AskRequest(BaseModel):
    question: str
    context_paths: Optional[List[str]] = None
    prefer_fast: Optional[bool] = True
    prompt: Optional[str] = None
    max_tokens: int = 256
    model_name: Optional[str] = "llama-7b"

class NoteEditRequest(BaseModel):
    note_path: str
    content: str

class FetchURLRequest(BaseModel):
    url: str

# --- Health check ---
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# --- Ask endpoint ---
@app.post("/api/ask")
async def ask(request: AskRequest):
    # 1️⃣ Check cache
    cached_answer = cache_manager.get_cached_answer(request.question)
    if cached_answer:
        return {"answer": cached_answer, "cached": True}

    # 2️⃣ Retrieve context if provided
    context_text = ""
    if request.context_paths:
        context_chunks = []
        for path in request.context_paths:
            retrieved = emb_manager.get_embedding_text(path)
            if retrieved:
                context_chunks.append(retrieved)
        context_text = "\n".join(context_chunks)

    # 3️⃣ Generate answer using LLM
    try:
        if request.prompt:
            # Use custom prompt if provided
            answer = router.generate(request.prompt, max_tokens=request.max_tokens)
        else:
            # Otherwise, use question + context
            answer = router.query(
                request.question,
                context=context_text,
                prefer_fast=request.prefer_fast
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4️⃣ Save to cache
    cache_manager.store_answer(request.question, answer)

    return {"answer": answer, "cached": False, "model": request.model_name}


# --- Note formatting ---
@app.post("/api/format_note")
async def format_note(edit: NoteEditRequest):
    if not os.path.exists(edit.note_path):
        return {"error": "note not found"}

    with open(edit.note_path, "r", encoding="utf-8") as f:
        content = f.read()

    summary = router.query(
        f"Summarize and improve this note:\n{content}",
        prefer_fast=False
    )
    return {"note_path": edit.note_path, "suggestions": summary}

# --- Link notes ---
@app.post("/api/link_notes")
async def link_notes(edit: NoteEditRequest):
    related_notes = emb_manager.search(edit.content, top_k=5)
    links = [r["id"] for r in related_notes if r["id"] != edit.note_path]
    return {"note_path": edit.note_path, "related_notes": links}

# --- Save note changes ---
@app.post("/api/save_note_changes")
async def save_note_changes(edit: NoteEditRequest):
    os.makedirs(os.path.dirname(edit.note_path), exist_ok=True)
    with open(edit.note_path, "w", encoding="utf-8") as f:
        f.write(edit.content)
    emb_manager.add_embedding(edit.content, edit.note_path)
    return {"status": "saved", "note_path": edit.note_path}

# --- Scan vault ---
@app.post("/api/scan_vault")
async def scan_vault(vault_path: str = "vault"):
    updated_files = vault_indexer.index_vault(vault_path)
    return {"indexed_files": updated_files}

# --- Fetch URL ---
@app.post("/api/fetch_url")
async def fetch_url(request: FetchURLRequest):
    text_content = vault_indexer.fetch_webpage(request.url)
    emb_manager.add_embedding(text_content, request.url)
    return {"url": request.url, "status": "fetched"}

# --- Reindex vault ---
@app.post("/api/reindex")
async def reindex(vault_path: str = "vault"):
    emb_manager.reset_db()
    updated_files = vault_indexer.reindex_all(vault_path)
    return {"status": "reindexed", "indexed_files": updated_files}

# --- Search ---
@app.post("/api/search")
async def search(query: str, top_k: int = 5):
    hits = emb_manager.search(query, top_k=top_k)
    return {"results": hits}

# --- Index PDF ---
@app.post("/api/index_pdf")
async def index_pdf(pdf_path: str):
    count = indexer.index_pdf(pdf_path)
    return {"chunks_indexed": count}

# --- Run server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
