# tests/backend/test_security.py
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet

# 🎵 Work it FASTER - use proper package imports! 🎵
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.security import KEY, decrypt_data, encrypt_data, fernet


class TestSecurity:
    """Test suite for the security module."""

    def test_key_is_valid_format(self):
        """Test that the encryption key is in valid Fernet format."""
        # KEY should be a 32-byte base64url-encoded key
        assert isinstance(KEY, bytes)
        assert len(KEY) > 0
        # Should be able to create Fernet instance with the key
        test_fernet = Fernet(KEY)
        assert test_fernet is not None

    def test_fernet_instance_created(self):
        """Test that Fernet instance is properly created."""
        assert fernet is not None
        assert isinstance(fernet, Fernet)

    def test_encrypt_data_basic_string(self):
        """Test basic string encryption."""
        test_data = "Hello, World!"
        encrypted = encrypt_data(test_data)
        assert isinstance(encrypted, bytes)
        assert encrypted != test_data.encode()  # Should be different from original
        assert len(encrypted) > len(test_data)  # Encrypted data should be longer

    def test_encrypt_data_empty_string(self):
        """Test encryption of empty string."""
        test_data = ""
        encrypted = encrypt_data(test_data)
        assert isinstance(encrypted, bytes)
        assert len(encrypted) > 0  # Even empty strings produce encrypted output

    def test_encrypt_data_unicode_characters(self):
        """Test encryption of unicode characters."""
        test_data = "Hello 世界! 🌍 Émojis & spëciàl cháracters"
        encrypted = encrypt_data(test_data)
        assert isinstance(encrypted, bytes)
        assert encrypted != test_data.encode()

    def test_encrypt_data_long_string(self):
        """Test encryption of long strings."""
        test_data = "A" * 10000  # 10KB string
        encrypted = encrypt_data(test_data)
        assert isinstance(encrypted, bytes)
        assert len(encrypted) > len(test_data)

    def test_encrypt_data_special_characters(self):
        """Test encryption with special characters and symbols."""
        test_data = "!@#$%^&*()_+-=[]{}|;':\",./<>?\n\t\r"
        encrypted = encrypt_data(test_data)
        assert isinstance(encrypted, bytes)
        assert encrypted != test_data.encode()

    def test_decrypt_data_basic(self):
        """Test basic data decryption."""
        test_data = "Hello, World!"

        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)

        assert decrypted == test_data
        assert isinstance(decrypted, str)

    def test_decrypt_data_empty_string(self):
        """Test decryption of encrypted empty string."""
        test_data = ""

        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)

        assert decrypted == test_data

    def test_decrypt_data_unicode(self):
        """Test decryption of unicode characters."""
        test_data = "Hello 世界! 🌍 Émojis & spëciàl cháracters"

        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)

        assert decrypted == test_data

    def test_decrypt_data_long_string(self):
        """Test decryption of long strings."""
        test_data = "B" * 5000

        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)

        assert decrypted == test_data

    def test_encrypt_decrypt_roundtrip(self):
        """Test multiple encrypt/decrypt operations."""
        test_cases = [
            "Simple string",
            "",
            "🔐 Security test with emojis 🛡️",
            "Line 1\nLine 2\tTabbed\rCarriage return",
            '{"json": "data", "numbers": [1, 2, 3]}',
            "SQL: SELECT * FROM users WHERE id = 1;",
            "<html><body>HTML content</body></html>",
            "A" * 1000,
        ]

        for test_data in test_cases:
            encrypted = encrypt_data(test_data)
            decrypted = decrypt_data(encrypted)
            assert decrypted == test_data, f"Roundtrip failed for: {test_data[:50]}"

    def test_different_encryptions_same_data(self):
        """Test that same data encrypts to different ciphertexts (nonce/IV)."""
        test_data = "Same data for multiple encryptions"
        encrypted1 = encrypt_data(test_data)
        encrypted2 = encrypt_data(test_data)
        # Should produce different ciphertexts due to random nonce/IV
        assert encrypted1 != encrypted2
        # But both should decrypt to same original data
        decrypted1 = decrypt_data(encrypted1)
        decrypted2 = decrypt_data(encrypted2)
        assert decrypted1 == test_data
        assert decrypted2 == test_data

    def test_decrypt_invalid_data_returns_none(self):
        """Test that decrypting invalid data returns None."""
        invalid_encrypted_data = b"invalid_encrypted_data_123"

        result = decrypt_data(invalid_encrypted_data)
        assert result is None

    def test_decrypt_empty_bytes_returns_none(self):
        """Test that decrypting empty bytes returns None."""
        result = decrypt_data(b"")
        assert result is None

    def test_decrypt_malformed_token_returns_none(self):
        """Test that decrypting malformed tokens returns None."""
        # Create a token that looks like it might be valid but isn't
        malformed_tokens = [
            b"malformed",
            b"gAAAAABh" + b"x" * 50,  # Looks like Fernet but wrong
            b"not_base64_encoded_properly",
        ]

        for token in malformed_tokens:
            result = decrypt_data(token)
            assert result is None

    def test_encrypt_data_input_type_validation(self):
        """Test that encrypt_data handles input type validation."""
        # Should work with strings
        result = encrypt_data("valid string")
        assert isinstance(result, bytes)
        # Test with non-string inputs (should handle or raise appropriate error)
        invalid_inputs = [123, None, [], {}]
        for invalid_input in invalid_inputs:
            with pytest.raises((AttributeError, TypeError)):
                encrypt_data(invalid_input)

    def test_decrypt_data_input_type_validation(self):
        """Test that decrypt_data handles input type validation."""
        # Should work with bytes
        valid_encrypted = encrypt_data("test")
        result = decrypt_data(valid_encrypted)
        assert isinstance(result, str)
        # Test with non-bytes inputs should return None
        invalid_inputs = ["string", 123, None, []]
        for invalid_input in invalid_inputs:
            result = decrypt_data(invalid_input)
            assert result is None

    @patch("backend.security.fernet")
    def test_encrypt_data_uses_global_fernet(self, mock_fernet):
        """Test that encrypt_data uses the global fernet instance."""
        mock_fernet.encrypt.return_value = b"mocked_encrypted_data"

        result = encrypt_data("test data")

        mock_fernet.encrypt.assert_called_once_with("test data".encode())
        assert result == b"mocked_encrypted_data"

    @patch("backend.security.fernet")
    def test_decrypt_data_uses_global_fernet(self, mock_fernet):
        """Test that decrypt_data uses the global fernet instance."""
        mock_fernet.decrypt.return_value = b"decrypted_data"

        result = decrypt_data(b"encrypted_data")

        mock_fernet.decrypt.assert_called_once_with(b"encrypted_data")
        assert result == "decrypted_data"

    def test_key_consistency(self):
        """Test that the same KEY is used consistently."""
        # The KEY should remain constant during runtime
        from backend.security import KEY as imported_key

        assert imported_key == KEY
        # Fernet instance should be created with this key
        test_fernet = Fernet(KEY)
        # Should be able to decrypt data encrypted with module's fernet
        test_data = "consistency test"
        encrypted_with_module = encrypt_data(test_data)
        decrypted_with_test = test_fernet.decrypt(encrypted_with_module).decode()
        assert decrypted_with_test == test_data


