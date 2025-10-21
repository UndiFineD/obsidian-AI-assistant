# Configuration Field Coverage Analysis

## Current State

**Total Settings Fields**: 53 fields in Settings class
**Allowed Update Keys**: 45 fields in _ALLOWED_UPDATE_KEYS
**Missing from _ALLOWED_UPDATE_KEYS**: 8 fields

## Missing Fields Analysis

### 1. Fields NOT in _ALLOWED_UPDATE_KEYS

| Field Name | Type | Default | Should Allow Updates? | Reason |
|------------|------|---------|------------------------|--------|
| `agent_url` | str | http://127.0.0.1:8000 | ❌ NO | Derived from api_port, changing directly could cause inconsistency |
| `project_root` | str | auto-detected | ❌ NO | System-level path, should not be user-configurable at runtime |
| `cors_allowed_origins` | list | [...] | ✅ YES | Users may need to add custom origins for integrations |
| `csrf_enabled` | bool | True | ⚠️ MAYBE | Security-critical, but could allow disabling for specific use cases |
| `csrf_secret` | str | env var | ⚠️ MAYBE | Security-critical, but should be rotatable via API |
| `ssl_certfile` | str | None | ✅ YES | Users need to configure SSL certificates for HTTPS |
| `ssl_keyfile` | str | None | ✅ YES | Users need to configure SSL private keys for HTTPS |
| `ssl_ca_certs` | str | None | ✅ YES | Users may need to specify CA bundle for enterprise environments |

### 2. Recommendation Summary

**Add to _ALLOWED_UPDATE_KEYS** (5 fields):
- `cors_allowed_origins` - Required for integration flexibility
- `ssl_certfile` - Required for HTTPS setup
- `ssl_keyfile` - Required for HTTPS setup
- `ssl_ca_certs` - Required for enterprise CA bundles
- `csrf_enabled` - Allow toggling for development/testing (with warning)

**Keep Protected** (3 fields):
- `agent_url` - Derived value, use api_port instead
- `project_root` - System path, immutable
- `csrf_secret` - Use dedicated rotation endpoint instead

## Validation Requirements

### New Fields to Validate

1. **cors_allowed_origins** (list of strings)
   - Must be valid URLs or wildcard patterns
   - Pattern: `https?://[a-zA-Z0-9.-]+(:\d+)?` or `*`
   - Example: `["https://app.example.com", "https://localhost:8080"]`

2. **ssl_certfile** (string path)
   - Must be valid file path
   - File must exist and be readable
   - Must be .pem, .crt, or .cert file

3. **ssl_keyfile** (string path)
   - Must be valid file path
   - File must exist and be readable
   - Must be .pem or .key file

4. **ssl_ca_certs** (string path)
   - Must be valid file path or None
   - File must exist and be readable
   - Must be .pem or .crt file

5. **csrf_enabled** (boolean)
   - Must be boolean
   - Log warning if disabled in production

## Documentation Requirements

### Field Documentation Format

Each configurable field should have:
1. **Description** - What the field controls
2. **Type** - Data type and constraints
3. **Default** - Default value
4. **Validation** - Validation rules
5. **Examples** - Usage examples
6. **Security Notes** - Any security implications

### Example Documentation

```python
# CORS Configuration
cors_allowed_origins: list
    Description: List of allowed origins for CORS (Cross-Origin Resource Sharing)
    Type: List[str] - URLs or wildcard patterns
    Default: ["https://localhost:8080", "https://localhost:8000"]
    Validation: 
        - Each origin must be valid URL or "*"
        - Pattern: https?://[a-zA-Z0-9.-]+(:\d+)?
    Examples:
        - ["https://app.example.com", "https://api.example.com"]
        - ["*"]  # Allow all origins (NOT recommended for production)
    Security Notes:
        - Avoid using "*" in production (allows any origin)
        - Use specific domains for better security
        - HTTPS origins recommended for secure communication

# SSL Certificate Configuration
ssl_certfile: str
    Description: Path to SSL certificate file for HTTPS
    Type: str (file path)
    Default: None
    Validation:
        - Must be valid file path
        - File must exist and be readable
        - File extension: .pem, .crt, or .cert
    Examples:
        - "agent/certs/server.crt"
        - "/etc/ssl/certs/myapp.pem"
    Security Notes:
        - Required for HTTPS deployment
        - Keep certificate files secure (chmod 600)
        - Renew certificates before expiration
```

## Implementation Plan

