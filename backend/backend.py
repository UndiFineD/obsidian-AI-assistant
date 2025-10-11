# backend/backend.py

import os
import sys as _sys
import time
from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .caching import CacheManager
from .embeddings import EmbeddingsManager
from .indexing import IndexingService, VaultIndexer
from .modelmanager import ModelManager
from .performance import (
    PerformanceMonitor,
    cached,
    get_cache_manager,
    get_connection_pool,
    get_task_queue,
)
from .settings import get_settings, reload_settings, update_settings

# --- External env loader (no secrets committed) ---
def _load_external_env():
    """Optionally load secrets (e.g., HF token) from an external file not in the repo.

    Priority:
    1) EXTERNAL_ENV_FILE environment variable points to a file
    2) Default path under the user's DEV folder: %USERPROFILE%/DEV/obsidian-llm-assistant/venv.txt

    Supported formats inside the file:
    - KEY=VALUE lines (e.g., HF_TOKEN=xxxxx)
    - Single token string (will be used as both HF_TOKEN and HUGGINGFACE_TOKEN)
    """
    try:
        import os
        from pathlib import Path

        # explicit override via env var
        path = os.environ.get("EXTERNAL_ENV_FILE")
        if not path:
            user_root = os.path.expanduser("~")
            default_path = Path(user_root) / "DEV" / "obsidian-llm-assistant" / "venv.txt"
            path = str(default_path)

        p = Path(path)
        if not p.exists():
            return

        # Read lines and apply
        content = p.read_text(encoding="utf-8").strip()
        if not content:
            return

        if "\n" not in content and "=" not in content:
            # Single token – set both names if not already set
            if not os.environ.get("HF_TOKEN"):
                os.environ["HF_TOKEN"] = content
            if not os.environ.get("HUGGINGFACE_TOKEN"):
                os.environ["HUGGINGFACE_TOKEN"] = content
            print("[env] External token loaded from venv.txt (single-token)")
            return

        # Parse KEY=VALUE lines
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                # Only set if not already present in process env
                if k and v and not os.environ.get(k):
                    os.environ[k] = v
        # Ensure aliasing
        tok = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        if tok:
            os.environ.setdefault("HF_TOKEN", tok)
            os.environ.setdefault("HUGGINGFACE_TOKEN", tok)
        print("[env] External env loaded from venv.txt")
    except Exception as e:
        print(f"[env] Warning: failed loading external env: {e}")

# Global flag to track background queue initialization
_background_queue_started = False

# Enterprise imports
try:
    from .enterprise_integration import EnterpriseIntegration

    ENTERPRISE_AVAILABLE = True
except ImportError as e:
    print(f"Enterprise features not available: {e}")
    ENTERPRISE_AVAILABLE = False

# --- FastAPI app ---
app = FastAPI(
    title=(
        "Obsidian AI Assistant - Enterprise Edition"
        if ENTERPRISE_AVAILABLE
        else "Obsidian AI Assistant"
    )
)

# Initialize enterprise features if available
if ENTERPRISE_AVAILABLE:
    try:
        enterprise_integration = EnterpriseIntegration()
        enterprise_integration.setup_enterprise_app(app)
        print("[Enterprise] Enterprise features initialized successfully")
    except Exception as e:
        print(f"[Enterprise] Warning: Failed to initialize enterprise features: {e}")
        ENTERPRISE_AVAILABLE = False

# Add basic CORS middleware (enterprise middleware will override if available)
if not ENTERPRISE_AVAILABLE:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- Services (lazy-init) ---
model_manager = None  # will be set to ModelManager instance
emb_manager = None  # will be set to EmbeddingsManager instance
vault_indexer = None  # will be set to VaultIndexer instance
cache_manager = None  # will be set to CacheManager instance


