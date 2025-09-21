import uvicorn
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv  # ✅ NEW: load .env support

from backend.indexing import IndexingService
from embeddings import EmbeddingManager
from indexing import VaultIndexer
from caching import CacheManager
from modelmanager import ModelManager

# --- Load environment variables from .env ---
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

if HF_TOKEN:
    print("✅ Hugging Face token loaded from .env")
else:
    print("⚠️ Warning: No Hugging Face token found. Some models may not download.")

# --- FastAPI app setup ---
app = FastAPI(title="Obsidian AI Assistant")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialize services ---
model_manager = ModelManager()
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
    # Check cache first
    cached_answer = cache_manager.get_cached_answer(request.question)
    if cached_answer:
        return {"answer": cached_answer, "cached": True, "model": request.model_name}

    # Retrieve context if provided
    context_text = ""
    if request.context_paths:
        context_chunks = [
            emb_manager.get_embedding_text(path)
            for path in request.context_paths
            if emb_manager.get_embedding_text(path)
        ]
        context_text = "\n".join(context_chunks)

    # Load requested model
    try:
        llm = model_manager.load_model(request.model_name)

        # Generate answer using prompt or question+context
        if request.prompt:
            answer = llm.generate(request.prompt, max_tokens=request.max_tokens)
        else:
            answer = llm.query(
                request.question,
                context=context_text,
                prefer_fast=request.prefer_fast
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save to cache
    cache_manager.store_answer(request.question, answer)

    return {"answer": answer, "cached": False, "model": request.model_name}

# --- Note formatting ---
@app.post("/api/format_note")
async def format_note(edit: NoteEditRequest):
    if not os.path.exists(edit.note_path):
        return {"error": "note not found"}

    with open(edit.note_path, "r", encoding="utf-8") as f:
        content = f.read()

    llm = model_manager.load_model("llama-7b")  # default model
    summary = llm.query(f"Summarize and improve this note:\n{content}", prefer_fast=False)
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