### Step 1: Update _ALLOWED_UPDATE_KEYS
Add 5 new fields to whitelist:
```python
_ALLOWED_UPDATE_KEYS = {
    # ... existing fields ...
    "cors_allowed_origins",
    "ssl_certfile",
    "ssl_keyfile",
    "ssl_ca_certs",
    "csrf_enabled",
}
```

### Step 2: Add Validation Functions
Create validation functions in settings.py:
```python
def validate_cors_origins(origins: list) -> bool:
    """Validate CORS origins list"""
    if not isinstance(origins, list):
        return False
    pattern = re.compile(r'^(https?://[a-zA-Z0-9.-]+(:\d+)?|\*)$')
    return all(pattern.match(str(origin)) for origin in origins)

def validate_ssl_file(filepath: str, extensions: list) -> bool:
    """Validate SSL file path and extension"""
    if not filepath:
        return True  # None/empty is valid (optional)
    path = Path(filepath)
    return path.exists() and path.is_file() and path.suffix in extensions
```

### Step 3: Enhance update_settings()
Add validation logic to update_settings():
```python
def update_settings(updates: dict) -> Settings:
    """Update settings with new values and validation."""
    filtered_updates = {}
    for key, value in updates.items():
        if key not in _ALLOWED_UPDATE_KEYS:
            continue
        
        # Validate based on field type
        if key == "cors_allowed_origins":
            if not validate_cors_origins(value):
                raise ValueError(f"Invalid CORS origins: {value}")
        elif key == "ssl_certfile":
            if not validate_ssl_file(value, [".pem", ".crt", ".cert"]):
                raise ValueError(f"Invalid SSL certificate file: {value}")
        elif key == "ssl_keyfile":
            if not validate_ssl_file(value, [".pem", ".key"]):
                raise ValueError(f"Invalid SSL key file: {value}")
        elif key == "ssl_ca_certs":
            if not validate_ssl_file(value, [".pem", ".crt"]):
                raise ValueError(f"Invalid CA certs file: {value}")
        elif key == "csrf_enabled":
            if isinstance(value, str):
                value = value.lower() in ("true", "1", "yes")
            if not value:
                # Log warning when CSRF is disabled
                import logging
                logging.warning("CSRF protection disabled - NOT recommended for production")
        
        filtered_updates[key] = value
    
    # ... rest of update logic ...
```

### Step 4: Create Configuration Documentation
Create `docs/CONFIGURATION_API.md` with full field documentation.

### Step 5: Add Tests
Create `tests/agent/test_config_api_validation.py` with:
- Valid CORS origins
- Invalid CORS origins
- Valid SSL file paths
- Invalid SSL file paths
- CSRF toggle with warning
- All new fields via /api/config endpoint

## Security Considerations

### CSRF Secret Rotation
Instead of allowing `csrf_secret` updates via /api/config, create dedicated endpoint:
```python
@app.post("/api/security/rotate-csrf-secret")
async def rotate_csrf_secret():
    """Generate new CSRF secret and update config"""
    new_secret = secrets.token_urlsafe(32)
    update_settings({"csrf_secret": new_secret})
    return {"status": "success", "message": "CSRF secret rotated"}
```

### SSL File Security
- Validate file permissions (should be 600 or 400)
- Warn if files are world-readable
- Check certificate expiration dates
- Validate certificate chain

### CORS Security
- Log warning for wildcard origins
- Recommend specific origins for production
- Validate origin patterns before saving

## Test Coverage

### Required Tests
1. `test_add_cors_origin_valid()` - Add valid CORS origin
2. `test_add_cors_origin_invalid()` - Reject invalid patterns
3. `test_add_cors_origin_wildcard()` - Allow wildcard with warning
4. `test_update_ssl_certfile_valid()` - Update with valid cert file
5. `test_update_ssl_certfile_invalid()` - Reject invalid cert path
6. `test_update_ssl_keyfile_valid()` - Update with valid key file
7. `test_update_ssl_keyfile_invalid()` - Reject invalid key path
8. `test_update_ssl_ca_certs_valid()` - Update with valid CA bundle
9. `test_disable_csrf_warning()` - Warning logged when CSRF disabled
10. `test_protected_fields_rejected()` - agent_url, project_root rejected

## Completion Criteria

- ✅ 5 new fields added to _ALLOWED_UPDATE_KEYS
- ✅ Validation functions created for all new fields
- ✅ update_settings() enhanced with validation logic
- ✅ Documentation created in docs/CONFIGURATION_API.md
- ✅ 10+ tests created in tests/agent/test_config_api_validation.py
- ✅ All tests passing
- ✅ No security regressions