def init_services():
    """Initialize global service singletons with performance optimizations.

    Reads environment variables at call time so tests can patch env before import.
    Includes connection pooling and performance monitoring setup.
    """
    global model_manager, emb_manager, vault_indexer, cache_manager
    if all(
        v is not None
        for v in (model_manager, emb_manager, vault_indexer, cache_manager)
    ):
        return

    # Initialize performance systems
    _init_performance_systems()

    # Load env here (not at module import) so tests can patch
    # 1) External env (venv.txt outside repo)
    _load_external_env()

    # 2) .env in current working directory (optional)
    def safe_init(cls, *args, **kwargs):
        try:
            return cls(*args, **kwargs)
        except Exception as e:
            print(f"[init_services] Error initializing {cls.__name__}: {e}")
            return None

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception as e:
        print(f"[init_services] Error loading .env: {e}")
    # Prefer settings-based initialization; fall back to defaults if it fails
    try:
        if hasattr(ModelManager, "from_settings"):
            model_manager = safe_init(ModelManager.from_settings)
        else:
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            model_manager = safe_init(ModelManager, hf_token=hf_token)
    except Exception:
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        model_manager = safe_init(ModelManager, hf_token=hf_token)

    try:
        if hasattr(EmbeddingsManager, "from_settings"):
            emb_manager = safe_init(EmbeddingsManager.from_settings)
        else:
            emb_manager = safe_init(EmbeddingsManager, db_path="./vector_db")
    except Exception:
        emb_manager = safe_init(EmbeddingsManager, db_path="./vector_db")

    # Use IndexingService.from_settings if available, otherwise use VaultIndexer with settings-based cache
    try:
        if hasattr(IndexingService, "from_settings"):
            indexing_service = safe_init(IndexingService.from_settings)
            vault_indexer = indexing_service.vault_indexer if indexing_service else None
        else:
            vault_indexer = safe_init(VaultIndexer, emb_mgr=emb_manager)
    except Exception:
        vault_indexer = safe_init(VaultIndexer, emb_mgr=emb_manager)

    cache_manager = safe_init(CacheManager, "./cache")


@app.on_event("startup")
async def _app_startup():
    """Initialize services on app startup.

    If FAST_STARTUP is set, perform initialization in a background thread to
    allow the server to respond to health checks quickly.
    """
    fast = os.getenv("FAST_STARTUP", "0").lower() in ("1", "true", "yes", "on")
    if fast:
        try:
            import threading

            threading.Thread(target=init_services, daemon=True).start()
            print("[startup] FAST_STARTUP enabled – initializing services in background")
        except Exception as e:
            print(f"[startup] Warning: failed to start background init: {e}")
    else:
        init_services()


def _init_performance_systems():
    """Initialize performance optimization systems"""
    try:
        # Initialize connection pools for different services

        # Model connection pool - for managing AI model instances
        def create_model_connection():
            """Factory function for model connections"""
            # This is a placeholder - would create actual model instances
            # in a real implementation with heavy models
            return {"status": "connected", "created": time.time()}

        get_connection_pool(
            "models", create_model_connection, min_size=1, max_size=3, max_idle=600
        )

        # Database connection pool - for vector database connections
        def create_db_connection():
            """Factory function for database connections"""
            return {"status": "connected", "created": time.time()}

        get_connection_pool(
            "vector_db", create_db_connection, min_size=2, max_size=5, max_idle=300
        )

        # Initialize async task queue for background processing
        # Note: Background queue will be started when first async endpoint is called
        print(
            "[Performance] Initialized connection pools (task queue will start on first async call)"
        )

    except Exception as e:
        print(f"[Performance] Warning: Failed to initialize performance systems: {e}")


async def _ensure_background_queue():
    """Ensure the background task queue is started (called from async endpoints)"""
    global _background_queue_started
    if not _background_queue_started:
        try:
            await get_task_queue()  # Initialize the task queue
            _background_queue_started = True
            print("[Performance] Background task queue started")
        except Exception as e:
            print(f"[Performance] Warning: Failed to start task queue: {e}")


# ----------------------
# Request models (exported via package)
# ----------------------
class AskRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    question: str
    prefer_fast: bool = True
    max_tokens: int = 256
    # Optional extras used by our internal flows
    context_paths: Optional[List[str]] = None
    prompt: Optional[str] = None
    model_name: Optional[str] = "llama-7b"


class ReindexRequest(BaseModel):
    vault_path: str = "./vault"


class WebRequest(BaseModel):
    url: str
    question: Optional[str] = None


class TranscribeRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    format: str = "webm"  # Audio format
    language: str = "en"  # Language code


# ----------------------
# API Endpoints
# ----------------------
def _health_payload():
    return {"status": "ok", "timestamp": int(time.time())}


@app.get("/api/health")
async def api_health():
    return _health_payload()


@app.get("/status")
async def status():
    """Lightweight status endpoint for quick liveness checks."""
    return {"status": "ok"}


