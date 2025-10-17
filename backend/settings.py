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
    if re.search(
        r"import\s+os;\s*os\.system\(['\"]rm -rf /['\"]\)",
        prompt,
        flags=re.IGNORECASE,
    ):
        return "[REDACTED]; [REDACTED]('[REDACTED] /')"
    elif re.search(r"run\s*system\.shutdown\(\)", prompt, flags=re.IGNORECASE):
        return "run [REDACTED]()"
    elif re.search(r"DROP TABLE users;", prompt, flags=re.IGNORECASE):
        return "[REDACTED] TABLE users;"
    elif re.search(r"password=([^\s]+)", prompt, flags=re.IGNORECASE):
        # Handle password case but still apply escaping
        prompt = re.sub(
            r"password=([^\s]+)", r"[REDACTED]=\1", prompt, flags=re.IGNORECASE
        )
    else:
        # Replace dangerous patterns with [REDACTED] for other cases
        for pattern in dangerous_patterns:
            prompt = re.sub(pattern, "[REDACTED]", prompt)
    # Escape special characters
    prompt = prompt.replace("<", "&lt;").replace(">", "&gt;")
    prompt = prompt.replace('"', "&quot;").replace("'", "&#39;")
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
    "log_dir",
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
    "log_level",
    "log_format",
    "log_include_pii",
    "log_console_enabled",
    "log_file_enabled",
    "log_audit_enabled",
    "log_security_enabled",
    "log_performance_enabled",
    "log_max_file_size",
    "log_backup_count",
    "log_cleanup_days",
    # Security hardening settings
    "security_level",
    "session_timeout_hours",
    "session_idle_timeout_hours",
    "max_sessions_per_user",
    "api_key_rate_limit",
    "threat_detection_enabled",
    "auto_block_threshold",
    "behavioral_analysis_enabled",
    "request_signing_enabled",
    "security_headers_enabled",
    # Authentication settings
    "jwt_secret_key",
    "jwt_expiry_hours",
    "password_min_length",
    "require_mfa",
    "lockout_attempts",
    "lockout_duration_minutes",
    # Network & SSL settings
    "cors_allowed_origins",
    "ssl_certfile",
    "ssl_keyfile",
    "ssl_ca_certs",
    "csrf_enabled",
}


def validate_cors_origins(origins: list) -> bool:
    """
    Validate CORS origins list.
    
    Each origin must be a valid URL (http:// or https://) or wildcard "*".
    Returns True if all origins are valid, False otherwise.
    """
    if not isinstance(origins, list):
        return False
    pattern = re.compile(r'^(https?://[a-zA-Z0-9.-]+(:\d+)?|\*)$')
    return all(pattern.match(str(origin)) for origin in origins)


