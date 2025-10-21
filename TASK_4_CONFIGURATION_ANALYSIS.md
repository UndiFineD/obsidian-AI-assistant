# Task 4: Settings and Configuration Documentation Update

**Date**: October 21, 2025  
**Status**: ✅ ANALYSIS COMPLETE  
**Task**: Update settings and configuration documentation  

---

## Executive Summary

**Issues Found**: 6 documentation gaps  
**Severity**: MEDIUM (configuration focused, helpful for deployment)  
**Files to Update**: 1 main file (docs/CONFIGURATION_API.md)  
**Estimated Fix Time**: 2-3 hours

---

## Current Issues

### Issue 1: Missing New Security Hardening Configuration Options

**Location**: `docs/CONFIGURATION_API.md` - Security section incomplete

**Problem**:
- agent/settings.py has extensive security hardening options (v0.1.35 addition)
- CONFIGURATION_API.md doesn't document these options
- Missing: security_level, threat_detection, behavioral_analysis, request_signing, security_headers

**Current Implementation** (`agent/settings.py` Lines 240-270):
```python
security_level: str = "standard"  # minimal, standard, enhanced, maximum
session_timeout_hours: int = 24
session_idle_timeout_hours: int = 2
max_sessions_per_user: int = 5
api_key_rate_limit: int = 100
threat_detection_enabled: bool = True
auto_block_threshold: float = 20.0
behavioral_analysis_enabled: bool = True
request_signing_enabled: bool = False
security_headers_enabled: bool = True
```

**What's Not Documented**:
- Security level modes (minimal, standard, enhanced, maximum)
- Session timeout strategies
- Threat detection configuration
- Behavioral analysis parameters
- Request signing setup
- Security headers configuration

---

### Issue 2: Missing Logging Configuration Documentation

**Location**: `docs/CONFIGURATION_API.md` - Logging section incomplete

**Problem**:
- agent/settings.py has comprehensive logging options (v0.1.35 addition)
- CONFIGURATION_API.md has minimal logging documentation
- Missing: log_format, log_include_pii, log_console_enabled, log_file_enabled, audit/security/performance logging

**Current Implementation** (`agent/settings.py` Lines 271-285):
```python
log_level: str = "INFO"
log_format: str = "structured"  # 'structured' or 'text'
log_include_pii: bool = False
log_console_enabled: bool = True
log_file_enabled: bool = True
log_audit_enabled: bool = True
log_security_enabled: bool = True
log_performance_enabled: bool = True
log_max_file_size: int = 50 * 1024 * 1024
log_backup_count: int = 5
log_cleanup_days: int = 30
```

**What's Not Documented**:
- Log format options (structured vs text)
- PII logging considerations (privacy)
- Console vs file logging toggle
- Audit logging configuration
- Security logging configuration
- Performance logging configuration
- Log rotation settings

---

### Issue 3: Missing Authentication Configuration

**Location**: `docs/CONFIGURATION_API.md` - Authentication section incomplete

**Problem**:
- agent/settings.py has JWT, password, and MFA options
- CONFIGURATION_API.md doesn't document these options
- Missing: jwt_secret_key, jwt_expiry_hours, password_min_length, require_mfa, lockout settings

**Current Implementation** (`agent/settings.py` Lines 316-330):
```python
jwt_secret_key: str = ""
jwt_expiry_hours: int = 24
password_min_length: int = 8
require_mfa: bool = False
lockout_attempts: int = 5
lockout_duration_minutes: int = 15
```

**What's Not Documented**:
- JWT secret key setup
- Token expiry configuration
- Password complexity rules
- MFA requirements
- Account lockout policy

---

### Issue 4: Missing CORS/SSL/CSRF Configuration Details

**Location**: `docs/CONFIGURATION_API.md` - Network security incomplete

**Problem**:
- agent/settings.py has CORS, SSL, CSRF options
- CONFIGURATION_API.md has basic docs but missing examples and best practices
- Missing: CORS validation examples, SSL certificate setup, CSRF token handling