@app.get("/health")
async def health():
    """Return a comprehensive health payload including a settings snapshot."""
    payload = _health_payload()
    s = get_settings()
    payload.update(
        {
            "backend_url": s.backend_url,
            "api_port": s.api_port,
            "vault_path": str(s.vault_path),
            "models_dir": str(s.models_dir),
            "cache_dir": str(s.cache_dir),
            "model_backend": s.model_backend,
            "embed_model": s.embed_model,
            "vector_db": s.vector_db,
            "allow_network": s.allow_network,
            "gpu": s.gpu,
        }
    )
    return payload


@app.get("/api/config")
async def get_config():
    from backend.settings import _ALLOWED_UPDATE_KEYS

    s = get_settings()
    # Only return whitelisted fields to avoid exposing sensitive data
    data = s.dict()
    return {k: v for k, v in data.items() if k in _ALLOWED_UPDATE_KEYS}


@app.post("/api/config/reload")
async def post_reload_config():
    try:
        s = reload_settings()
        return {"ok": True, "settings": s.dict()}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reload settings: {str(e)}"
        ) from e


@app.post("/api/config")
async def post_update_config(partial: dict):
    try:
        s = update_settings(dict(partial or {}))
        return {"ok": True, "settings": s.dict()}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update settings: {str(e)}"
        ) from e


def _ask_impl(request: AskRequest):
    # Ensure services
    global model_manager, cache_manager
    if model_manager is None or cache_manager is None:
        init_services()
    # If model manager failed to initialize, return an error status
    if model_manager is None:
        raise HTTPException(status_code=500, detail="Model manager unavailable")

    # Use the centralized, high-performance cache
    performance_cache = get_cache_manager()
    cache_key = f"ask:{hash((request.question, request.model_name, request.max_tokens, request.prefer_fast))}"

    cached_result = performance_cache.get(cache_key)
    if cached_result is not None:
        return {
            "answer": cached_result,
            "cached": True,
            "cache_level": "performance",
            "model": request.model_name,
        }

    # Generate new answer
    try:
        # Get context from embeddings if use_context is True
        context_text = ""
        use_context = getattr(request, "use_context", False)
        if use_context and emb_manager and hasattr(request, "question"):
            search_results = emb_manager.search(
                request.question, top_k=get_settings().top_k
            )
            if search_results:
                context_text = "\n".join([hit["text"] for hit in search_results])

        # Limit context size to 16,000 characters to avoid model failures
        MAX_CONTEXT_CHARS = 16000
        if context_text and len(context_text) > MAX_CONTEXT_CHARS:
            print(
                f"[ask_impl] Warning: Context truncated from {len(context_text)} to {MAX_CONTEXT_CHARS} characters."
            )
            context_text = context_text[:MAX_CONTEXT_CHARS]

        # Prepare the prompt for the model
        if context_text:
            to_generate = f"Context: {context_text}\n\nQuestion: {request.question}"
        else:
            to_generate = request.prompt if request.prompt else request.question

        start_time = time.time()
        answer = model_manager.generate(
            to_generate,
            context=context_text,
            prefer_fast=request.prefer_fast,
            max_tokens=request.max_tokens,
        )
        generation_time = time.time() - start_time

        if not answer or (isinstance(answer, str) and "No model available" in answer):
            raise RuntimeError("Model unavailable or failed to generate an answer.")
    except Exception as e:
        print(f"[_ask_impl] Error generating answer: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    performance_cache.set(cache_key, answer)

    return {
        "answer": answer,
        "cached": False,
        "model": request.model_name,
        "generation_time": generation_time,
    }


@app.post("/api/ask")
async def api_ask(request: AskRequest):
    return _ask_impl(request)


@app.post("/ask")  # type: ignore
async def ask(request: AskRequest):
    return _ask_impl(request)


# Note editing endpoints removed for test alignment


@app.post("/api/scan_vault")
async def scan_vault(vault_path: str = "vault"):
    global vault_indexer
    if vault_indexer is None:
        init_services()
    if not os.path.isdir(vault_path):
        raise HTTPException(status_code=400, detail=f"Invalid vault path: {vault_path}")
    return {"indexed_files": vault_indexer.index_vault(vault_path)}


@app.post("/api/web")
async def api_web(request: WebRequest):
    """Process web content and answer a question about it."""
    global model_manager, vault_indexer
    if model_manager is None or vault_indexer is None:
        init_services()

    if not vault_indexer:
        raise HTTPException(
            status_code=503, detail="Indexing service is not available."
        )

    content = vault_indexer.fetch_web_page(request.url)
    if not content:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch or process content from URL: {request.url}",
        )

    question = (
        request.question or f"Summarize the following content:\n\n{content[:2000]}"
    )
    answer = model_manager.generate(question, context=content)
    return {"answer": answer, "url": request.url}


