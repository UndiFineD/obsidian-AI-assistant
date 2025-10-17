# Configuration API Documentation

## Overview

The Configuration API (`/api/config`) allows runtime configuration updates for the
Obsidian AI Assistant backend. This document provides comprehensive documentation for
all configurable fields.

## Endpoints

### Get Current Configuration

**Endpoint**: `GET /api/config`

**Description**: Retrieve current runtime configuration (whitelisted fields only, sensitive values redacted)

**Response Example**:
```json
{
  "api_port": 8000,
  "allow_network": false,
  "gpu": true,
  "model_backend": "llama_cpp",
  "chunk_size": 800,
  "security_level": "standard",
  "jwt_expiry_hours": 24
}
```

### Update Configuration

**Endpoint**: `POST /api/config`

**Description**: Update runtime configuration (only whitelisted keys accepted)

**Request Body**:
```json
{
  "chunk_size": 1000,
  "gpu": true,
  "cors_allowed_origins": ["https://app.example.com"]
}
```

**Response**:
```json
{
  "status": "success",
  "updated_fields": ["chunk_size", "gpu", "cors_allowed_origins"]
}
```

### Reload Configuration

**Endpoint**: `POST /api/config/reload`

**Description**: Reload configuration from `backend/config.yaml`

**Response**:
```json
{
  "status": "success",
  "message": "Configuration reloaded from backend/config.yaml"
}
```

## Configurable Fields

### Core Server Settings

#### api_port
- **Type**: Integer
- **Default**: `8000`
- **Validation**: Must be valid port number (1-65535)
- **Description**: Port number for API server
- **Example**: `8000`, `3000`, `5000`
- **Security Notes**: Avoid using privileged ports (<1024) without proper permissions

#### allow_network
- **Type**: Boolean
- **Default**: `false`
- **Validation**: Must be boolean
- **Description**: Allow network access for external requests
- **Example**: `true`, `false`
- **Security Notes**: Enable only when needed for external integrations

#### continuous_mode
- **Type**: Boolean
- **Default**: `false`
- **Validation**: Must be boolean
- **Description**: Enable continuous processing mode
- **Example**: `true`, `false`

### Path Configuration

#### vault_path
- **Type**: String (path)
- **Default**: `"vault"`
- **Validation**: Valid directory path
- **Description**: Path to Obsidian vault directory
- **Example**: `"vault"`, `"C:/Users/me/Documents/MyVault"`

#### models_dir
- **Type**: String (path)
- **Default**: `"backend/models"`
- **Validation**: Valid directory path
- **Description**: Directory containing AI models
- **Example**: `"backend/models"`, `"/data/ai-models"`

#### cache_dir
- **Type**: String (path)
- **Default**: `"backend/cache"`
- **Validation**: Valid directory path
- **Description**: Directory for cached embeddings and responses
- **Example**: `"backend/cache"`, `"/tmp/ai-cache"`

#### log_dir
- **Type**: String (path)
- **Default**: `"backend/logs"`
- **Validation**: Valid directory path
- **Description**: Directory for log files
- **Example**: `"backend/logs"`, `"/var/log/obsidian-ai"`

### AI Model Configuration

#### model_backend
- **Type**: String (enum)
- **Default**: `"llama_cpp"`
- **Validation**: Must be one of: `llama_cpp`, `gpt4all`, `openai`
- **Description**: AI model backend to use
- **Example**: `"llama_cpp"`, `"gpt4all"`

#### model_path
- **Type**: String (path)
- **Default**: `"backend/models/llama-7b.gguf"`
- **Validation**: Valid file path to .gguf model
- **Description**: Path to AI model file
- **Example**: `"backend/models/llama-7b.gguf"`

#### embed_model
- **Type**: String
- **Default**: `"sentence-transformers/all-MiniLM-L6-v2"`
- **Validation**: Valid model identifier
- **Description**: Embedding model for vector search
- **Example**: `"sentence-transformers/all-MiniLM-L6-v2"`

#### gpu
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable GPU acceleration for AI models
- **Example**: `true`, `false`
- **Security Notes**: GPU drivers must be properly installed

### Vector Database Settings

#### vector_db
- **Type**: String (enum)
- **Default**: `"chroma"`
- **Validation**: Must be one of: `chroma`, `faiss`, `qdrant`
- **Description**: Vector database backend
- **Example**: `"chroma"`, `"faiss"`

