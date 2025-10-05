import logging
from typing import Callable, Any

logger = logging.getLogger("obsidian_ai_assistant")
logging.basicConfig(level=logging.INFO)

def safe_call(fn: Callable, *args, error_msg: str = None, default: Any = None, **kwargs) -> Any:
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        msg = error_msg or f"Error in {fn.__name__}: {e}"
        logger.error(msg)
        return default