@app.post("/web")
async def web(request: WebRequest):
    """Alias for /api/web for backward compatibility."""
    return await api_web(request)


@app.post("/api/reindex")
async def api_reindex(request: ReindexRequest):
    # Return what the indexer reports; tests stub this
    global vault_indexer
    if vault_indexer is None:
        init_services()
    return vault_indexer.reindex(request.vault_path)


@app.post("/reindex")
async def reindex(request: ReindexRequest):
    global vault_indexer
    if vault_indexer is None:
        init_services()
    return vault_indexer.reindex(request.vault_path)


@app.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio to text using a speech-to-text service.
    This is a fallback when browser-based speech recognition is not available.
    """
    try:
        import base64

        # Decode base64 audio data
        audio_bytes = base64.b64decode(request.audio_data)
        # TODO: Implement actual transcription logic
        _ = audio_bytes  # Acknowledge variable to avoid unused warning

        # For now, return a placeholder response
        # In a production environment, you would integrate with:
        # - OpenAI Whisper (local or API)
        # - Google Cloud Speech-to-Text
        # - Azure Cognitive Services
        # - AWS Transcribe

        # Placeholder implementation
        transcription = "Server-side speech recognition not yet implemented. Please use browser speech recognition."

        return {
            "transcription": transcription,
            "confidence": 0.0,
            "status": "placeholder",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Transcription failed: {str(e)}"
        ) from e


@app.post("/api/search")
async def search(query: str, top_k: int = 5):
    global emb_manager
    if emb_manager is None:
        init_services()
    try:
        hits = emb_manager.search(query, top_k=top_k)
        return {"results": hits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/index_pdf")
async def index_pdf(pdf_path: str):
    global vault_indexer
    if vault_indexer is None:
        init_services()
    count = vault_indexer.index_pdf(pdf_path)
    return {"chunks_indexed": count}


# ----------------------
# Performance & Monitoring Endpoints
# ----------------------


@app.get("/api/performance/metrics")
async def get_performance_metrics():
    """Get comprehensive performance metrics"""
    try:
        metrics = PerformanceMonitor.get_system_metrics()
        return {"status": "success", "metrics": metrics, "timestamp": time.time()}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get metrics: {str(e)}"
        ) from e


@app.get("/api/performance/cache/stats")
async def get_cache_stats():
    """Get detailed cache performance statistics"""
    try:
        cache_manager = get_cache_manager()
        stats = cache_manager.get_stats()
        return {"status": "success", "cache_stats": stats}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache stats: {str(e)}"
        ) from e


@app.post("/api/performance/cache/clear")
async def clear_performance_cache():
    """Clear performance cache (L1 and L2)"""
    try:
        cache_manager = get_cache_manager()
        # Clear L1 cache
        cache_manager.l1_cache.clear()
        # Clear L2 cache
        cache_manager.l2_cache.clear()
        cache_manager._persist_l2_cache()

        return {"status": "success", "message": "Performance cache cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear cache: {str(e)}"
        ) from e


@app.post("/api/performance/optimize")
async def trigger_optimization(background_tasks: BackgroundTasks):
    """Trigger background performance optimization tasks"""
    try:
        task_queue = await get_task_queue()

        # Schedule optimization tasks
        optimization_tasks = [
            _cleanup_expired_cache(),
            _optimize_connection_pools(),
            _collect_performance_metrics(),
        ]

        scheduled_count = 0
        for task in optimization_tasks:
            success = await task_queue.submit_task(task, priority=1)
            if success:
                scheduled_count += 1

        return {
            "status": "success",
            "message": f"Scheduled {scheduled_count} optimization tasks",
            "queue_stats": task_queue.get_stats(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger optimization: {str(e)}"
        ) from e


# Background optimization tasks
async def _cleanup_expired_cache():
    """Clean up expired cache entries"""
    try:
        cache_manager = get_cache_manager()

        # Clean L1 cache
        expired_keys = [
            key for key, entry in cache_manager.l1_cache.items() if entry.is_expired()
        ]
        for key in expired_keys:
            del cache_manager.l1_cache[key]

        # Clean L2 cache
        expired_keys = [
            key for key, entry in cache_manager.l2_cache.items() if entry.is_expired()
        ]
        for key in expired_keys:
            del cache_manager.l2_cache[key]

        cache_manager._persist_l2_cache()

    except Exception as e:
        print(f"Cache cleanup failed: {e}")


async def _optimize_connection_pools():
    """Optimize connection pools by cleaning idle connections"""
    try:
        from .performance import _connection_pools

        for _, pool in _connection_pools.items():
            pool.cleanup_idle_connections()
    except Exception as e:
        print(f"Connection pool optimization failed: {e}")


async def _collect_performance_metrics():
    """Collect and log performance metrics"""
    try:
        metrics = PerformanceMonitor.get_system_metrics()
        # Log metrics for analysis (could be sent to monitoring system)
        print(f"Performance metrics collected: {metrics['timestamp']}")
    except Exception as e:
        print(f"Metrics collection failed: {e}")


# Enhanced ask endpoint with performance caching
@cached(
    ttl=1800,
    key_func=lambda req: f"ask:{hash((req.question, req.model_name, req.max_tokens))}",
)
def _cached_ask_processing(question: str, model_name: str, max_tokens: int) -> str:
    """Cached version of AI processing for identical requests"""
    # This would be called by the main ask endpoint for cacheable requests
    return f"Cached response for: {question[:50]}..."


# ----------------------
# Enterprise Feature Endpoints (if available)
# ----------------------

if ENTERPRISE_AVAILABLE:

    @app.get("/api/enterprise/status")
    async def enterprise_status():
        """Get enterprise features status"""
        return {
            "enterprise_enabled": True,
            "features": {
                "sso_authentication": True,
                "multi_tenant": True,
                "rbac": True,
                "gdpr_compliance": True,
                "soc2_compliance": True,
                "admin_dashboard": True,
            },
            "version": "1.0.0",
        }

    @app.get("/api/enterprise/demo")
    async def enterprise_demo():
        """Demo endpoint showing enterprise capabilities"""
        return {
            "message": "Enterprise AI Assistant - Production Ready",
            "capabilities": [
                "Single Sign-On (SSO) with Azure AD, Google, Okta, SAML, LDAP",
                "Multi-tenant architecture with resource isolation",
                "Role-based access control (RBAC) with granular permissions",
                "GDPR compliance with data subject rights management",
                "SOC2 Type II compliance framework",
                "Comprehensive admin dashboard and monitoring",
                "Enterprise-grade security and audit logging",
                "Scalable tenant management and billing",
            ],
            "authentication": "JWT-based with enterprise SSO integration",
            "compliance": "GDPR and SOC2 ready with audit trails",
            "security": "Enterprise-grade with role-based permissions",
        }

else:

    @app.get("/api/enterprise/status")
    async def enterprise_status_unavailable():
        """Enterprise features not available"""
        return {
            "enterprise_enabled": False,
            "message": "Enterprise features not available in this deployment",
            "available_features": [
                "Basic AI Assistant",
                "Document Indexing",
                "Web Search",
            ],
        }


# ----------------------
# Run server
# ----------------------
if __name__ == "__main__":
    # Start FastAPI app using Uvicorn
    import uvicorn

    # Non-blocking fast startup for CLI run as well
    if os.getenv("FAST_STARTUP", "0") in ("1", "true", "True"):
        import threading
        threading.Thread(target=init_services, daemon=True).start()
    else:
        init_services()
    PORT = 8000
    print(f"Starting FastAPI backend at http://127.0.0.1:{PORT}")
    uvicorn.run("backend.backend:app", host="127.0.0.1", port=PORT, reload=False)


# Ensure this module can be accessed as 'backend.backend' regardless of import mode
try:
    # When imported as top-level module 'backend', make it behave like a package for submodule import
    this_mod = _sys.modules.get(__name__)
    if this_mod is not None:
        # Expose attribute for patch targets: backend.backend -> this module
        this_mod.__dict__.setdefault("backend", this_mod)
        # Mark as package-like: provide __path__ so import system allows 'backend.backend'
        if not hasattr(this_mod, "__path__"):
            this_mod.__path__ = []  # type: ignore[attr-defined]
        # Register alias in sys.modules
        fq_name = "backend.backend"
        _sys.modules.setdefault(fq_name, this_mod)
except Exception as e:
    import logging
    logging.error(f"Exception in backend.backend (module access): {e}")


# Do not initialize services at import time to keep startup fast for the server