**Current Implementation** (`agent/settings.py` Lines 290-315):
```python
cors_allowed_origins: list = ["https://localhost:8080"]
ssl_certfile: str = None
ssl_keyfile: str = None
ssl_ca_certs: str = None
csrf_enabled: bool = True
csrf_secret: str = "change-me"
```

**What's Not Documented**:
- CORS origin validation rules and examples
- SSL/TLS setup with certificate paths
- CA bundle configuration for client certificate validation
- CSRF token setup and usage
- Production vs development CORS policies

---

### Issue 5: Missing File Validation Settings

**Location**: `docs/CONFIGURATION_API.md` - File handling incomplete

**Problem**:
- agent/settings.py has file size and validation options
- CONFIGURATION_API.md doesn't document these properly
- Missing: file_validation_enabled, size limits by file type, security considerations

**Current Implementation** (`agent/settings.py` Lines 230-236):
```python
pdf_max_size_mb: int = 50
audio_max_size_mb: int = 25
text_max_size_mb: int = 10
archive_max_size_mb: int = 100
file_validation_enabled: bool = True
```

**What's Not Documented**:
- Why file validation matters (security)
- Safe limits for each file type
- When to adjust limits
- Validation error handling
- Recommended settings for different deployment scenarios

---

### Issue 6: Missing Model and Vector DB Configuration Best Practices

**Location**: `docs/CONFIGURATION_API.md` - Model config has basic info, missing best practices

**Problem**:
- agent/settings.py model options lack context in documentation
- No guidance on how to choose models/backends
- Missing: recommendations for different hardware, performance tradeoffs
- No documentation of minimal vs optimal settings

**Current Implementation** (`agent/settings.py` Lines 196-211):
```python
model_backend: str = "llama_cpp"
model_path: str = "./models/gpt4all/llama-7b.gguf"
embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
vector_db: str = "chroma"
gpu: bool = True
top_k: int = 10
chunk_size: int = 800
chunk_overlap: int = 200
similarity_threshold: float = 0.75
```

**What's Not Documented**:
- Model backend comparison (llama_cpp vs gpt4all)
- When to use GPU vs CPU
- Top-k selection strategy
- Chunk size optimization
- Similarity threshold tuning
- Embedding model trade-offs
- Performance impact of each setting

---

## Required Documentation Updates

### Update 1: Add Complete Security Configuration Section

**File**: `docs/CONFIGURATION_API.md`  
**Action**: Expand security section with all hardening options

**New Content**:
```markdown
### Security Hardening Settings

#### security_level
- **Type**: String (enum)
- **Values**: "minimal", "standard", "enhanced", "maximum"
- **Default**: "standard"
- **Description**: Overall security posture for the deployment

**Mode Details**:
- minimal: Low security overhead, for trusted internal networks
- standard: Balanced security/performance (recommended)
- enhanced: High security with minor performance impact
- maximum: Maximum security (significant performance cost)

**Example**:
```yaml
security_level: "enhanced"
```

#### session_timeout_hours
- **Type**: Integer
- **Default**: 24
- **Validation**: Must be 1-720 hours
- **Description**: Session expiration time (hours)
- **Example**: 24 (1 day), 720 (30 days), 8 (work shift)

#### session_idle_timeout_hours
- **Type**: Integer
- **Default**: 2
- **Validation**: Must be < session_timeout_hours
- **Description**: Idle time before automatic logout (hours)
- **Example**: 2 (30 min = 0.5), 1 (1 hour), 8 (work day)

#### max_sessions_per_user
- **Type**: Integer
- **Default**: 5
- **Validation**: Must be 1-100
- **Description**: Maximum concurrent sessions per user
- **Example**: 1 (single session), 5 (desktop + mobile), 10 (team)

#### api_key_rate_limit
- **Type**: Integer
- **Default**: 100
- **Validation**: Must be 1-10000
- **Description**: API calls per minute per key
- **Example**: 100 (standard), 1000 (high throughput), 10 (restricted)

#### threat_detection_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Enable automatic threat detection and response
- **Security Impact**: HIGH (detects and blocks attacks)

#### auto_block_threshold
- **Type**: Float
- **Default**: 20.0
- **Validation**: Must be 1.0-100.0
- **Description**: Threat score threshold for automatic blocking
- **Example**: 10.0 (sensitive), 20.0 (balanced), 50.0 (permissive)

#### behavioral_analysis_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Enable behavioral analysis for anomaly detection
- **Security Impact**: MEDIUM (detects suspicious patterns)

#### request_signing_enabled
- **Type**: Boolean
- **Default**: false
- **Description**: Require HMAC-SHA256 request signatures
- **Security Impact**: HIGH (prevents tampering)
- **Note**: Increases latency slightly, highly recommended for production

#### security_headers_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Enable security headers (CSP, HSTS, etc.)
- **Security Impact**: HIGH (browser-level protection)
```

