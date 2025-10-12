import logging
import re
from typing import Callable, Any, Optional, Mapping, Sequence

# Use __name__ to create a logger that is part of the package's hierarchy.
# The application's entry point should be responsible for configuring logging.
logger = logging.getLogger(__name__)


def safe_call(
    fn: Callable, *args, error_msg: Optional[str] = None, default: Any = None, **kwargs
) -> Any:
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        msg = error_msg or f"Error in {fn.__name__}: {e}"
        # Log the full exception traceback for better debugging, without crashing the app.
        logger.error(msg, exc_info=True)
        return default


# --- Privacy & PII Redaction Utilities ---
_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s-]?\d{3,4}[\s-]?\d{3,4}\b")
_IPV4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
_TOKEN_RE = re.compile(r"\b(?:sk|hf|ghp|gho|pat|token)[-_][A-Za-z0-9]{10,}\b", re.IGNORECASE)
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_WIN_PATH_RE = re.compile(r"[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*")
_NIX_PATH_RE = re.compile(r"(?:/[^\s/:*?\"'<>|]+)+")


def redact_text(text: str) -> str:
    """Redact common PII/secrets patterns from text.

    This is best-effort and not exhaustive. Returns the redacted text.
    """
    if not text:
        return text
    redacted = text
    for pattern in (_EMAIL_RE, _PHONE_RE, _IPV4_RE, _TOKEN_RE, _SSN_RE, _WIN_PATH_RE, _NIX_PATH_RE):
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def redact_data(obj: Any) -> Any:
    """Recursively redact PII from strings inside mappings/sequences.

    - Strings are passed through redact_text
    - Dict keys are preserved; values are redacted
    - Lists/tuples are redacted element-wise
    """
    try:
        if obj is None:
            return obj
        if isinstance(obj, str):
            return redact_text(obj)
        if isinstance(obj, Mapping):
            return {k: redact_data(v) for k, v in obj.items()}
        if isinstance(obj, Sequence) and not isinstance(obj, (bytes, bytearray)):
            return [redact_data(v) for v in obj]
        return obj
    except Exception:
        # Best-effort; if redaction fails, return original object
        return obj