class TestSecurityIntegration:
    """Integration tests for security module."""

    def test_security_with_json_data(self):
        """Test encryption/decryption with JSON-like data."""
        json_data = '{"user_id": 12345, "session": "abc-def-123", "permissions": ["read", "write"]}'

        encrypted = encrypt_data(json_data)
        decrypted = decrypt_data(encrypted)

        assert decrypted == json_data

    def test_security_with_sensitive_data_patterns(self):
        """Test encryption with patterns that might appear in sensitive data."""
        sensitive_patterns = [
            "password=secret123",
            "api_key=sk-1234567890abcdef",
            "credit_card=4111-1111-1111-1111",
            "ssn=123-45-6789",
            "email=user@example.com",
            "phone=+1-555-123-4567",
        ]

        for pattern in sensitive_patterns:
            encrypted = encrypt_data(pattern)
            decrypted = decrypt_data(encrypted)

            assert decrypted == pattern
            assert pattern not in str(
                encrypted
            )  # Sensitive data not visible in encrypted form

    def test_security_performance_large_data(self):
        """Test encryption/decryption performance with larger datasets."""
        import time

        # Test with moderately large data (100KB)
        large_data = "Performance test data " * 5000

        start_time = time.time()
        encrypted = encrypt_data(large_data)
        encrypt_time = time.time() - start_time

        start_time = time.time()
        decrypted = decrypt_data(encrypted)
        decrypt_time = time.time() - start_time

        assert decrypted == large_data

        # Performance should be reasonable (less than 1 second for 100KB
        assert encrypt_time < 1.0
        assert decrypt_time < 1.0

    def test_security_module_constants_immutable(self):
        """Test that security constants cannot be easily modified."""
        original_key = KEY
        original_fernet = fernet

        # KEY and fernet should remain the same after import
        from backend.security import KEY as key_check
        from backend.security import fernet as fernet_check

        assert key_check == original_key
        assert fernet_check == original_fernet


if __name__ == "__main__":
    pytest.main([__file__])