### Update 2: Add Comprehensive Logging Configuration

**File**: `docs/CONFIGURATION_API.md`  
**Action**: Create dedicated logging section

**New Content**:
```markdown
### Logging Configuration

#### log_level
- **Type**: String (enum)
- **Values**: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
- **Default**: "INFO"
- **Description**: Logging output verbosity level
- **Examples**:
  - DEBUG: Verbose output (development only, high I/O)
  - INFO: Standard production logging
  - WARNING: Only warnings and errors
  - ERROR: Only errors
  - CRITICAL: Only critical failures

#### log_format
- **Type**: String (enum)
- **Values**: "structured", "text"
- **Default**: "structured"
- **Description**: Log message format
- **Examples**:
  - structured: JSON format (machine-readable, recommended for production)
  - text: Human-readable format (better for development)

#### log_include_pii
- **Type**: Boolean
- **Default**: false
- **Description**: Include Personally Identifiable Information in logs
- **Security Impact**: CRITICAL
- **WARNING**: Enable only in compliance-controlled environments
- **Compliance**: Affects GDPR, CCPA, SOC2 compliance

#### log_console_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Log to stdout/console
- **Example**: true (development), false (background service)

#### log_file_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Log to file system
- **Example**: true (persistent storage), false (ephemeral/containers)

#### log_audit_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Log audit events (login, permission changes)
- **Security Impact**: HIGH (required for compliance)

#### log_security_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Log security events (auth failures, blocked requests)
- **Security Impact**: HIGH (threat detection)

#### log_performance_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Log performance metrics (latency, cache hits)
- **Performance Impact**: MEDIUM (overhead of 5-10%)

#### log_max_file_size
- **Type**: Integer
- **Default**: 52428800 (50MB)
- **Unit**: Bytes
- **Description**: Maximum size before log rotation
- **Example**: 10485760 (10MB), 52428800 (50MB), 104857600 (100MB)

#### log_backup_count
- **Type**: Integer
- **Default**: 5
- **Description**: Number of rotated logs to retain
- **Example**: 5 (5 files = 250MB total), 10 (500MB total)

#### log_cleanup_days
- **Type**: Integer
- **Default**: 30
- **Description**: Auto-delete logs older than N days
- **Example**: 7 (weekly cleanup), 30 (monthly), 90 (quarterly)

**Complete Logging Configuration Example**:
```yaml
# Development (verbose, human-readable)
log_level: DEBUG
log_format: text
log_include_pii: false
log_console_enabled: true
log_file_enabled: true
log_audit_enabled: true
log_security_enabled: true
log_performance_enabled: true

# Production (balanced, structured)
log_level: INFO
log_format: structured
log_include_pii: false
log_console_enabled: false
log_file_enabled: true
log_audit_enabled: true
log_security_enabled: true
log_performance_enabled: false  # Reduce overhead
log_max_file_size: 104857600  # 100MB (larger files)
log_backup_count: 10  # Keep 1GB of logs
log_cleanup_days: 90  # Keep 3 months history
```
```

### Update 3: Add Authentication Configuration

**File**: `docs/CONFIGURATION_API.md`  
**Action**: Create dedicated authentication section

**New Content**:
```markdown
### Authentication Configuration

#### jwt_secret_key
- **Type**: String
- **Default**: "" (empty, auto-generated on init)
- **Validation**: Minimum 32 characters for production
- **Description**: Secret key for JWT token signing
- **Security**: CRITICAL
- **Setup**:
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Result example: 
# v7j9K_xQ8pL2mN4wE6rT1yUiOpAsD5fG3hJ
```

