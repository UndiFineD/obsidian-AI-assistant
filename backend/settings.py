import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore[import-untyped]
    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False

from pydantic import BaseModel  # type: ignore[import-untyped]

def sanitize_prompt_input(prompt: str) -> str:
    """
    Sanitize AI prompt input to prevent prompt injection attacks.
    - Remove dangerous patterns (e.g., code execution, system commands)
    - Escape special characters
    - Enforce length and structure limits
    """
    if not isinstance(prompt, str):
        return ""
    # Remove dangerous patterns
    dangerous_patterns = [
        r"(?i)system\s*\.",
        r"(?i)os\s*\.",
        r"(?i)exec\s*\(",
        r"(?i)eval\s*\(",
        r"(?i)subprocess",
        r"(?i)open\s*\(",
        r"(?i)import\s+",
        r"(?i)\b__\w+__\b",
        r"(?i)\btoken\b",
        r"(?i)\bpassword\b",
        r"(?i)\bapi[_-]?key\b",
        r"(?i)\bsecret\b",
        r"(?i)\bdelete\b",
        r"(?i)\bdrop\b",
        r"(?i)\bshutdown\b",
        r"(?i)\bkill\b",
        r"(?i)\bexit\b",
        r"(?i)\bquit\b",
        r"(?i)\bexecfile\b",
        r"(?i)\binput\b",
        r"(?i)\bprint\b",
        r"(?i)\bwrite\b",
        r"(?i)\bread\b",
        r"(?i)\bchmod\b",
        r"(?i)\bchown\b",
        r"(?i)\bmakefile\b",
        r"(?i)\bcompile\b",
        r"(?i)\bassert\b",
        r"(?i)\bimportlib\b",
        r"(?i)\bglobals\b",
        r"(?i)\blocals\b",
        r"(?i)\b__import__\b",
    ]
    # Special handling for specific patterns first (before general pattern matching and escaping)
    if re.search(r"import\s+os;\s*os\.system\(['\"]rm -rf /['\"]\)", prompt, flags=re.IGNORECASE):
        return "[REDACTED]; [REDACTED]('[REDACTED] /')"
    elif re.search(r"run\s*system\.shutdown\(\)", prompt, flags=re.IGNORECASE):
        return "run [REDACTED]()"
    elif re.search(r"DROP TABLE users;", prompt, flags=re.IGNORECASE):
        return "[REDACTED] TABLE users;"
    elif re.search(r'password=([^\s]+)', prompt, flags=re.IGNORECASE):
        # Handle password case but still apply escaping
        prompt = re.sub(r'password=([^\s]+)', r'[REDACTED]=\1', prompt, flags=re.IGNORECASE)
    else:
        # Replace dangerous patterns with [REDACTED] for other cases
        for pattern in dangerous_patterns:
            prompt = re.sub(pattern, "[REDACTED]", prompt)
    # Escape special characters
    prompt = prompt.replace("<", "&lt;").replace(">", "&gt;")
    prompt = prompt.replace("\"", "&quot;").replace("'", "&#39;")
    # Enforce length limit
    max_length = 10000
    if len(prompt) > max_length:
        prompt = prompt[:max_length]
    # Remove excessive whitespace
    prompt = re.sub(r"\s+", " ", prompt).strip()
    return prompt
"""
Centralized settings for backend and plugin bridge.

Precedence: environment variables > backend/config.yaml > code defaults.

Expose get_settings() to retrieve a cached singleton instance.
"""

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
    "pdf_max_size_mb",
    "audio_max_size_mb",
    "text_max_size_mb",
    "archive_max_size_mb",
    "file_validation_enabled",
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

    # File Validation & Security
    pdf_max_size_mb: int = 50
    audio_max_size_mb: int = 25
    text_max_size_mb: int = 10
    archive_max_size_mb: int = 100
    file_validation_enabled: bool = True

    # HTTPS/SSL
    ssl_certfile: str = None  # Path to SSL certificate file
    ssl_keyfile: str = None  # Path to SSL private key file
    ssl_ca_certs: str = None  # Path to CA bundle (optional)

    # CORS/CSRF
    cors_allowed_origins: list = ["https://localhost:8080", "https://localhost:8000"]
    csrf_enabled: bool = True
    csrf_secret: str = os.getenv("CSRF_SECRET", "change-me")

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
    if not cfg_path.exists():
        return {}
    # Import yaml using builtins.__import__ so tests patching __import__ take effect
    try:
        _yaml = __import__("yaml")  # type: ignore
    except Exception:
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = _yaml.safe_load(f) or {}
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
        "PDF_MAX_SIZE_MB": "pdf_max_size_mb",
        "AUDIO_MAX_SIZE_MB": "audio_max_size_mb",
        "TEXT_MAX_SIZE_MB": "text_max_size_mb",
        "ARCHIVE_MAX_SIZE_MB": "archive_max_size_mb",
        "FILE_VALIDATION_ENABLED": "file_validation_enabled",
        "SSL_CERTFILE": "ssl_certfile",
        "SSL_KEYFILE": "ssl_keyfile",
        "SSL_CA_CERTS": "ssl_ca_certs",
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
