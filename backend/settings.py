"""
Centralized settings for backend and plugin bridge.

Precedence: environment variables > backend/config.yaml > code defaults.

Expose get_settings() to retrieve a cached singleton instance.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # type: ignore


class Settings(BaseModel):
    # Core server
    backend_url: str = "http://127.0.0.1:8000"
    api_port: int = 8000
    allow_network: bool = False
    continuous_mode: bool = False

    # Paths
    project_root: str = str(Path(__file__).resolve().parents[1])
    vault_path: str = "vault"
    models_dir: str = "models"
    cache_dir: str = "cache"

    # LLM / embeddings / vector DB
    model_backend: str = "llama_cpp"
    model_path: str = "models/llama-7b.gguf"
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_db: str = "chroma"
    gpu: bool = True
    top_k: int = 10
    chunk_size: int = 800
    chunk_overlap: int = 200
    similarity_threshold: float = 0.75

    # Voice
    vosk_model_path: str = "models/vosk-model-small-en-us-0.15"

    # Derived
    @property
    def base_dir(self) -> Path:
        return Path(self.project_root)

    @property
    def abs_vault_path(self) -> Path:
        p = Path(self.vault_path)
        return p if p.is_absolute() else self.base_dir / p

    @property
    def abs_models_dir(self) -> Path:
        p = Path(self.models_dir)
        return p if p.is_absolute() else self.base_dir / p

    @property
    def abs_cache_dir(self) -> Path:
        p = Path(self.cache_dir)
        return p if p.is_absolute() else self.base_dir / p


def _load_yaml_config() -> dict:
    cfg_path = Path(__file__).parent / "config.yaml"
    if not cfg_path.exists() or yaml is None:
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def _merge_env(overrides: dict) -> dict:
    """Map selected environment variables into settings fields."""
    env_map = {
        "BACKEND_URL": "backend_url",
        "API_PORT": "api_port",
        "ALLOW_NETWORK": "allow_network",
        "CONTINUOUS_MODE": "continuous_mode",
        "VAULT_PATH": "vault_path",
        "MODELS_DIR": "models_dir",
        "CACHE_DIR": "cache_dir",
        "MODEL_BACKEND": "model_backend",
        "MODEL_PATH": "model_path",
        "EMBED_MODEL": "embed_model",
        "VECTOR_DB": "vector_db",
        "GPU": "gpu",
        "TOP_K": "top_k",
        "CHUNK_SIZE": "chunk_size",
        "CHUNK_OVERLAP": "chunk_overlap",
        "SIMILARITY_THRESHOLD": "similarity_threshold",
        "VOSK_MODEL_PATH": "vosk_model_path",
    }

    for env_key, field in env_map.items():
        if env_key in os.environ and os.environ[env_key] != "":
            val = os.environ[env_key]
            # Cast simple types
            if field in {"api_port", "top_k", "chunk_size", "chunk_overlap"}:
                try:
                    overrides[field] = int(val)
                except ValueError:
                    continue
            elif field in {"allow_network", "continuous_mode", "gpu"}:
                overrides[field] = str(val).lower() in {"1", "true", "yes", "on"}
            elif field in {"similarity_threshold"}:
                try:
                    overrides[field] = float(val)
                except ValueError:
                    continue
            else:
                overrides[field] = val
    return overrides


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    data = _load_yaml_config()
    data = _merge_env(dict(data))
    # Compute backend_url from api_port if not explicitly provided
    if not data.get("backend_url"):
        port = data.get("api_port", Settings().api_port)
        data["backend_url"] = f"http://127.0.0.1:{port}"
    return Settings(**data)


# --- Runtime helpers for API endpoints ---

_ALLOWED_UPDATE_KEYS = {
    "allow_network",
    "continuous_mode",
    "vault_path",
    "models_dir",
    "cache_dir",
    "model_backend",
    "model_path",
    "embed_model",
    "vector_db",
    "gpu",
    "top_k",
    "chunk_size",
    "chunk_overlap",
    "similarity_threshold",
    "vosk_model_path",
}


def reload_settings() -> Settings:
    try:
        get_settings.cache_clear()  # type: ignore[attr-defined]
    except Exception:
        pass
    return get_settings()


def update_settings(updates: dict) -> Settings:
    """Persist selected fields to backend/config.yaml and reload settings."""
    cfg_path = Path(__file__).parent / "config.yaml"
    current = _load_yaml_config()
    if not isinstance(current, dict):
        current = {}
    # Filter and coerce
    for k, v in list(updates.items()):
        if k not in _ALLOWED_UPDATE_KEYS:
            updates.pop(k, None)
            continue
        # Basic coercions
        if k in {"top_k", "chunk_size", "chunk_overlap"}:
            try:
                updates[k] = int(v)
            except Exception:
                updates.pop(k, None)
        elif k in {"similarity_threshold"}:
            try:
                updates[k] = float(v)
            except Exception:
                updates.pop(k, None)
        elif k in {"allow_network", "continuous_mode", "gpu"}:
            updates[k] = True if str(v).lower() in {"1", "true", "yes", "on"} else False
        else:
            # strings/paths
            updates[k] = str(v)

    if updates and yaml is not None:
        current.update(updates)
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(current, f, sort_keys=False)
        except Exception:
            # If write fails, still return current in-memory merged settings
            pass
    return reload_settings()