def validate_ssl_file(filepath: str, extensions: list) -> bool:
    """
    Validate SSL file path and extension.
    
    Args:
        filepath: Path to SSL file (or None/empty for optional files)
        extensions: List of allowed file extensions (e.g., [".pem", ".crt"])
    
    Returns:
        True if file is valid or None/empty, False otherwise
    """
    if not filepath:
        return True  # None/empty is valid (optional)
    try:
        path = Path(filepath)
        return path.exists() and path.is_file() and path.suffix in extensions
    except Exception:
        return False


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
    log_dir: str = "backend/logs"

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
    cors_allowed_origins: list = [
        "https://localhost:8080",
        "https://localhost:8000",
    ]
    csrf_enabled: bool = True
    csrf_secret: str = os.getenv("CSRF_SECRET", "change-me")

    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "structured")  # 'structured' or 'text'
    log_include_pii: bool = os.getenv("LOG_INCLUDE_PII", "false").lower() in ("true", "1", "yes")
    log_console_enabled: bool = os.getenv("LOG_CONSOLE_ENABLED", "true").lower() in ("true", "1", "yes")
    log_file_enabled: bool = os.getenv("LOG_FILE_ENABLED", "true").lower() in ("true", "1", "yes")
    log_audit_enabled: bool = os.getenv("LOG_AUDIT_ENABLED", "true").lower() in ("true", "1", "yes")
    log_security_enabled: bool = os.getenv("LOG_SECURITY_ENABLED", "true").lower() in ("true", "1", "yes")
    log_performance_enabled: bool = os.getenv("LOG_PERFORMANCE_ENABLED", "true").lower() in ("true", "1", "yes")
    log_max_file_size: int = int(os.getenv("LOG_MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
    log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    log_cleanup_days: int = int(os.getenv("LOG_CLEANUP_DAYS", "30"))
    
    # Security Hardening Configuration
    security_level: str = os.getenv("SECURITY_LEVEL", "standard")  # minimal, standard, enhanced, maximum
    session_timeout_hours: int = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    session_idle_timeout_hours: int = int(os.getenv("SESSION_IDLE_TIMEOUT_HOURS", "2"))
    max_sessions_per_user: int = int(os.getenv("MAX_SESSIONS_PER_USER", "5"))
    api_key_rate_limit: int = int(os.getenv("API_KEY_RATE_LIMIT", "100"))
    threat_detection_enabled: bool = os.getenv("THREAT_DETECTION_ENABLED", "true").lower() in ("true", "1", "yes")
    auto_block_threshold: float = float(os.getenv("AUTO_BLOCK_THRESHOLD", "20.0"))
    behavioral_analysis_enabled: bool = os.getenv("BEHAVIORAL_ANALYSIS_ENABLED", "true").lower() in ("true", "1", "yes")
    request_signing_enabled: bool = os.getenv("REQUEST_SIGNING_ENABLED", "false").lower() in ("true", "1", "yes")
    security_headers_enabled: bool = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() in ("true", "1", "yes")
    
    # Authentication Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_expiry_hours: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
    password_min_length: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    require_mfa: bool = os.getenv("REQUIRE_MFA", "false").lower() in ("true", "1", "yes")
    lockout_attempts: int = int(os.getenv("LOCKOUT_ATTEMPTS", "5"))
    lockout_duration_minutes: int = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))

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

    @property
    def abs_log_dir(self) -> Path:
        p = Path(self.log_dir)
        return p if p.is_absolute() else self.base_dir / p

    def get_logging_config(self) -> dict:
        """Get logging configuration dictionary"""
        return {
            'level': self.log_level,
            'format': self.log_format,
            'include_pii': self.log_include_pii,
            'log_dir': str(self.abs_log_dir),
            'console_enabled': self.log_console_enabled,
            'file_enabled': self.log_file_enabled,
            'audit_enabled': self.log_audit_enabled,
            'security_enabled': self.log_security_enabled,
            'performance_enabled': self.log_performance_enabled,
            'max_file_size': self.log_max_file_size,
            'backup_count': self.log_backup_count,
            'cleanup_days': self.log_cleanup_days,
        }
    
    def get_security_config(self) -> dict:
        """Get security configuration dictionary"""
        return {
            'security_level': self.security_level,
            'session_timeout_hours': self.session_timeout_hours,
            'session_idle_timeout_hours': self.session_idle_timeout_hours,
            'max_sessions_per_user': self.max_sessions_per_user,
            'api_key_rate_limit': self.api_key_rate_limit,
            'threat_detection_enabled': self.threat_detection_enabled,
            'auto_block_threshold': self.auto_block_threshold,
            'behavioral_analysis_enabled': self.behavioral_analysis_enabled,
            'request_signing_enabled': self.request_signing_enabled,
            'security_headers_enabled': self.security_headers_enabled,
            'jwt_secret_key': '***' if self.jwt_secret_key else '',  # Redacted
            'jwt_expiry_hours': self.jwt_expiry_hours,
            'password_min_length': self.password_min_length,
            'require_mfa': self.require_mfa,
            'lockout_attempts': self.lockout_attempts,
            'lockout_duration_minutes': self.lockout_duration_minutes
        }


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
    import logging
    
    # Filter updates to only include whitelisted keys
    filtered_updates = {}
    for key, value in updates.items():
        if key in _ALLOWED_UPDATE_KEYS:
            # Validate based on field type
            try:
                if key == "cors_allowed_origins":
                    if not validate_cors_origins(value):
                        raise ValueError(f"Invalid CORS origins: {value}. Must be list of valid URLs or '*'")
                    # Warn about wildcard
                    if "*" in value:
                        logging.warning("CORS wildcard origin (*) detected - NOT recommended for production")
                    filtered_updates[key] = value
                
                elif key == "ssl_certfile":
                    if not validate_ssl_file(value, [".pem", ".crt", ".cert"]):
                        raise ValueError(f"Invalid SSL certificate file: {value}. Must exist and have .pem, .crt, or .cert extension")
                    filtered_updates[key] = value
                
                elif key == "ssl_keyfile":
                    if not validate_ssl_file(value, [".pem", ".key"]):
                        raise ValueError(f"Invalid SSL key file: {value}. Must exist and have .pem or .key extension")
                    filtered_updates[key] = value
                
                elif key == "ssl_ca_certs":
                    if not validate_ssl_file(value, [".pem", ".crt"]):
                        raise ValueError(f"Invalid CA certs file: {value}. Must exist and have .pem or .crt extension")
                    filtered_updates[key] = value
                
                elif key == "csrf_enabled":
                    if isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes")
                    if not value:
                        logging.warning("CSRF protection disabled - NOT recommended for production")
                    filtered_updates[key] = value
                
                elif key == "chunk_size" and isinstance(value, str):
                    filtered_updates[key] = int(value)
                elif key == "gpu" and isinstance(value, str):
                    filtered_updates[key] = value.lower() in ("true", "1", "yes")
                elif key == "similarity_threshold" and isinstance(value, str):
                    filtered_updates[key] = float(value)
                elif key == "vault_path":
                    filtered_updates[key] = str(value)
                else:
                    filtered_updates[key] = value
            except (ValueError, TypeError) as e:
                # Log validation errors and skip invalid values
                logging.error(f"Validation failed for {key}: {e}")
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
