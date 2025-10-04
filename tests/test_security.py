import os
import sys
import unittest
from cryptography.fernet import InvalidToken

# Add project root to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

# Import after path setup
from backend.security import encrypt_data, decrypt_data  # noqa: E402


class TestSecurity(unittest.TestCase):
    def test_encrypt_decrypt_round_trip(self):
        """Test data encryption and decryption."""
        test_data = [
            "Simple text",
            "Text with numbers 123",
            "Text with symbols !@#$%^&*()",
            "Unicode text: こんにちは, 안녕하세요",
            "Multi-line\ntext\nwith\nbreaks",
            "Very " * 1000  # Long text
        ]
        
        for data in test_data:
            # Encrypt
            encrypted = encrypt_data(data)
            self.assertIsInstance(encrypted, bytes)
            self.assertNotEqual(encrypted, data.encode())
            
            # Decrypt
            decrypted = decrypt_data(encrypted)
            self.assertEqual(decrypted, data)

    def test_empty_string(self):
        """Test handling empty string."""
        encrypted = encrypt_data("")
        decrypted = decrypt_data(encrypted)
        self.assertEqual(decrypted, "")

    def test_invalid_input(self):
        """Test error handling for invalid input."""
        # Test invalid encrypted data
        with self.assertRaises(InvalidToken):
            decrypt_data(b"invalid data")
            
        # Test non-bytes input
        with self.assertRaises(InvalidToken):
            decrypt_data("not bytes")


if __name__ == '__main__':
    unittest.main()