#### top_k
- **Type**: Integer
- **Default**: `10`
- **Validation**: Must be positive integer
- **Description**: Number of top results to return from vector search
- **Example**: `5`, `10`, `20`

#### chunk_size
- **Type**: Integer
- **Default**: `800`
- **Validation**: Must be positive integer (recommended: 500-2000)
- **Description**: Text chunk size for indexing (characters)
- **Example**: `800`, `1000`, `1500`

#### chunk_overlap
- **Type**: Integer
- **Default**: `200`
- **Validation**: Must be positive integer (recommended: 10-50% of chunk_size)
- **Description**: Overlap between text chunks (characters)
- **Example**: `100`, `200`, `400`

#### similarity_threshold
- **Type**: Float
- **Default**: `0.75`
- **Validation**: Must be between 0.0 and 1.0
- **Description**: Minimum similarity score for search results
- **Example**: `0.5`, `0.75`, `0.9`

### Voice Recognition

#### vosk_model_path
- **Type**: String (path)
- **Default**: `"backend/models/vosk-model-small-en-us-0.15"`
- **Validation**: Valid directory path to Vosk model
- **Description**: Path to Vosk speech recognition model
- **Example**: `"backend/models/vosk-model-small-en-us-0.15"`

### File Validation

#### pdf_max_size_mb
- **Type**: Integer
- **Default**: `50`
- **Validation**: Must be positive integer
- **Description**: Maximum PDF file size (megabytes)
- **Example**: `25`, `50`, `100`

#### audio_max_size_mb
- **Type**: Integer
- **Default**: `25`
- **Validation**: Must be positive integer
- **Description**: Maximum audio file size (megabytes)
- **Example**: `10`, `25`, `50`

#### text_max_size_mb
- **Type**: Integer
- **Default**: `10`
- **Validation**: Must be positive integer
- **Description**: Maximum text file size (megabytes)
- **Example**: `5`, `10`, `25`

#### archive_max_size_mb
- **Type**: Integer
- **Default**: `100`
- **Validation**: Must be positive integer
- **Description**: Maximum archive file size (megabytes)
- **Example**: `50`, `100`, `200`

#### file_validation_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable file validation and size limits
- **Example**: `true`, `false`
- **Security Notes**: Disabling validation may expose system to malicious files

### Logging Configuration

#### log_level
- **Type**: String (enum)
- **Default**: `"INFO"`
- **Validation**: Must be one of: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Description**: Logging level
- **Example**: `"DEBUG"`, `"INFO"`, `"WARNING"`

#### log_format
- **Type**: String (enum)
- **Default**: `"structured"`
- **Validation**: Must be one of: `structured`, `text`
- **Description**: Log output format
- **Example**: `"structured"`, `"text"`

#### log_include_pii
- **Type**: Boolean
- **Default**: `false`
- **Validation**: Must be boolean
- **Description**: Include personally identifiable information in logs
- **Example**: `true`, `false`
- **Security Notes**: Enable only for debugging, disable in production

#### log_console_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable console logging
- **Example**: `true`, `false`

#### log_file_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable file logging
- **Example**: `true`, `false`

#### log_audit_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable audit logging
- **Example**: `true`, `false`

#### log_security_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable security event logging
- **Example**: `true`, `false`

#### log_performance_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable performance metrics logging
- **Example**: `true`, `false`

#### log_max_file_size
- **Type**: Integer
- **Default**: `52428800` (50MB)
- **Validation**: Must be positive integer (bytes)
- **Description**: Maximum log file size before rotation
- **Example**: `10485760` (10MB), `52428800` (50MB)

#### log_backup_count
- **Type**: Integer
- **Default**: `5`
- **Validation**: Must be positive integer
- **Description**: Number of backup log files to keep
- **Example**: `3`, `5`, `10`

#### log_cleanup_days
- **Type**: Integer
- **Default**: `30`
- **Validation**: Must be positive integer
- **Description**: Days to keep old log files
- **Example**: `7`, `30`, `90`

### Security Hardening

