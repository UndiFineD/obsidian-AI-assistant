import logging
from typing import Callable, Any, Optional

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
