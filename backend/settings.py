"""
Centralized settings for backend and plugin bridge.

Precedence: environment variables > backend/config.yaml > code defaults.

Expose get_settings() to retrieve a cached singleton instance.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel

# Fields that can be safely updated via the API
_ALLOWED_UPDATE_KEYS = {
    "api_port",
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


class Settings(BaseModel):
    model_config = {"protected_namespaces": ()}  # Allow model_ prefixed fields

    # Core server
    backend_url: str = "http://127.0.0.1:8000"
    api_port: int = 8000
    allow_network: bool = False
    continuous_mode: bool = False

    # Paths
    project_root: str = str(Path(__file__).resolve().parents[1])
    vault_path: str = "vault"
    models_dir: str = "backend/models"
    cache_dir: str = "backend/cache"

    # LLM / embeddings / vector DB
    model_backend: str = "llama_cpp"
    model_path: str = "backend/models/llama-7b.gguf"
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_db: str = "chroma"
    gpu: bool = True
    top_k: int = 10
    chunk_size: int = 800
    chunk_overlap: int = 200
    similarity_threshold: float = 0.75

    # Voice
    vosk_model_path: str = "backend/models/vosk-model-small-en-us-0.15"

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
    try:
        import yaml
    except ImportError:
        yaml = None
    if not cfg_path.exists() or yaml is None:
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        # Drop unknown keys for safety
        allowed = set(Settings.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed}
    except Exception:
        return {}


def _coerce_value_for_field(field_name: str, value: Any) -> Optional[Any]:
    """Coerce a string value to the correct type for a given Settings field."""
    field_info = Settings.model_fields.get(field_name)
    if not field_info:
        return None

    target_type = field_info.annotation
    try:
        if target_type is bool:
            return str(value).lower() in {"1", "true", "yes", "on"}
        elif target_type is int:
            return int(value)
        elif target_type is float:
            return float(value)
        else:
            return str(value)
    except (ValueError, TypeError):
        # If coercion fails, return None to indicate the value should be skipped.
        return None


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
            coerced_value = _coerce_value_for_field(field, val)
            if coerced_value is not None:
                overrides[field] = coerced_value

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


def reload_settings() -> Settings:
    """Clear the cache and reload settings."""
    get_settings.cache_clear()
    return get_settings()


def update_settings(updates: dict) -> Settings:
    """Update settings with new values and reload."""
    from pathlib import Path

    import yaml

    # Filter updates to only include whitelisted keys
    filtered_updates = {}
    for key, value in updates.items():
        if key in _ALLOWED_UPDATE_KEYS:
            # Type coercion for known fields
            try:
                if key == "chunk_size" and isinstance(value, str):
                    filtered_updates[key] = int(value)
                elif key == "gpu" and isinstance(value, str):
                    filtered_updates[key] = value.lower() in ("true", "1", "yes")
                elif key == "similarity_threshold" and isinstance(value, str):
                    filtered_updates[key] = float(value)
                elif key == "vault_path":
                    filtered_updates[key] = str(value)
                else:
                    filtered_updates[key] = value
            except (ValueError, TypeError):
                # Skip invalid type coercions
                continue
    # Load existing config
    cfg_path = Path(__file__).parent / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}
    # Update with filtered values
    config.update(filtered_updates)
    # Save back to config.yaml
    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    # Reload settings
    return reload_settings()
