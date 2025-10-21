"""
API Key Management Module
Handles API key generation, rotation, validation, and storage for secure access control.
"""

import hashlib
import secrets
import time
from typing import Dict, Optional

from fastapi import HTTPException

# In-memory store for demonstration (replace with persistent storage in production)
_API_KEYS: Dict[str, Dict] = {}


class APIKeyManager:
    @staticmethod
    def generate_key() -> str:
        key = secrets.token_urlsafe(32)
        hashed = hashlib.sha256(key.encode()).hexdigest()
        _API_KEYS[hashed] = {"created": time.time(), "active": True}
        return key

    @staticmethod
    def rotate_key(old_key: str) -> str:
        old_hashed = hashlib.sha256(old_key.encode()).hexdigest()
        if old_hashed not in _API_KEYS or not _API_KEYS[old_hashed]["active"]:
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")
        # Deactivate old key
        _API_KEYS[old_hashed]["active"] = False
        # Generate new key
        return APIKeyManager.generate_key()

    @staticmethod
    def validate_key(key: str) -> bool:
        hashed = hashlib.sha256(key.encode()).hexdigest()
        return hashed in _API_KEYS and _API_KEYS[hashed]["active"]

    @staticmethod
    def deactivate_key(key: str) -> None:
        hashed = hashlib.sha256(key.encode()).hexdigest()
        if hashed in _API_KEYS:
            _API_KEYS[hashed]["active"] = False

    @staticmethod
    def get_key_info(key: str) -> Optional[Dict]:
        hashed = hashlib.sha256(key.encode()).hexdigest()
        return _API_KEYS.get(hashed)
