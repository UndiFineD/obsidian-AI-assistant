"""
Runtime dependency bootstrapper for the backend.

This module provides best-effort installation of a minimal set of Python
packages required to start the API. It avoids hard failures by catching
errors and returning status for logging.

Notes:
- Installs are done via pip as a subprocess to respect the active environment.
- We keep the minimal list small to reduce friction on fresh setups.
- Heavy ML deps (torch, sentence-transformers, chromadb) are optional
  and handled lazily by the relevant modules.
"""

from __future__ import annotations

import sys
import subprocess
from typing import List, Tuple


# All required packages for backend and indexing
REQUIRED_PACKAGES = [
    "fastapi>=0.104.1",
    "uvicorn>=0.24.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "python-multipart>=0.0.6",
    "readability-lxml>=0.8.1",
    "pypdf>=3.0.0",
    "beautifulsoup4>=4.10.0",
    "lxml>=4.9.0",
    "cssselect>=1.1.0",
    "chardet>=4.0.0",
    "numpy>=1.24.0",
]


def _run(cmd: List[str]) -> Tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out
    except Exception as e:
        return 1, f"subprocess error: {e}"


def ensure_minimal_dependencies() -> bool:
    """
    Ensure all required backend dependencies are available. If an import fails, attempt to
    install via pip and retry imports. Returns True if all imports succeed at the end.
    """
    ok = True

    # Map top-level import names to pip specs
    checks = [
        ("fastapi", "fastapi>=0.104.1"),
        ("uvicorn", "uvicorn>=0.24.0"),
        ("requests", "requests>=2.31.0"),
        ("python_dotenv", "python-dotenv>=1.0.0"),
        ("python_multipart", "python-multipart>=0.0.6"),
        ("readability", "readability-lxml>=0.8.1"),
        ("pypdf", "pypdf>=3.0.0"),
        ("bs4", "beautifulsoup4>=4.10.0"),
        ("lxml", "lxml>=4.9.0"),
        ("cssselect", "cssselect>=1.1.0"),
        ("chardet", "chardet>=4.0.0"),
        ("numpy", "numpy>=1.24.0"),
        ("huggingface_hub", "huggingface_hub>=0.20.0"),
    ]

    def _try_import(name: str) -> bool:
        try:
            __import__(name)
            return True
        except Exception:
            return False

    for mod, spec in checks:
        if not _try_import(mod):
            code, out = _run([sys.executable, "-m", "pip", "install", spec])
            if code != 0 or not _try_import(mod):
                print(f"[deps] Failed to install {spec}: {out}")
                ok = False
    return ok


def optional_ml_hint() -> str:
    return (
        "Optional ML dependencies not installed. Some features may be disabled.\n"
        "To enable embeddings and local models, install: torch, sentence-transformers, chromadb, transformers, accelerate."
    )