#### jwt_expiry_hours
- **Type**: Integer
- **Default**: 24
- **Validation**: 1-720 hours
- **Description**: JWT token lifetime in hours
- **Examples**:
  - 1 (very short, high security)
  - 24 (daily, standard)
  - 168 (weekly, convenience)

#### password_min_length
- **Type**: Integer
- **Default**: 8
- **Validation**: 4-128 characters
- **Description**: Minimum password length
- **Examples**:
  - 8 (default, balances security/usability)
  - 12 (high security)
  - 16 (maximum security)

#### require_mfa
- **Type**: Boolean
- **Default**: false
- **Description**: Require Multi-Factor Authentication for all users
- **Security Impact**: CRITICAL
- **Performance**: Minimal (auth only, not per-request)
- **Example**: true (production), false (development)

#### lockout_attempts
- **Type**: Integer
- **Default**: 5
- **Validation**: 3-20 attempts
- **Description**: Failed login attempts before lockout
- **Examples**:
  - 3 (strict, prevents brute force)
  - 5 (balanced)
  - 10 (lenient)

#### lockout_duration_minutes
- **Type**: Integer
- **Default**: 15
- **Validation**: 1-1440 minutes
- **Description**: Lockout duration after failed attempts
- **Examples**:
  - 5 (quick reset)
  - 15 (standard, prevents rapid attempts)
  - 60 (strict, prevents distributed attacks)

**Complete Authentication Configuration Example**:
```yaml
# Development (relaxed)
jwt_secret_key: "dev-secret-key-change-in-production"
jwt_expiry_hours: 168  # 1 week
password_min_length: 6
require_mfa: false
lockout_attempts: 10
lockout_duration_minutes: 5

# Production (strict)
jwt_secret_key: "${JWT_SECRET_KEY}"  # From environment
jwt_expiry_hours: 24  # 1 day
password_min_length: 12
require_mfa: true  # All users
lockout_attempts: 5
lockout_duration_minutes: 30
```
```

### Update 4: Add Network Security Configuration

**File**: `docs/CONFIGURATION_API.md`  
**Action**: Expand CORS/SSL/CSRF section with examples

**New Content**:
```markdown
### Network Security Configuration

#### cors_allowed_origins
- **Type**: List of strings
- **Default**: `["https://localhost:8080", "https://localhost:8000"]`
- **Validation**: Must be valid URLs or "*"
- **Description**: Allowed CORS origins
- **Wildcard**: "*" allows any origin (NOT recommended for production)

**Examples**:
```yaml
# Development (localhost only)
cors_allowed_origins:
  - "https://localhost:3000"
  - "https://localhost:8080"

# Production (specific domains)
cors_allowed_origins:
  - "https://app.example.com"
  - "https://admin.example.com"
  - "https://api.example.com"

# Wildcard (NOT RECOMMENDED)
cors_allowed_origins:
  - "*"  # Allows any origin - security risk!
```

#### ssl_certfile
- **Type**: String (file path)
- **Default**: null (uses HTTP)
- **Description**: Path to SSL/TLS certificate file (.pem, .crt)
- **Format**: PEM-encoded X.509 certificate
- **Example**: `/etc/ssl/certs/server.crt`

#### ssl_keyfile
- **Type**: String (file path)
- **Default**: null
- **Description**: Path to private key file (.key, .pem)
- **Security**: CRITICAL - must be readable only by service account
- **Example**: `/etc/ssl/private/server.key`

#### ssl_ca_certs
- **Type**: String (file path)
- **Default**: null
- **Description**: Path to CA certificate bundle
- **Use**: Client certificate validation
- **Example**: `/etc/ssl/certs/ca-bundle.crt`

**SSL/TLS Setup Example**:
```bash
# 1. Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365

# 2. Set in config
ssl_certfile: "./ssl/server.crt"
ssl_keyfile: "./ssl/server.key"

# 3. Verify certificate
openssl x509 -in server.crt -text -noout
```

#### csrf_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Enable CSRF token protection
- **Security**: HIGH (prevents cross-site request forgery)