#### security_level
- **Type**: String (enum)
- **Default**: `"standard"`
- **Validation**: Must be one of: `minimal`, `standard`, `enhanced`, `maximum`
- **Description**: Security configuration preset
- **Example**: `"standard"`, `"enhanced"`

#### session_timeout_hours
- **Type**: Integer
- **Default**: `24`
- **Validation**: Must be positive integer
- **Description**: Session timeout duration (hours)
- **Example**: `8`, `24`, `72`

#### session_idle_timeout_hours
- **Type**: Integer
- **Default**: `2`
- **Validation**: Must be positive integer
- **Description**: Idle session timeout (hours)
- **Example**: `1`, `2`, `4`

#### max_sessions_per_user
- **Type**: Integer
- **Default**: `5`
- **Validation**: Must be positive integer
- **Description**: Maximum concurrent sessions per user
- **Example**: `3`, `5`, `10`

#### api_key_rate_limit
- **Type**: Integer
- **Default**: `100`
- **Validation**: Must be positive integer
- **Description**: API requests per minute per key
- **Example**: `50`, `100`, `1000`

#### threat_detection_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable threat detection
- **Example**: `true`, `false`

#### auto_block_threshold
- **Type**: Float
- **Default**: `20.0`
- **Validation**: Must be positive number
- **Description**: Threat score threshold for auto-blocking
- **Example**: `10.0`, `20.0`, `50.0`

#### behavioral_analysis_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable behavioral analysis
- **Example**: `true`, `false`

#### request_signing_enabled
- **Type**: Boolean
- **Default**: `false`
- **Validation**: Must be boolean
- **Description**: Require request signing
- **Example**: `true`, `false`

#### security_headers_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable security headers (HSTS, CSP, etc.)
- **Example**: `true`, `false`

### Authentication Settings

#### jwt_secret_key
- **Type**: String
- **Default**: `""` (empty, must be set via environment)
- **Validation**: Minimum 32 characters recommended
- **Description**: Secret key for JWT token signing
- **Example**: `"your-secret-key-here-make-it-long-and-random"`
- **Security Notes**: NEVER commit to version control, use environment variable

#### jwt_expiry_hours
- **Type**: Integer
- **Default**: `24`
- **Validation**: Must be positive integer
- **Description**: JWT token expiration time (hours)
- **Example**: `1`, `24`, `168`

#### password_min_length
- **Type**: Integer
- **Default**: `8`
- **Validation**: Must be positive integer
- **Description**: Minimum password length
- **Example**: `8`, `12`, `16`

#### require_mfa
- **Type**: Boolean
- **Default**: `false`
- **Validation**: Must be boolean
- **Description**: Require multi-factor authentication
- **Example**: `true`, `false`

#### lockout_attempts
- **Type**: Integer
- **Default**: `5`
- **Validation**: Must be positive integer
- **Description**: Failed login attempts before lockout
- **Example**: `3`, `5`, `10`

#### lockout_duration_minutes
- **Type**: Integer
- **Default**: `15`
- **Validation**: Must be positive integer
- **Description**: Account lockout duration (minutes)
- **Example**: `15`, `30`, `60`

### Network & SSL Settings

#### cors_allowed_origins
- **Type**: List of strings
- **Default**: `["https://localhost:8080", "https://localhost:8000"]`
- **Validation**: Must be list of valid URLs or `"*"`
- **Pattern**: `https?://[a-zA-Z0-9.-]+(:\d+)?` or `*`
- **Description**: Allowed origins for CORS (Cross-Origin Resource Sharing)
- **Examples**:
  ```json
  ["https://app.example.com", "https://api.example.com"]
  ["https://localhost:3000", "https://localhost:8080"]
  ["*"]  // Allow all origins (NOT recommended for production)
  ```
- **Security Notes**:
    - Avoid using `"*"` in production (allows any origin)
    - Use specific domains for better security
    - HTTPS origins recommended for secure communication
    - Wildcard origins trigger warning in logs

#### ssl_certfile
- **Type**: String (file path)
- **Default**: `null`
- **Validation**: Must be valid file path with .pem, .crt, or .cert extension
- **Description**: Path to SSL certificate file for HTTPS
- **Examples**:
  ```
  "backend/certs/server.crt"
  "/etc/ssl/certs/myapp.pem"
  "C:/certs/server.cert"
  ```
