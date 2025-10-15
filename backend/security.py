import logging
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

# --- Key Management ---
# For production, set the ENCRYPTION_KEY environment variable.
# You can generate a new key with: Fernet.generate_key().decode()
_DEFAULT_KEY = b"ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg="
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "").encode()

if not ENCRYPTION_KEY:
    logger.warning(
        "ENCRYPTION_KEY environment variable not set. "
        "Using default key for development."
    )
    ENCRYPTION_KEY = _DEFAULT_KEY

# Expose KEY for backward compatibility with tests
KEY = ENCRYPTION_KEY

try:
    fernet: Optional[Fernet] = Fernet(ENCRYPTION_KEY)
except (ValueError, TypeError) as e:
    logger.critical(
        "Invalid ENCRYPTION_KEY. It must be a 32-byte URL-safe "
        "base64-encoded string. Error: %s",
        e,
    )
    # Fallback to a default, non-functional fernet instance to avoid crashing on import.
    fernet = None


def encrypt_data(data: str) -> bytes:
    """
    Encrypts a string using the global Fernet instance.

    Args:
        data: The string to encrypt.

    Returns:
        The encrypted data as bytes.
    """
    if fernet is None:
        raise RuntimeError("Encryption service is not available due to an invalid key.")
    return fernet.encrypt(data.encode())


def decrypt_data(data: bytes) -> Optional[str]:
    """
    Decrypts data using the global Fernet instance.
    Returns None if decryption fails.
    """
    if fernet is None:
        logger.error("Decryption failed: Encryption service is not available.")
        return None
    try:
        return fernet.decrypt(data).decode()
    except (InvalidToken, TypeError, AttributeError):
        logger.warning("Decryption failed: Invalid or tampered token provided.")
        return None