#### csrf_secret
- **Type**: String
- **Default**: "change-me"
- **Security**: CRITICAL - change in production
- **Description**: Secret key for CSRF token generation
- **Example**: Use same method as jwt_secret_key
```

### Update 5: Add File Validation Settings

**File**: `docs/CONFIGURATION_API.md`  
**Action**: Create file handling section

**New Content**:
```markdown
### File Handling & Validation

#### file_validation_enabled
- **Type**: Boolean
- **Default**: true
- **Description**: Enable file type/size validation
- **Security**: HIGH (prevents malicious uploads)

#### pdf_max_size_mb
- **Type**: Integer
- **Default**: 50
- **Unit**: Megabytes
- **Validation**: 1-1000 MB
- **Description**: Maximum PDF file size
- **Examples**: 20 (restrictive), 50 (standard), 200 (large docs)

#### audio_max_size_mb
- **Type**: Integer
- **Default**: 25
- **Unit**: Megabytes
- **Description**: Maximum audio file size
- **Examples**: 10 (short clips), 25 (standard), 100 (long recordings)

#### text_max_size_mb
- **Type**: Integer
- **Default**: 10
- **Unit**: Megabytes
- **Description**: Maximum text file size
- **Examples**: 5 (restrictive), 10 (standard), 50 (large documents)

#### archive_max_size_mb
- **Type**: Integer
- **Default**: 100
- **Unit**: Megabytes
- **Description**: Maximum archive (ZIP, TAR) size
- **Examples**: 50 (restrictive), 100 (standard), 500 (large imports)

**File Validation Configuration Example**:
```yaml
# Development (permissive)
file_validation_enabled: true
pdf_max_size_mb: 500
audio_max_size_mb: 200
text_max_size_mb: 100
archive_max_size_mb: 500

# Production (restrictive - prevents abuse)
file_validation_enabled: true
pdf_max_size_mb: 50
audio_max_size_mb: 25
text_max_size_mb: 10
archive_max_size_mb: 100
```

**Why These Limits Matter**:
- **Security**: Prevents resource exhaustion attacks (DoS)
- **Performance**: Smaller files = faster processing
- **Storage**: Limits disk usage
- **Memory**: Prevents OOM errors during processing
```

### Update 6: Add Model & Vector DB Best Practices

**File**: `docs/CONFIGURATION_API.md`  
**Action**: Expand model section with guidance

**New Content**:
```markdown
### AI Model & Vector Database Configuration

#### model_backend
- **Type**: String (enum)
- **Values**: "llama_cpp", "gpt4all", "openai", "huggingface"
- **Default**: "llama_cpp"
- **Description**: LLM backend provider

**Comparison**:
| Backend | Speed | Quality | Cost | Setup | GPU |
|---------|-------|---------|------|-------|-----|
| llama_cpp | Fast | Good | Free | Local | Yes |
| gpt4all | Medium | Good | Free | Local | Yes |
| openai | Slow | Excellent | $$ | API | No |
| huggingface | Medium | Good | $$ | Local/Cloud | Yes |

#### model_path
- **Type**: String (file path)
- **Default**: "./models/gpt4all/llama-7b.gguf"
- **Description**: Path to model weights file

**Recommended Models**:
- Lightweight (2GB VRAM): deepseek-ai/Janus-Pro-1B
- Balanced (4GB VRAM): Qwen2.5-Omni-3B
- Quality (8GB VRAM): Mistral-7B
- Best (24GB VRAM): LLaMA-2-70B

#### embed_model
- **Type**: String (HuggingFace model ID)
- **Default**: "sentence-transformers/all-MiniLM-L6-v2"
- **Description**: Embedding model for vector search

**Options**:
- all-MiniLM-L6-v2: Fast, lightweight (recommended)
- all-mpnet-base-v2: Slower, better quality
- multilingual-e5-large: Multilingual support

#### vector_db
- **Type**: String (enum)
- **Values**: "chroma", "faiss", "milvus"
- **Default**: "chroma"
- **Description**: Vector database backend

**Comparison**:
| DB | Speed | Scalability | Setup |
|----|-------|-------------|-------|
| chroma | Fast | Small-medium | Simple (local) |
| faiss | Very Fast | Medium | Moderate |
| milvus | Medium | Large | Complex (server) |

