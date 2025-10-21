import pytest

from agent import utils


def test_utils_exists():
    assert hasattr(utils, "safe_call")
