import pytest
from backend import exception_handlers

def test_exception_handlers_exists():
    assert hasattr(exception_handlers, "HTTPException")