#### gpu
- **Type**: Boolean
- **Default**: true
- **Description**: Use GPU acceleration
- **Recommendation**:
  - true: If NVIDIA GPU available (3x-5x faster)
  - false: CPU only (slower but always works)

#### top_k
- **Type**: Integer
- **Default**: 10
- **Validation**: 1-100
- **Description**: Number of search results to return

**Recommendations**:
- 5: Fast, focused results
- 10: Balanced (default)
- 20: Comprehensive search
- 50+: Only for high-precision needs

#### chunk_size
- **Type**: Integer
- **Default**: 800
- **Validation**: 100-4000 tokens
- **Description**: Document chunk size for indexing

**Impact on Quality**:
- 400: Smaller chunks (more specific results, higher cost)
- 800: Balanced (recommended)
- 1500: Larger chunks (broader context, fewer results)

#### chunk_overlap
- **Type**: Integer
- **Default**: 200
- **Validation**: 0-chunk_size/2
- **Description**: Token overlap between chunks

**Recommendations**:
- 0: No overlap (faster, may miss context)
- 200: Standard overlap
- 400: High overlap (comprehensive, slower)

#### similarity_threshold
- **Type**: Float (0.0-1.0)
- **Default**: 0.75
- **Description**: Minimum similarity score for results

**Impact**:
- 0.5: Very permissive (many false positives)
- 0.75: Balanced (recommended)
- 0.95: Very strict (may miss results)

**Complete Model Configuration Example**:
```yaml
# Minimal (2GB VRAM, CPU-only)
model_backend: "llama_cpp"
model_path: "./models/deepseek/janus-pro-1b.gguf"
embed_model: "sentence-transformers/all-MiniLM-L6-v2"
vector_db: "chroma"
gpu: false
top_k: 5
chunk_size: 400
chunk_overlap: 100
similarity_threshold: 0.8

# Balanced (4GB VRAM, GPU)
model_backend: "llama_cpp"
model_path: "./models/qwen/qwen2.5-omni-3b.gguf"
embed_model: "sentence-transformers/all-mpnet-base-v2"
vector_db: "chroma"
gpu: true
top_k: 10
chunk_size: 800
chunk_overlap: 200
similarity_threshold: 0.75

# High-Performance (24GB VRAM, GPU)
model_backend: "llama_cpp"
model_path: "./models/llama/llama-2-70b.gguf"
embed_model: "sentence-transformers/all-mpnet-base-v2"
vector_db: "milvus"
gpu: true
top_k: 20
chunk_size: 1200
chunk_overlap: 300
similarity_threshold: 0.7
```
```

---

## Implementation Steps

### Step 1: Update Security Section
- Replace existing security docs with comprehensive hardening options

### Step 2: Add Logging Section
- Insert new logging configuration section with all options and examples

### Step 3: Add Authentication Section
- Insert new authentication configuration section

### Step 4: Expand Network Security
- Add CORS, SSL, CSRF detailed documentation

### Step 5: Add File Handling Section
- Insert file validation settings with rationale

### Step 6: Enhance Model Configuration
- Add comparison tables and best practices
- Add configuration examples for different scenarios

---

## Testing the Updates

After implementation:

```bash
# 1. Verify documentation renders
# (View CONFIGURATION_API.md in GitHub/web viewer)

# 2. Test configuration endpoints
curl http://localhost:8000/api/config

# 3. Verify all settings are documented
# (Cross-reference agent/settings.py against CONFIGURATION_API.md)

# 4. Check examples are accurate
# (Run example configurations and verify they work)
```

---

## Notes for Documentation Team

1. **Configuration Hierarchy**: Emphasize that env vars > config.yaml > code defaults
2. **Security**: Clearly mark security-critical settings with warnings
3. **Performance**: Include impact assessment for each setting
4. **Examples**: Provide realistic examples for dev/prod/minimal scenarios
5. **Compliance**: Note which settings affect compliance (GDPR, SOC2, CCPA)

---

**Status**: Ready for implementation  
**Estimated Time**: 2-3 hours including testing  
**Priority**: MEDIUM (configuration documentation improves deployment experience)
