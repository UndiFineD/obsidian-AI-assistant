#!/usr/bin/env python3
"""
File upload validation utilities for secure file handling.

Provides comprehensive validation for:
- File type checking via MIME type and magic bytes
- File size limits
- Path traversal prevention  
- Malicious content detection
- Filename sanitization
"""

import os
import mimetypes
from pathlib import Path

# Optional import for python-magic
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    magic = None
    MAGIC_AVAILABLE = False
from typing import Dict, List, Optional, Tuple, Union
import base64
import hashlib
import re

class FileValidationError(Exception):
    """Custom exception for file validation errors"""
    pass

class FileValidator:
    """Comprehensive file upload validator"""
    
    # Allowed file types with MIME types and magic bytes
    ALLOWED_TYPES = {
        'pdf': {
            'mime_types': ['application/pdf'],
            'magic_bytes': [b'%PDF-'],
            'max_size_mb': 50,
            'extensions': ['.pdf']
        },
        'audio': {
            'mime_types': [
                'audio/wav', 'audio/wave', 'audio/x-wav',
                'audio/webm', 'audio/ogg', 'audio/mp3',
                'audio/mpeg', 'audio/mp4', 'audio/aac'
            ],
            'magic_bytes': [
                b'RIFF', b'OggS', b'ID3', b'\xff\xfb',  # WAV, OGG, MP3
                b'\x1a\x45\xdf\xa3'  # WebM/Matroska
            ],
            'max_size_mb': 25,
            'extensions': ['.wav', '.webm', '.ogg', '.mp3', '.mp4', '.aac']
        },
        'text': {
            'mime_types': [
                'text/plain', 'text/markdown', 'text/x-markdown',
                'application/json', 'text/csv'
            ],
            'magic_bytes': [],  # Text files don't have reliable magic bytes
            'max_size_mb': 10,
            'extensions': ['.txt', '.md', '.json', '.csv']
        },
        'archive': {
            'mime_types': [
                'application/zip', 'application/x-zip-compressed',
                'application/gzip', 'application/x-gzip'
            ],
            'magic_bytes': [
                b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08',  # ZIP variants
                b'\x1f\x8b'  # GZIP
            ],
            'max_size_mb': 100,
            'extensions': ['.zip', '.gz']
        }
    }
    
    # Dangerous file extensions that should never be allowed
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.vbe',
        '.js', '.jse', '.wsf', '.wsh', '.ps1', '.ps1xml', '.ps2', '.ps2xml',
        '.psc1', '.psc2', '.msh', '.msh1', '.msh2', '.mshxml', '.msh1xml',
        '.msh2xml', '.scf', '.lnk', '.inf', '.reg', '.app', '.deb', '.pkg',
        '.dmg', '.iso', '.img', '.bin', '.run', '.action', '.apk', '.jar'
    }
    
    # Maximum path length to prevent path traversal
    MAX_PATH_LENGTH = 260
    MAX_FILENAME_LENGTH = 255
    
    # Windows reserved names
    WINDOWS_RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    def __init__(self, allowed_types: Optional[List[str]] = None):
        """
        Initialize validator with optional type restrictions
        
        Args:
            allowed_types: List of allowed file types from ALLOWED_TYPES keys
        """
        self.allowed_types = allowed_types or list(self.ALLOWED_TYPES.keys())
        
        # Initialize python-magic if available
        if MAGIC_AVAILABLE:
            try:
                self.magic_mime = magic.Magic(mime=True)
                self.magic_available = True
            except Exception:
                print("[FileValidator] Warning: python-magic available but failed to initialize")
                self.magic_available = False
        else:
            print("[FileValidator] Info: python-magic not available, using basic validation")
            self.magic_available = False
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent security issues
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename:
            raise FileValidationError("Filename cannot be empty")
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        # Allow only alphanumeric, dots, hyphens, underscores, and spaces
        sanitized = re.sub(r'[^\w\s\-_\.]', '', filename)
        
        # Replace multiple spaces/dots with single ones
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = re.sub(r'\.+', '.', sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            raise FileValidationError("Filename is invalid after sanitization")
        
        # Check for Windows reserved names
        name_without_ext = os.path.splitext(sanitized)[0].upper()
        if name_without_ext in self.WINDOWS_RESERVED_NAMES:
            sanitized = f"file_{sanitized}"
        
        # Check length
        if len(sanitized) > self.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(sanitized)
            max_name_len = self.MAX_FILENAME_LENGTH - len(ext)
            sanitized = name[:max_name_len] + ext
        
        return sanitized
    
    def validate_path(self, file_path: str) -> str:
        """
        Validate and sanitize file path to prevent path traversal
        
        Args:
            file_path: File path to validate
            
        Returns:
            Sanitized absolute path
            
        Raises:
            FileValidationError: If path is invalid or dangerous
        """
        if not file_path:
            raise FileValidationError("File path cannot be empty")
        
        # Convert to Path object for safer handling
        try:
            path = Path(file_path).resolve()
        except Exception as e:
            raise FileValidationError(f"Invalid file path: {e}")
        
        # Check for path traversal attempts
        import urllib.parse
        
        # Decode URL encoding and normalize
        decoded_path = urllib.parse.unquote(file_path)
        normalized_path = str(path).replace('\\', '/')
        
        # Multiple traversal patterns to check
        traversal_indicators = [
            '..' in decoded_path,
            '..' in file_path,
            '..' in str(path),
            '/..' in decoded_path,
            '/..' in normalized_path,
            '\\..\\' in decoded_path,
            '\\..\\' in str(path),
            normalized_path.startswith('/'),  # Absolute path
            '%2e%2e' in file_path.lower(),  # URL encoded ..
            '....' in file_path,  # Alternative traversal attempts
        ]
        
        if any(traversal_indicators):
            raise FileValidationError("Path traversal detected")
        
        # Check path length
        if len(str(path)) > self.MAX_PATH_LENGTH:
            raise FileValidationError(f"Path too long (max {self.MAX_PATH_LENGTH} characters)")
        
        return str(path)
    
    def detect_file_type(self, file_content: bytes, filename: str) -> Tuple[str, str]:
        """
        Detect file type using multiple methods
        
        Args:
            file_content: File content bytes
            filename: Original filename
            
        Returns:
            Tuple of (detected_type, mime_type)
        """
        # Check magic bytes first (most reliable)
        for file_type, config in self.ALLOWED_TYPES.items():
            for magic_bytes in config['magic_bytes']:
                if file_content.startswith(magic_bytes):
                    return file_type, config['mime_types'][0]
        
        # Use python-magic if available
        if self.magic_available:
            try:
                detected_mime = self.magic_mime.from_buffer(file_content)
                for file_type, config in self.ALLOWED_TYPES.items():
                    if detected_mime in config['mime_types']:
                        return file_type, detected_mime
            except Exception:
                pass
        
        # Fallback to extension-based detection
        extension = Path(filename).suffix.lower()
        for file_type, config in self.ALLOWED_TYPES.items():
            if extension in config['extensions']:
                return file_type, config['mime_types'][0]
        
        # Use mimetypes module as last resort
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            for file_type, config in self.ALLOWED_TYPES.items():
                if mime_type in config['mime_types']:
                    return file_type, mime_type
        
        raise FileValidationError(f"Unsupported file type for {filename}")
    
    def validate_file_size(self, file_content: bytes, file_type: str) -> None:
        """
        Validate file size against type-specific limits
        
        Args:
            file_content: File content bytes
            file_type: Detected file type
            
        Raises:
            FileValidationError: If file is too large
        """
        size_mb = len(file_content) / (1024 * 1024)
        max_size = self.ALLOWED_TYPES[file_type]['max_size_mb']
        
        if size_mb > max_size:
            raise FileValidationError(
                f"File too large: {size_mb:.1f}MB (max {max_size}MB for {file_type} files)"
            )
    
    def check_dangerous_content(self, file_content: bytes, filename: str) -> None:
        """
        Check for potentially dangerous content
        
        Args:
            file_content: File content bytes  
            filename: Filename
            
        Raises:
            FileValidationError: If dangerous content detected
        """
        # Check file extension
        extension = Path(filename).suffix.lower()
        if extension in self.DANGEROUS_EXTENSIONS:
            raise FileValidationError(f"Dangerous file extension: {extension}")
        
        # Check for embedded executables in PDFs
        if filename.lower().endswith('.pdf'):
            dangerous_pdf_content = [
                b'/JavaScript', b'/JS', b'/AcroForm', b'/XFA',
                b'/EmbeddedFile', b'/Launch', b'/SubmitForm'
            ]
            for dangerous in dangerous_pdf_content:
                if dangerous in file_content:
                    raise FileValidationError("PDF contains potentially dangerous content")
        
        # Check for null bytes (can indicate binary injection)
        if b'\x00' in file_content[:1024] and not any(
            file_content.startswith(magic) for config in self.ALLOWED_TYPES.values()
            for magic in config['magic_bytes'] if magic
        ):
            raise FileValidationError("File contains null bytes (potential binary injection)")
    
    def validate_file(self, file_content: bytes, filename: str, 
                     file_path: Optional[str] = None) -> Dict[str, any]:
        """
        Comprehensive file validation
        
        Args:
            file_content: File content bytes
            filename: Original filename
            file_path: Optional file path to validate
            
        Returns:
            Dict with validation results and file metadata
            
        Raises:
            FileValidationError: If validation fails
        """
        result = {
            'valid': False,
            'sanitized_filename': None,
            'sanitized_path': None,
            'file_type': None,
            'mime_type': None,
            'size_bytes': len(file_content),
            'size_mb': len(file_content) / (1024 * 1024),
            'hash_sha256': hashlib.sha256(file_content).hexdigest(),
            'warnings': []
        }
        
        try:
            # 1. Sanitize filename
            result['sanitized_filename'] = self.sanitize_filename(filename)
            
            # 2. Validate path if provided
            if file_path:
                result['sanitized_path'] = self.validate_path(file_path)
            
            # 3. Detect file type
            file_type, mime_type = self.detect_file_type(file_content, filename)
            result['file_type'] = file_type
            result['mime_type'] = mime_type
            
            # 4. Check if file type is allowed
            if file_type not in self.allowed_types:
                raise FileValidationError(f"File type '{file_type}' not allowed")
            
            # 5. Validate file size
            self.validate_file_size(file_content, file_type)
            
            # 6. Check for dangerous content
            self.check_dangerous_content(file_content, filename)
            
            # 7. Additional type-specific validation
            if file_type == 'pdf':
                self._validate_pdf_content(file_content, result)
            elif file_type == 'audio':
                self._validate_audio_content(file_content, result)
            
            result['valid'] = True
            
        except FileValidationError as e:
            result['error'] = str(e)
            raise
        
        return result
    
    def _validate_pdf_content(self, content: bytes, result: Dict) -> None:
        """Additional PDF-specific validation"""
        if not content.startswith(b'%PDF-'):
            result['warnings'].append("PDF header not found at beginning of file")
        
        # Check PDF version
        if len(content) > 8:
            version_line = content[:20].decode('ascii', errors='ignore')
            if '%PDF-1.4' in version_line or '%PDF-1.3' in version_line:
                result['warnings'].append("Old PDF version detected (may have security issues)")
    
    def _validate_audio_content(self, content: bytes, result: Dict) -> None:
        """Additional audio-specific validation"""
        # Basic audio format validation
        if content.startswith(b'RIFF') and b'WAVE' not in content[:20]:
            result['warnings'].append("RIFF file that may not be valid audio")


# Helper functions for common validation scenarios

def validate_base64_audio(audio_data: str, max_size_mb: float = 25) -> Dict[str, any]:
    """
    Validate base64-encoded audio data
    
    Args:
        audio_data: Base64-encoded audio
        max_size_mb: Maximum size in MB
        
    Returns:
        Validation result dict
    """
    try:
        # Decode base64
        audio_bytes = base64.b64decode(audio_data)
    except Exception as e:
        raise FileValidationError(f"Invalid base64 audio data: {e}")
    
    # Create validator for audio only
    validator = FileValidator(allowed_types=['audio'])
    
    # Override size limit if specified
    if max_size_mb != 25:
        validator.ALLOWED_TYPES['audio']['max_size_mb'] = max_size_mb
    
    return validator.validate_file(audio_bytes, 'audio.webm')


def validate_pdf_path(pdf_path: str) -> Dict[str, any]:
    """
    Validate PDF file from filesystem path
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Validation result dict
    """
    validator = FileValidator(allowed_types=['pdf'])
    
    # Read file content
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
    except Exception as e:
        raise FileValidationError(f"Cannot read file {pdf_path}: {e}")
    
    filename = os.path.basename(pdf_path)
    return validator.validate_file(content, filename, pdf_path)


# Configuration for environment-based limits
def get_file_size_limits() -> Dict[str, int]:
    """Get file size limits from environment variables"""
    return {
        'pdf_max_mb': int(os.getenv('PDF_MAX_SIZE_MB', '50')),
        'audio_max_mb': int(os.getenv('AUDIO_MAX_SIZE_MB', '25')),
        'text_max_mb': int(os.getenv('TEXT_MAX_SIZE_MB', '10')),
        'archive_max_mb': int(os.getenv('ARCHIVE_MAX_SIZE_MB', '100'))
    }
