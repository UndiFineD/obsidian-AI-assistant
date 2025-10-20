# Troubleshooting Guide

**Last Updated**: October 2025  
**For**: Developers, DevOps, and Support Teams

---

## Table of Contents

1. [Common Issues](#common-issues)
2. [Error Recovery](#error-recovery)
3. [Backend Issues](#backend-issues)
4. [Plugin Issues](#plugin-issues)
5. [API Issues](#api-issues)
6. [Performance Issues](#performance-issues)
7. [Security Issues](#security-issues)
8. [Getting Help](#getting-help)

---

## Common Issues

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
   cat backend/config.yaml  # Verify settings
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
   tail -f backend/logs/app.log
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
   ls -lh backend/models/  # Verify file sizes
   md5sum backend/models/*.gguf  # Check integrity
   ```

2. **Verify model configuration**:
   ```bash
   grep "model_backend\|embed_model" backend/config.yaml
   ```

3. **Check system resources**:
   ```bash
   free -h  # Available RAM
   nvidia-smi  # GPU status (if using GPU)
   ```

4. **Reinitialize models**:
   ```bash
   rm -rf backend/models/*.cache
   python -c "from backend.modelmanager import ModelManager; m = ModelManager()"
   ```

---

## Error Recovery

### Database Corruption

**Symptoms**: Vector DB errors, search failures, or data corruption warnings

**Recovery Steps**:

1. **Back up current database**:
   ```bash
   cp -r backend/vector_db backend/vector_db.backup
   ```

2. **Clear corrupted index**:
   ```bash
   rm -rf backend/vector_db/chroma*
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
   rm -rf backend/cache/*
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
   cp backend/config.yaml backend/config.yaml.backup
   ```

2. **Reset to defaults**:
   ```bash
   rm backend/config.yaml
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
   systemctl restart obsidian-ai-assistant
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
   ls backend/enterprise_*.py
   ls plugin/enterprise*.js
   ```

2. **Verify enterprise enabled** (config.yaml):
   ```yaml
   enterprise_enabled: true
   ```

3. **Check backend logs** for enterprise errors:
   ```bash
   grep -i enterprise backend/logs/app.log
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
   du -sh backend/vector_db/
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
   grep "401\|403" backend/logs/app.log
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
tail -100 backend/logs/app.log > /tmp/diagnostics/logs.txt
cp backend/config.yaml /tmp/diagnostics/config.yaml

# Share diagnostics (sanitized)
tar czf diagnostics.tar.gz /tmp/diagnostics/
```

### Support Channels

- **GitHub Issues**: https://github.com/UndiFineD/obsidian-AI-assistant/issues
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
