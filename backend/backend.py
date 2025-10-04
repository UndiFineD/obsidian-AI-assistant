# backend/backend.py
import os
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Local imports ---
from .embeddings import EmbeddingsManager
from .indexing import VaultIndexer
from .caching import CacheManager
from .modelmanager import ModelManager

# --- Load environment variables ---
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
if HF_TOKEN:
    print("✅ Hugging Face token loaded from .env")
else:
    print("⚠️ Warning: No Hugging Face token found. Some models may not download.")

# --- FastAPI app ---
app = FastAPI(title="Obsidian AI Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialize services ---
model_manager = None
cache_manager = None
emb_manager = None
vault_indexer = None


def get_model_manager():
    global model_manager
    if model_manager is None:
        model_manager = ModelManager(hf_token=HF_TOKEN)
    return model_manager


def get_cache_manager():
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager("./cache")
    return cache_manager


def get_emb_manager():
    global emb_manager
    if emb_manager is None:
        emb_manager = EmbeddingsManager(db_path="./vector_db")
    return emb_manager


def get_vault_indexer():
    global vault_indexer
    if vault_indexer is None:
        vault_indexer = VaultIndexer(emb_mgr=get_emb_manager())
    return vault_indexer

# --- Ensure model is available ---
default_model = None
try:
    default_model = model_manager.load_model("llama-7b")
except Exception as e:
    print(f"Warning: Failed to load default model: {e}")

# ----------------------
# Request models
# ----------------------
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

# ----------------------
# API Endpoints
# ----------------------
@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/ask")
async def ask(request: AskRequest):
    cached_answer = get_cache_manager().get_cached_answer(request.question)
    if cached_answer:
        return {"answer": cached_answer, "cached": True, "model": request.model_name}

    context_text = ""
    if request.context_paths:
        context_chunks = [
            get_emb_manager().get_embedding_text(path)
            for path in request.context_paths
            if get_emb_manager().get_embedding_text(path)
        ]
        context_text = "\n".join(context_chunks)

    try:
        llm = get_model_manager().load_text_model(request.model_name)
        if request.prompt:
            answer = llm.generate(
                request.prompt,
                max_tokens=request.max_tokens
            )
        else:
            answer = llm.query(
                request.question,
                context=context_text,
                prefer_fast=request.prefer_fast
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) from e

    get_cache_manager().store_answer(request.question, answer)
    return {"answer": answer, "cached": False, "model": request.model_name}

@app.post("/api/format_note")
async def format_note(edit: NoteEditRequest):
    if not os.path.exists(edit.note_path):
        return {"error": "note not found"}
    with open(edit.note_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        llm = get_model_manager().load_text_model("llama-7b")
        prompt = f"Summarize and improve this note:\n{content}"
        summary = llm.query(prompt, prefer_fast=False)
        return {"note_path": edit.note_path, "suggestions": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to process note content"
        ) from e

@app.post("/api/link_notes")
async def link_notes(edit: NoteEditRequest):
    try:
        related_notes = get_emb_manager().search(edit.content, top_k=5)
        links = [
            r["source"] for r in related_notes 
            if r["source"] != edit.note_path
        ]
        return {"note_path": edit.note_path, "related_notes": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save_note_changes")
async def save_note_changes(edit: NoteEditRequest):
    os.makedirs(os.path.dirname(edit.note_path), exist_ok=True)
    with open(edit.note_path, "w", encoding="utf-8") as f:
        f.write(edit.content)
    get_emb_manager().add_embedding(edit.content, edit.note_path)
    return {"status": "saved", "note_path": edit.note_path}

@app.post("/api/scan_vault")
async def scan_vault(vault_path: str = "vault"):
    try:
        updated_files = get_vault_indexer().index_vault(vault_path)
        if not isinstance(updated_files, list):
            updated_files = []
        return {"indexed_files": updated_files, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fetch_url")
async def fetch_url(request: FetchURLRequest):
    text_content = get_vault_indexer().fetch_web_page(request.url)
    get_emb_manager().add_embedding(text_content, request.url)
    return {"url": request.url, "status": "fetched"}

@app.post("/api/reindex")
async def reindex(vault_path: str = "vault"):
    try:
        get_emb_manager().reset_db()
        updated_files = get_vault_indexer().reindex_all(vault_path)
        if not isinstance(updated_files, list):
            updated_files = []
        return {
            "status": "reindexed",
            "indexed_files": updated_files,
            "message": "Successfully reindexed vault"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search(query: str, top_k: int = 5):
    try:
        hits = get_emb_manager().search(query, top_k=top_k)
        return {"results": hits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/api/index_pdf")
async def index_pdf(pdf_path: str):
    count = get_vault_indexer().index_pdf(pdf_path)
    return {"chunks_indexed": count}

# ----------------------
# Run server
# ----------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
