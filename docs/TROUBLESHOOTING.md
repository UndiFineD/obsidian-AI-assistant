# Troubleshooting Guide

**Last Updated**: October 2025  
**For**: Developers, DevOps, and Support Teams

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Common Issues](#common-issues)
3. [20+ Error Scenarios](#20-error-scenarios)
4. [Error Recovery](#error-recovery)
5. [Backend Issues](#backend-issues)
6. [Plugin Issues](#plugin-issues)
7. [API Issues](#api-issues)
8. [Performance Issues](#performance-issues)
9. [Security Issues](#security-issues)
10. [Getting Help](#getting-help)

---

## Quick Reference

**Quick Diagnosis Checklist**:
1. ✅ Backend running? `curl http://localhost:8000/health`
2. ✅ Correct Python version? `python --version` (should be 3.11+)
3. ✅ Agent paths updated? Should be `agent/` not `backend/`
4. ✅ Models location? Should be `./models/` not `agent/models/`
5. ✅ Tests passing? `python -m pytest tests/ -v`
6. ✅ Logs checked? `tail -f agent/logs/app.log`

**Emergency Fixes**:
```bash
# Clear everything and restart
rm -rf agent/cache agent/vector_db agent/logs
python -m uvicorn agent.backend:app --reload
```

---

## 20+ Error Scenarios

### Error 1: ModuleNotFoundError: No module named 'backend'

**Cause**: Code still references old `backend` module (pre-v0.1.35)

**Error Message**:
```
ModuleNotFoundError: No module named 'backend'
```

**Solution**:
```bash
# Update all imports
find . -type f -name "*.py" -exec sed -i 's/from backend/from agent/g' {} \;
find . -type f -name "*.py" -exec sed -i 's/import backend/import agent/g' {} \;

# Or manually update file
# OLD: from backend.modelmanager import ModelManager
# NEW: from agent.modelmanager import ModelManager
```

---

### Error 2: FileNotFoundError: agent/models/ directory not found

**Cause**: Models directory path changed in v0.1.35

**Error Message**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'agent/models/'
```

**Solution**:
```bash
# Models moved to ./models/ at root level
ls ./models/  # Should exist with gpt4all, embeddings, vosk subdirs

# If missing, create and re-download
python setup.py --download-models
# OR
./setup.ps1  # On Windows
```

---

### Error 3: Port 8000 Already in Use

**Cause**: Another process running on port 8000

**Error Message**:
```
ERROR: Uvicorn server failed to start. Address already in use (Windows)
ERROR: Address already in use (Unix)
```

**Solution** (PowerShell):
```powershell
# Find process on port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object -Property OwningProcess
Get-Process -Id <PID>

# Kill process
Stop-Process -Id <PID> -Force

# Or use different port
python -m uvicorn agent.backend:app --port 8001
```

---

### Error 4: CUDA/GPU Not Available

**Cause**: GPU requested but not available

**Error Message**:
```
RuntimeError: No CUDA GPUs available
```

**Solution**:
```yaml
# agent/config.yaml - Set to use CPU
gpu: false

# Or disable GPU in environment
export GPU=false
python -m uvicorn agent.backend:app
```

---

### Error 5: Insufficient Memory for Model Loading

**Cause**: Not enough RAM for model

**Error Message**:
```
MemoryError: Unable to allocate X GiB for an array
```

**Solution**:
```yaml
# agent/config.yaml - Use smaller model or reduce threads
model_backend: gpt4all
model_args:
  n_threads: 2  # Reduce from 4
  n_gpu_layers: 0  # Force CPU instead of GPU
```

---

### Error 6: Vector DB Corruption

**Cause**: Chroma database corrupted

**Error Message**:
```
ValueError: Chroma index is corrupted
sqlite3.DatabaseError: database disk image is malformed
```

**Solution**:
```bash
# Backup and rebuild
cp -r agent/vector_db agent/vector_db.backup
rm -rf agent/vector_db/chroma*

# Reindex from API
curl -X POST http://localhost:8000/api/reindex

# Or delete and restart
rm -rf agent/vector_db
python -m uvicorn agent.backend:app --reload
```

---

### Error 7: Configuration File Not Found

**Cause**: Missing agent/config.yaml

**Error Message**:
```
FileNotFoundError: agent/config.yaml not found
```

**Solution**:
```bash
# Regenerate from defaults
python -c "from agent.settings import Settings; print(Settings().dict(indent=2))" > agent/config.yaml

# Or copy from backup
cp agent/config.yaml.backup agent/config.yaml
```

---

### Error 8: Invalid JSON in Config File

**Cause**: Syntax error in YAML/JSON

**Error Message**:
```
yaml.YAMLError: mapping values are not allowed
```

**Solution**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('agent/config.yaml'))"

# Or use online validator
# Copy contents to https://www.yamllint.com/

# Fix common issues:
# - Missing colons after keys
# - Inconsistent indentation (use spaces, not tabs)
# - Quotes around values with special characters
```

---

### Error 9: Plugin Not Loading in Obsidian

**Cause**: Plugin file missing or syntax error

**Error Message**:
```
Plugin failed to load: SyntaxError in main.js:10
```

**Solution**:
```bash
# Verify plugin files exist
ls -la plugin/main.js plugin/manifest.json

# Check JavaScript syntax
node -c plugin/main.js

# Fix syntax and reload Obsidian
# Settings → Community Plugins → Reload
# Or restart Obsidian completely

# Check plugin console
# Dev Tools → Console (F12 in most browsers)
```

---

### Error 10: 401 Unauthorized - Invalid Token

**Cause**: Expired or invalid authentication token

**Error Message**:
```
401 Unauthorized: Invalid or expired token
```

**Solution**:
```bash
# Get new token
curl -X POST http://localhost:8000/api/auth/token \
  -d "username=user&password=pass"

# Or use new bearer token
curl -H "Authorization: Bearer <new_token>" \
  http://localhost:8000/api/ask

# In development/testing, skip auth by setting:
export PYTEST_CURRENT_TEST=true
```

---

### Error 11: 422 Validation Error - Missing Fields

**Cause**: Required field missing from request

**Error Message**:
```json
{
  "detail": [
    {"loc": ["body", "question"], "msg": "field required", "type": "value_error.missing"}
  ]
}
```

**Solution**:
```bash
# Include all required fields
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is in my vault?",
    "model": "gpt4all"
  }'

# Check API docs for required fields
# http://localhost:8000/docs
```

---

### Error 12: 429 Rate Limit Exceeded

**Cause**: Too many requests in time window

**Error Message**:
```json
{"error": "Rate limit exceeded", "retry_after": 60}
```

**Solution**:
```bash
# Implement exponential backoff
# Wait 60 seconds (from Retry-After header)
sleep 60
curl http://localhost:8000/api/ask

# Or increase rate limit in config
export RATE_LIMIT=200
export RATE_LIMIT_BURST=20
```

---

### Error 13: 500 Internal Server Error

**Cause**: Unhandled exception in backend

**Error Message**:
```
500 Internal Server Error
```

**Solution**:
```bash
# Check backend logs
tail -50 agent/logs/app.log

# Enable debug logging
export LOG_LEVEL=debug
python -m uvicorn agent.backend:app --reload

# Common causes:
# 1. Model not loaded - check agent/logs/app.log
# 2. Database connection failed - verify agent/vector_db/
# 3. Out of memory - check system resources
# 4. Unhandled exception - review stack trace in logs
```

---

### Error 14: Search Returns No Results

**Cause**: Vector DB not indexed or similarity threshold too high

**Symptoms**:
```json
{"results": []}
```

**Solution**:
```bash
# Check if vault indexed
curl http://localhost:8000/api/scan_vault

# Reindex if needed
curl -X POST http://localhost:8000/api/reindex

# Verify with specific search
curl -X POST http://localhost:8000/api/search \
  -d '{
    "query": "test",
    "top_k": 5,
    "similarity_threshold": 0.5  # Lower threshold
  }'
```

---

### Error 15: Voice Transcription Fails

**Cause**: Vosk model missing or audio format/sample rate wrong

**Error Messages**:
- `RuntimeError: Vosk model not found at ./models/vosk/vosk-model-small-en-us-0.15`
- `Error: Audio must be mono PCM WAV with 16kHz or 8kHz sample rate`
- `JSONDecodeError: Cannot parse Vosk response`

**Solution**:

1. **Verify Vosk Model Installed**:
```bash
# Check if model exists
ls -la ./models/vosk/vosk-model-small-en-us-0.15/

# If missing, download from: https://alphacephei.com/vosk/models
# Example: vosk-model-small-en-us-0.15.zip

# Extract to models/vosk/ directory
unzip vosk-model-small-en-us-0.15.zip -d ./models/vosk/
```

2. **Prepare Audio File (Correct Format)**:
```bash
# Audio must be:
# - Mono (single channel)
# - PCM WAV format
# - 16kHz or 8kHz sample rate

# Convert audio to required format:
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 16000 -ac 1 output.wav

# OR for 8kHz:
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 8000 -ac 1 output.wav
```

3. **Test Voice Transcription**:
```bash
# Upload WAV file for transcription (correct method)
curl -X POST http://localhost:8000/api/voice_transcribe \
  -F "file=@/path/to/audio.wav"

# Response:
# {"transcription": "the transcribed text here"}
```

4. **Verify Vosk Integration**:
```bash
# Check Vosk model loading (Python)
python << 'EOF'
from agent.voice import get_vosk_model
try:
    model = get_vosk_model()
    if model:
        print("✓ Vosk model loaded successfully")
    else:
        print("✗ Vosk model is None - check VOSK_MODEL_PATH")
except RuntimeError as e:
    print(f"✗ Vosk model error: {e}")
EOF
```

5. **Debug Voice Endpoint**:
```bash
# Check voice router is registered
curl http://localhost:8000/docs | grep -i voice

# View endpoint details in OpenAPI spec
curl http://localhost:8000/openapi.json | jq '.paths | keys | .[] | select(contains("voice"))'
```

**Common Issues**:
- ❌ `"Audio must be mono PCM WAV"` → Use `ffmpeg` to convert to mono
- ❌ `"16kHz or 8kHz sample rate"` → Resample audio: `-ar 16000` or `-ar 8000`
- ❌ Vosk model not found → Download from Alphacephei or set `VOSK_MODEL_PATH` env var
- ❌ Large file upload → Audio files should be < 50MB
- ❌ JSON format not working → Use file upload (`-F "file=@..."`) not JSON body

---

### Error 16: Cache Inconsistency Issues

**Cause**: Stale cache or multi-instance cache conflicts

**Symptoms**:
```
Inconsistent results, old data returned
```

**Solution**:
```bash
# Clear all caches
curl -X POST http://localhost:8000/api/performance/cache/clear

# Or manually
rm -rf agent/cache/*

# Restart backend
python -m uvicorn agent.backend:app --reload

# For multi-instance, use Redis
# Update config.yaml:
# cache_backend: redis
# redis_url: redis://localhost:6379
```

---

### Error 17: Embedding Model Not Found

**Cause**: Embedding model not downloaded

**Error Message**:
```
FileNotFoundError: Model 'all-MiniLM-L6-v2' not found
```

**Solution**:
```bash
# Download embeddings model
python -c "from agent.embeddings import EmbeddingsManager; e = EmbeddingsManager.from_settings()"

# Or verify it exists
ls ./models/embeddings/

# Verify model config
grep embed_model agent/config.yaml
```

---

### Error 18: Obsidian Plugin Backend Connection Fails

**Cause**: Backend URL misconfigured or backend down

**Error Message** (in Obsidian console):
```
Error: Failed to connect to backend at http://localhost:8000
```

**Solution**:
```javascript
// In plugin settings, verify backend URL
// Default: http://localhost:8000
// If behind proxy: http://your-domain.com/agent-api

// Check from Obsidian console
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(d => console.log('Backend OK:', d))
  .catch(e => console.log('Backend error:', e.message))

// Or from terminal
curl http://localhost:8000/health
```

---

### Error 19: Enterprise SSO Not Working

**Cause**: Enterprise module not enabled or SSO not configured

**Error Message**:
```
404 Not Found: /api/enterprise/auth/sso
```

**Solution**:
```yaml
# agent/config.yaml - Enable enterprise
enterprise_enabled: true
sso_providers:
  - azure_ad
  - google
  - okta
azure_tenant_id: "your-tenant-id"
google_client_id: "your-client-id"
```

---

### Error 20: Health Check Fails But Backend Running

**Cause**: Health check endpoint issue, but API working

**Symptoms**:
```
GET /health → 500 error
But POST /api/ask → 200 OK
```

**Solution**:
```bash
# Try detailed health check
curl http://localhost:8000/api/health/detailed

# Check which service failed
# Response will show service status

# Common causes:
# 1. Model manager timeout - restart models
# 2. Vector DB issue - reindex
# 3. Cache corrupted - clear cache

# Workaround: Use lightweight status check
curl http://localhost:8000/status  # <100ms response
```

---

### Error 21: API Documentation (Swagger) Won't Load

**Cause**: FastAPI/Swagger initialization issue

**Symptoms**:
```
http://localhost:8000/docs → Blank or error
```

**Solution**:
```bash
# Verify docs are generated
curl http://localhost:8000/openapi.json

# If JSON returns successfully but UI doesn't load:
# 1. Clear browser cache
# 2. Try different browser
# 3. Check browser console for JS errors

# Workaround: Use ReDoc alternative
# http://localhost:8000/redoc
```

---

### Error 22: Tests Failing with Import Errors

**Cause**: Module paths not updated from backend→agent migration

**Error Message**:
```
ImportError: cannot import name 'backend' from 'agent'
```

**Solution**:
```bash
# Update test imports
find tests/ -type f -name "*.py" -exec sed -i 's/from backend/from agent/g' {} \;
find tests/ -type f -name "*.py" -exec sed -i 's/import backend/import agent/g' {} \;

# Also update conftest.py
# OLD: sys.path.insert(0, os.path.join(basedir, "backend"))
# NEW: sys.path.insert(0, os.path.join(basedir, "agent"))

# Verify tests pass
python -m pytest tests/ -v
```

---

## Error Recovery

### Backend Won't Start

**Symptoms**: Server fails to start or crashes immediately

**Possible Causes**:
- Port already in use
- Python environment not configured
- Missing dependencies
- Configuration file errors

**Solutions**:

1. **Check port availability**:
   ```bash
   lsof -i :8000  # Linux/Mac
   netstat -ano | findstr :8000  # Windows
   ```

2. **Verify Python environment**:
   ```bash
   python --version  # Should be 3.11+
   pip list | grep fastapi  # Verify key packages
   ```

3. **Install missing dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Check configuration**:
   ```bash
   cat agent/config.yaml  # Verify settings
   ```

---

### Plugin Not Loading

**Symptoms**: Plugin not visible in Obsidian, or error on startup

**Possible Causes**:
- Plugin file missing
- Manifest.json invalid
- JavaScript syntax error
- Backend unavailable

**Solutions**:

1. **Verify plugin files**:
   ```bash
   ls -la plugin/  # Check all .js files exist
   cat plugin/manifest.json  # Verify JSON syntax
   ```

2. **Check JavaScript syntax**:
   ```bash
   node -c plugin/main.js  # Syntax validation
   ```

3. **Verify backend connection**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Check browser console** (Dev Tools → Console):
   - Look for JavaScript errors
   - Verify plugin initialization messages

---

### API Request Fails

**Symptoms**: 5xx errors, timeouts, or connection refused

**Status Codes**:
- **400** - Bad request (check parameters)
- **401** - Unauthorized (check API key)
- **403** - Forbidden (check permissions)
- **404** - Not found (check endpoint)
- **500** - Server error (check server logs)
- **503** - Service unavailable (backend down)

**Solutions**:

1. **Check backend health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify API key** (if using authentication):
   ```bash
   echo $API_KEY  # Check environment variable
   ```

3. **Check request format**:
   ```bash
   # Example: POST /api/ask
   curl -X POST http://localhost:8000/api/ask \
     -H "Content-Type: application/json" \
     -d '{"prompt":"test"}'
   ```

4. **Review server logs**:
   ```bash
   tail -f agent/logs/app.log
   ```

---

### Model Loading Issues

**Symptoms**: Model fails to load, or AI responses are missing

**Possible Causes**:
- Model file corrupted
- Insufficient RAM/GPU
- Model path incorrect
- CUDA compatibility issue

**Solutions**:

1. **Check model files**:
   ```bash
   ls -lh ./models/  # Verify file sizes (moved from agent/models/ in v0.1.35)
   ```

2. **Verify model configuration**:
   ```bash
   grep "model_backend\|embed_model" agent/config.yaml
   ```

3. **Check system resources**:
   ```bash
   free -h  # Available RAM
   nvidia-smi  # GPU status (if using GPU)
   ```

4. **Reinitialize models**:
   ```bash
   rm -rf agent/models/*.cache
   python -c "from agent.modelmanager import ModelManager; m = ModelManager()"
   ```

---

## Error Recovery

### Database Corruption

**Symptoms**: Vector DB errors, search failures, or data corruption warnings

**Recovery Steps**:

1. **Back up current database**:
   ```bash
   cp -r agent/vector_db agent/vector_db.backup
   ```

2. **Clear corrupted index**:
   ```bash
   rm -rf agent/vector_db/chroma*
   ```

3. **Rebuild from scratch**:
   ```bash
   curl -X POST http://localhost:8000/reindex
   ```

4. **Verify rebuild**:
   ```bash
   curl http://localhost:8000/health
   ```

---

### Cache Issues

**Symptoms**: Stale data, inconsistent results, or cache errors

**Recovery Steps**:

1. **Clear all caches**:
   ```bash
   curl -X POST http://localhost:8000/api/performance/cache/clear
   ```

2. **Or manually clear**:
   ```bash
   rm -rf agent/cache/*
   ```

3. **Restart backend**:
   ```bash
   pkill -f "uvicorn"
   python -m uvicorn backend:app
   ```

4. **Verify cache rebuilt**:
   ```bash
   curl http://localhost:8000/api/performance/metrics
   ```

---

### Configuration Reset

**Symptoms**: Settings invalid or corrupted

**Recovery Steps**:

1. **Back up current config**:
   ```bash
   cp agent/config.yaml agent/config.yaml.backup
   ```

2. **Reset to defaults**:
   ```bash
   rm agent/config.yaml
   ```

3. **Reconfigure**:
   ```bash
   curl -X POST http://localhost:8000/api/config/reload
   ```

4. **Verify configuration**:
   ```bash
   curl http://localhost:8000/api/config
   ```

---

## Backend Issues

### High Memory Usage

**Symptoms**: System slow, OOM errors, or backend crash

**Diagnosis**:
```bash
ps aux | grep python  # Check process memory
free -h  # Available RAM
top -p $(pidof python)  # Real-time monitoring
```

**Solutions**:

1. **Reduce model precision** (config.yaml):
   ```yaml
   model_backend: gpt4all
   model_args:
     n_gpu_layers: 0  # Use CPU instead of GPU
     n_threads: 4      # Reduce thread count
   ```

2. **Clear caches**:
   ```bash
   curl -X POST http://localhost:8000/api/performance/cache/clear
   ```

3. **Reduce connection pool size** (config.yaml):
   ```yaml
   performance:
     max_db_connections: 5
     model_pool_size: 1
   ```

4. **Restart and monitor**:
   ```bash
   systemctl restart obsidian-ai-agent
   watch free -h
   ```

---

### Slow Response Times

**Symptoms**: API requests take >2 seconds, timeouts

**Diagnosis**:
```bash
curl http://localhost:8000/api/performance/metrics  # Check metrics
curl http://localhost:8000/health  # Check component times
```

**Solutions**:

1. **Enable performance monitoring**:
   ```yaml
   performance:
     metrics_enabled: true
     metrics_interval: 10
   ```

2. **Check bottleneck**:
   ```bash
   curl http://localhost:8000/api/performance/metrics | grep -E "cache|queue|pool"
   ```

3. **Optimize caching**:
   ```bash
   curl -X POST http://localhost:8000/api/performance/optimize
   ```

4. **Scale horizontally** (if load balancing):
   - Add more backend instances
   - Configure load balancer
   - Use Redis for shared cache

---

### Connection Timeouts

**Symptoms**: "Connection refused", socket timeout errors

**Diagnosis**:
```bash
netstat -an | grep 8000  # Check if port listening
curl -v http://localhost:8000/health  # Verbose output
```

**Solutions**:

1. **Check if server running**:
   ```bash
   ps aux | grep uvicorn
   ```

2. **Start server** (if not running):
   ```bash
   python -m uvicorn backend:app --host 0.0.0.0 --port 8000
   ```

3. **Check firewall**:
   ```bash
   sudo ufw allow 8000  # Ubuntu/Debian
   sudo firewall-cmd --permanent --add-port=8000/tcp  # RHEL/CentOS
   ```

4. **Increase timeout** (client-side):
   - JavaScript: `timeout: 60000` (milliseconds)
   - Python: `timeout=60` (seconds)

---

## Plugin Issues

### Plugin Button Not Working

**Symptoms**: Button click does nothing, or error message

**Solutions**:

1. **Check browser console** for JavaScript errors
2. **Verify backend is running**: `curl http://localhost:8000/health`
3. **Check network tab** in browser dev tools for failed requests
4. **Reload plugin**:
   - In Obsidian: Settings → Community Plugins → Reload
   - Or restart Obsidian completely

---

### Enterprise Features Unavailable

**Symptoms**: Admin button missing, SSO not working

**Solutions**:

1. **Check if enterprise modules present**:
   ```bash
   ls agent/enterprise_*.py
   ls plugin/enterprise*.js
   ```

2. **Verify enterprise enabled** (config.yaml):
   ```yaml
   enterprise_enabled: true
   ```

3. **Check backend logs** for enterprise errors:
   ```bash
   grep -i enterprise agent/logs/app.log
   ```

4. **Reinstall enterprise components** if missing

---

## API Issues

### 401 Unauthorized

**Cause**: Invalid or missing API key

**Solutions**:

1. **Check API key**:
   ```bash
   echo $API_KEY
   ```

2. **Generate new key** (if needed):
   ```bash
   curl -X POST http://localhost:8000/api/enterprise/auth/sso
   ```

3. **Include in request**:
   ```bash
   curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/api/config
   ```

---

### 422 Validation Error

**Cause**: Invalid request parameters

**Solutions**:

1. **Check request format**:
   ```bash
   # Example: POST /api/ask
   curl -X POST http://localhost:8000/api/ask \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "test question",
       "context": "optional context",
       "model": "gpt4all"
     }'
   ```

2. **Verify required fields** are present

3. **Check API documentation**: `http://localhost:8000/docs` (Swagger UI)

---

### Rate Limiting

**Symptoms**: 429 errors ("Too Many Requests")

**Solutions**:

1. **Check rate limit config** (config.yaml):
   ```yaml
   rate_limiting:
     enabled: true
     requests_per_minute: 100
   ```

2. **Increase limit** if needed:
   ```bash
   curl -X POST http://localhost:8000/api/config \
     -H "Content-Type: application/json" \
     -d '{"rate_limit_requests_per_minute": 200}'
   ```

3. **Implement backoff** (client-side):
   - Wait 1 second, retry
   - If fails, wait 2 seconds, retry
   - Continue doubling wait time

---

## Performance Issues

### Slow Search

**Symptoms**: Search takes >5 seconds

**Solutions**:

1. **Check index size**:
   ```bash
   du -sh agent/vector_db/
   ```

2. **If very large (>10GB)**:
   - Rebuild with smaller chunk size
   - Archive old documents
   - Use separate search instances

3. **Optimize parameters** (config.yaml):
   ```yaml
   vector_db:
     chunk_size: 500  # Reduce from 1000
     chunk_overlap: 50  # Reduce from 200
     top_k: 3  # Reduce from 5
   ```

---

### Slow AI Generation

**Symptoms**: Model takes >30 seconds to respond

**Solutions**:

1. **Check model choice**:
   ```bash
   curl http://localhost:8000/api/config | grep model
   ```

2. **Use faster model** if available
3. **Reduce max tokens**:
   ```yaml
   model_args:
     max_tokens: 256  # Reduce from 512
   ```

4. **Use GPU** (if available):
   ```yaml
   gpu: true
   model_args:
     n_gpu_layers: 33
   ```

---

## Security Issues

### Unauthorized Access Detected

**Symptoms**: Unauthorized access alerts in logs

**Solutions**:

1. **Check access logs**:
   ```bash
   grep "401\|403" agent/logs/app.log
   ```

2. **Review recent API keys**:
   ```bash
   curl http://localhost:8000/api/enterprise/auth/keys
   ```

3. **Revoke suspicious keys**:
   ```bash
   curl -X DELETE http://localhost:8000/api/enterprise/auth/keys/{key_id}
   ```

4. **Change admin password** (if applicable)

---

### SSL/TLS Certificate Error

**Symptoms**: "Certificate not valid", "Cannot verify certificate"

**Solutions**:

1. **Check certificate validity**:
   ```bash
   openssl x509 -in /path/to/cert.pem -text -noout
   ```

2. **Renew certificate** (if expired):
   ```bash
   certbot renew  # Let's Encrypt
   ```

3. **Update config** (config.yaml):
   ```yaml
   ssl:
     cert_path: /path/to/cert.pem
     key_path: /path/to/key.pem
   ```

---

## Getting Help

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=debug
python -m uvicorn backend:app --log-level debug
```

### Collect Diagnostics

```bash
# Create diagnostic report
mkdir /tmp/diagnostics
ps aux | grep python > /tmp/diagnostics/processes.txt
free -h > /tmp/diagnostics/memory.txt
df -h > /tmp/diagnostics/disk.txt
curl http://localhost:8000/health > /tmp/diagnostics/health.json
curl http://localhost:8000/api/performance/metrics > /tmp/diagnostics/metrics.json
tail -100 agent/logs/app.log > /tmp/diagnostics/logs.txt
cp agent/config.yaml /tmp/diagnostics/config.yaml

# Share diagnostics (sanitized)
tar czf diagnostics.tar.gz /tmp/diagnostics/
```

### Support Channels

- **GitHub Issues**: https://github.com/UndiFineD/obsidian-ai-agent/issues
- **Documentation**: Check [DOCUMENTATION.md](DOCUMENTATION.md)
- **FAQ**: See [openspec/docs/faq.md](openspec/docs/faq.md)
- **Configuration**: [CONFIGURATION_API.md](CONFIGURATION_API.md)

### Common Solutions Checklist

- [ ] Tried restarting the backend
- [ ] Checked backend is running (`curl localhost:8000/health`)
- [ ] Verified Python version (should be 3.11+)
- [ ] Confirmed API key is correct
- [ ] Checked firewall/network connectivity
- [ ] Reviewed browser console for JavaScript errors
- [ ] Cleared cache (`curl -X POST localhost:8000/api/performance/cache/clear`)
- [ ] Checked logs for specific error messages
- [ ] Tried in debug mode (`LOG_LEVEL=debug`)
- [ ] Collected diagnostics report

---

**Last Updated**: October 20, 2025  
**Version**: 2.0  
**Maintained By**: Development Team

For more help, see [DOCUMENTATION.md](../DOCUMENTATION.md)