- **Security Notes**:
    - Required for HTTPS deployment
    - Keep certificate files secure (chmod 600 recommended)
    - Renew certificates before expiration
    - File must exist and be readable

#### ssl_keyfile
- **Type**: String (file path)
- **Default**: `null`
- **Validation**: Must be valid file path with .pem or .key extension
- **Description**: Path to SSL private key file for HTTPS
- **Examples**:
  ```
  "backend/certs/server.key"
  "/etc/ssl/private/myapp.key"
  "C:/certs/server.pem"
  ```
- **Security Notes**:
    - Required for HTTPS deployment
    - NEVER commit private keys to version control
    - Keep key files extremely secure (chmod 400 recommended)
    - File must exist and be readable

#### ssl_ca_certs
- **Type**: String (file path)
- **Default**: `null`
- **Validation**: Must be valid file path with .pem or .crt extension (or null)
- **Description**: Path to CA bundle for certificate chain validation
- **Examples**:
  ```
  "backend/certs/ca-bundle.crt"
  "/etc/ssl/certs/ca-certificates.crt"
  null  // Use system CA bundle
  ```
- **Security Notes**:
    - Optional, but recommended for enterprise environments
    - Required for client certificate validation
    - Use trusted CA bundles only

#### csrf_enabled
- **Type**: Boolean
- **Default**: `true`
- **Validation**: Must be boolean
- **Description**: Enable CSRF (Cross-Site Request Forgery) protection
- **Example**: `true`, `false`
- **Security Notes**:
    - **WARNING**: Disabling CSRF protection is NOT recommended for production
    - Only disable for development/testing or when using alternative CSRF mechanisms
    - Disabling triggers warning in logs
    - Always re-enable before production deployment

## Usage Examples

### Update Multiple Fields

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 1000,
    "gpu": true,
    "log_level": "DEBUG",
    "cors_allowed_origins": ["https://app.example.com"]
  }'
```

### Configure SSL for HTTPS

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "ssl_certfile": "backend/certs/server.crt",
    "ssl_keyfile": "backend/certs/server.key",
    "ssl_ca_certs": "backend/certs/ca-bundle.crt"
  }'
```

### Update CORS Origins

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "cors_allowed_origins": [
      "https://app1.example.com",
      "https://app2.example.com",
      "https://localhost:3000"
    ]
  }'
```

### Temporarily Disable CSRF (Development Only)

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "csrf_enabled": false
  }'
```

**WARNING**: This will log a security warning. Re-enable before production deployment.

## Protected Fields

The following fields CANNOT be updated via the API for security reasons:

- `backend_url` - Derived from `api_port`, use `api_port` instead
- `project_root` - System-level path, immutable at runtime
- `csrf_secret` - Use dedicated rotation endpoint instead (future feature)

Attempting to update these fields will silently skip them.

## Error Handling

### Validation Errors

```json
{
  "status": "error",
  "message": "Validation failed for cors_allowed_origins: Invalid CORS origins: ['not-a-url']. Must be list of valid URLs or '*'"
}
```

### Type Coercion Errors

```json
{
  "status": "error",
  "message": "Validation failed for chunk_size: invalid literal for int() with base 10: 'abc'"
}
```

### File Not Found Errors

```json
{
  "status": "error",
  "message": "Validation failed for ssl_certfile: Invalid SSL certificate file: /nonexistent/cert.pem. Must exist and have .pem, .crt, or .cert extension"
}
```

## Best Practices

1. **Environment Variables**: Use environment variables for sensitive settings (JWT_SECRET_KEY, CSRF_SECRET)
2. **Configuration Files**: Use `backend/config.yaml` for persistent configuration
3. **API Updates**: Use `/api/config` for runtime updates during development/testing
4. **Security**: Never disable security features in production
5. **Validation**: Always validate SSL file paths before deployment
6. **CORS**: Use specific origins instead of wildcard in production
7. **Logging**: Enable audit and security logging for compliance
8. **Backups**: Keep backups of config.yaml before making changes

## See Also

- [Backend API Documentation](./spec.md)
- [Security Specification](./SECURITY_SPECIFICATION.md)
- [Deployment Guide](./DEPLOYMENT_SPECIFICATION.md)
- [Performance Configuration](./PERFORMANCE_REQUIREMENTS_SPECIFICATION.md)
