# Frequently Asked Questions (FAQ)

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Status**: ✅ PRODUCTION-READY

---

## Quick Navigation

- [Setup & Installation](#setup--installation)
- [Basic Usage](#basic-usage)
- [Voice Features](#voice-features)
- [Enterprise Features](#enterprise-features)
- [Performance & Optimization](#performance--optimization)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)

---

## Setup & Installation

### Q1: What are the minimum system requirements?

**A**: Minimum requirements vary by use case:

- **Individual User**: 2 CPU cores, 4GB RAM, 20GB SSD, optional GPU
- **Small Team**: 4 CPU cores, 8GB RAM, 50GB SSD
- **Enterprise**: 16 CPU cores, 32GB RAM, 200GB SSD, GPU recommended

For detailed requirements, see [System Requirements](docs/CONFIGURATION_API.md#minimum-requirements).

### Q2: How do I install the plugin?

**A**: 
1. Download plugin files to `.obsidian/plugins/obsidian-ai-assistant/`
2. Enable plugin in Obsidian settings (Community plugins section)
3. Configure backend URL in plugin settings (default: `http://localhost:8000`)
4. Test connection with health check endpoint

See [Setup Guide](docs/CONFIGURATION_API.md) for detailed steps.

### Q3: Can I run this on Windows/Mac/Linux?

**A**: Yes! Supported platforms:
- **Windows 10+** - Python 3.11+, Docker Desktop
- **macOS 10.15+** - Python 3.11+, Docker Desktop
- **Ubuntu 20.04+** - Python 3.11+, Docker or native

Setup scripts provided for all platforms in `setup.ps1` (Windows) or `setup.sh` (Linux/Mac).

### Q4: How do I deploy using Docker?

**A**: Quick start:
```bash
docker-compose up -d
```

For production deployment with load balancing, see [Docker Deployment Guide](docs/CONFIGURATION_API.md#docker-deployment).

### Q5: What Python version is required?

**A**: **Python 3.11 or higher** is required. Check your version:
```bash
python --version
```

If you need to install Python 3.11+, see [Python Installation Guide](docs/CONFIGURATION_API.md).

### Q6: How do I index my vault?

**A**: 
```bash
# Option 1: Via API
curl -X POST http://localhost:8000/api/reindex \
  -H "Content-Type: application/json" \
  -d '{"vault_path": "/path/to/vault"}'

# Option 2: In Obsidian UI
# Click "Reindex Vault" button in AI panel
```

Indexing typically takes 1-10 minutes depending on document count.

### Q7: How do I update to the latest version?

**A**:
```bash
git pull origin main
pip install -r requirements.txt
# Restart backend
```

See [Migration Guide](docs/MIGRATION_GUIDE.md) for v0.1.34 → v0.1.35 upgrade details.

---

## Basic Usage

### Q8: How do I search my documents?

**A**: In the Obsidian AI panel:
1. Type your question in the search box
2. Press Enter or click Search
3. Results appear in order of relevance
4. Click document titles to open them

Example: "What is our Q1 2024 roadmap?"

### Q9: What query types are supported?

**A**: The system supports:
- **Questions**: "What is...?", "How do I...?"
- **Keywords**: "roadmap", "API authentication"
- **Phrases**: "Q1 2024 priorities"
- **Boolean**: "authentication AND security"
- **Semantic**: "Our strategic direction for next quarter"

### Q10: Why are my search results not relevant?

**A**: Check these factors:
1. **Indexing**: Ensure vault is indexed with `POST /api/reindex`
2. **Keywords**: Your query should match document content
3. **Embeddings**: Similarity threshold may need adjustment (default: 0.7)
4. **Documents**: Add more documents if vault is small

Adjust similarity threshold in config:
```yaml
vector_db:
    similarity_threshold: 0.65  # Lower for more results
```

### Q11: Can I search across multiple vaults?

**A**: Yes! Configure multiple vault paths:
```yaml
vault_paths:
    - /path/to/vault1
    - /path/to/vault2
    - /path/to/vault3
```

All documents are indexed into shared vector database for unified search.

### Q12: How do I export search results?

**A**: 
1. In search results, click Export
2. Choose format: PDF, Markdown, or JSON
3. Results saved to disk

Alternatively, copy results from UI directly.

### Q13: What's the maximum query response time?

**A**: 
- **Cached query**: 200-300ms
- **First query**: 500-800ms
- **Uncached large vault**: 1-2 seconds

Times vary based on vault size and system resources. See [Performance Guide](docs/PERFORMANCE_TUNING.md).

---

## Voice Features

### Q14: How do I enable voice queries?

**A**:
1. Ensure Vosk model is downloaded: `./models/vosk-model-small-en-us-0.15/`
2. Click voice button in Obsidian
3. Speak your question clearly
4. Release button when done

See [Voice Setup Guide](docs/USE_CASES.md#use-case-2-voice-query-workflow).

### Q15: What audio formats are supported?

**A**: 
- **Format**: PCM WAV (.wav files)
- **Channels**: Mono (1 channel)
- **Sample Rate**: 16kHz or 8kHz
- **Bit Depth**: 16-bit

For other formats, convert with ffmpeg:
```bash
ffmpeg -i audio.mp3 -ar 16000 -ac 1 -f wav audio.wav
```

### Q16: Why isn't my voice being recognized?

**A**: 
1. **Microphone**: Check browser microphone permissions
2. **Vosk Model**: Verify model in `./models/vosk/`
3. **Audio Quality**: Speak clearly, reduce background noise
4. **Language**: Default is English (US)

For detailed troubleshooting, see [Voice Troubleshooting](docs/TROUBLESHOOTING.md#voice-transcription-issues).

### Q17: Can I use a different speech recognition model?

**A**: Yes, download alternative models from [Vosk](https://alphacephei.com/vosk/models):
- Small model: `vosk-model-small-en-us-0.15` (default, ~50MB)
- Medium model: `vosk-model-en-us-dayton-20200905-512` (~200MB, better accuracy)
- Large model: `vosk-model-en-us-0.42-gigaspeech` (~2GB, best accuracy)

Extract to `./models/vosk/` and configure in settings.

### Q18: Is voice processing done locally or in the cloud?

**A**: **Fully local** - all voice processing happens on your machine using Vosk. No audio is sent to cloud services. This ensures privacy and works offline.

---

## Enterprise Features

### Q19: How do I enable enterprise features?

**A**:
```bash
export ENTERPRISE_ENABLED=true
export JWT_SECRET_KEY="your-secret-key-min-32-chars"
export ENCRYPTION_KEY="your-encryption-key"
```

Or in `agent/config.yaml`:
```yaml
enterprise:
    enabled: true
```

See [Enterprise Setup Guide](docs/ENTERPRISE_FEATURES_SPECIFICATION.md#enterprise-setup--configuration-guide).

### Q20: How do I set up SSO with Azure AD?

**A**: 
1. Register app in Azure Portal
2. Get client ID and secret
3. Set environment variables:
```bash
export SSO_PROVIDER=azure_ad
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

For detailed steps, see [Azure AD Configuration](docs/ENTERPRISE_FEATURES_SPECIFICATION.md#azure-ad-configuration).

### Q21: How do I create multiple tenants?

**A**:
```bash
curl -X POST http://localhost:8000/api/enterprise/tenants \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Sales Team",
    "admin_email": "admin@sales.com",
    "tier": "professional"
  }'
```

Tenant tiers:
- **BASIC**: 1-10 users, 1K documents
- **PROFESSIONAL**: 11-100 users, 10K documents
- **ENTERPRISE**: 100+ users, 100K documents
- **CUSTOM**: Unlimited (custom pricing)

### Q22: How do I assign users to roles?

**A**:
```bash
curl -X POST http://localhost:8000/api/enterprise/users/{user_id}/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"roles": ["user", "power_user"]}'
```

Available roles: `READONLY`, `USER`, `POWER_USER`, `TEAM_ADMIN`, `TENANT_ADMIN`, `SYSTEM_ADMIN`

See [RBAC Documentation](docs/ENTERPRISE_FEATURES_SPECIFICATION.md#role-based-access-control-rbac) for permissions matrix.

### Q23: How do I handle GDPR data subject requests?

**A**:
```bash
# Submit data access request
curl -X POST http://localhost:8000/api/enterprise/compliance/gdpr/requests \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"request_type": "access"}'

# User receives download link with encrypted data
```

For deletion requests, use `"request_type": "erasure"`.

See [GDPR Procedures](docs/ENTERPRISE_FEATURES_SPECIFICATION.md#gdpr-data-subject-rights).

### Q24: How do I audit who accessed what?

**A**:
```bash
curl -X GET http://localhost:8000/api/enterprise/audit?user_id=xxx \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Response includes:
- User ID, timestamp, action
- Document accessed, permissions granted
- IP address, user agent

Enable audit logging in config:
```yaml
enterprise:
    audit_logging: true
    audit_retention_days: 2555  # 7 years
```

---

## Performance & Optimization

### Q25: How do I speed up searches?

**A**: 
1. **Enable caching**:
```yaml
cache:
    backend: redis  # or memory for single instance
    ttl_seconds: 3600
```

2. **Adjust chunk size**:
```yaml
vector_db:
    chunk_size: 1000  # Smaller = faster, less accurate
```

3. **Use GPU** (if available):
```yaml
gpu: true
```

See [Performance Tuning Guide](docs/PERFORMANCE_TUNING.md).

### Q26: What's the difference between caching backends?

**A**: 

| Backend | Speed | Persistence | Multi-Instance |
|---------|-------|-------------|-----------------|
| Memory | ⚡ Fastest | No | No |
| Redis | ⚡ Fast | Yes | Yes |
| Disk | Slower | Yes | No |

For teams, use Redis. For single users, memory cache is fine.

### Q27: How do I configure GPU acceleration?

**A**:
```yaml
gpu: true
cuda_enabled: true
device_id: 0  # GPU ID if multiple GPUs
```

Requires:
- NVIDIA GPU with CUDA 11.8+
- `nvidia-docker` or NVIDIA container toolkit
- Appropriate Python packages (handled by setup)

Performance: **2-5x faster** embeddings with GPU.

### Q28: What's the recommended config for 100 users?

**A**: 
```yaml
# Production config for 100 users
workers: 4
max_connections: 500
cache:
    backend: redis
    ttl_seconds: 3600

vector_db:
    chunk_size: 1000
    top_k: 5
    similarity_threshold: 0.7

gpu: true  # Strongly recommended
```

Infrastructure: 16 CPU cores, 32GB RAM, 1 GPU minimum.

### Q29: How do I monitor performance?

**A**:
```bash
# Real-time metrics
curl http://localhost:8000/api/performance/metrics

# Health check with details
curl http://localhost:8000/api/health/detailed

# Check cache hit rate
curl http://localhost:8000/api/cache/stats
```

---

## Troubleshooting

### Q30: Backend won't start - port already in use

**A**:
```bash
# Option 1: Use different port
export API_PORT=8001
python -m uvicorn agent.backend:app --port 8001

# Option 2: Kill existing process
lsof -i :8000
kill -9 <PID>
```

### Q31: "Backend connection refused" error

**A**: 
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check firewall rules
3. Verify plugin backend URL is correct
4. Check backend logs: `tail -f agent/logs/`

### Q32: Vault indexing fails or is very slow

**A**:
1. **Check vault size**: 
```bash
find /path/to/vault -type f | wc -l
```

2. **Enable debug logging**:
```bash
export LOG_LEVEL=debug
```

3. **Try partial indexing**:
```bash
# Index specific directory
curl -X POST http://localhost:8000/api/reindex \
  -d '{"vault_path": "/path/to/vault", "max_files": 1000}'
```

For vault with 100K+ files, consider splitting into multiple instances.

### Q33: GPU out of memory errors

**A**:
```yaml
# Reduce batch size
model_max_batch_size: 32  # Default: 128
embeddings_batch_size: 64  # Default: 256

# Or disable GPU
gpu: false
```

### Q34: "Authorization failed" or "Invalid token" errors

**A**: 
1. **Verify JWT secret** is consistent across all nodes
2. **Check token expiry**:
```bash
curl http://localhost:8000/api/health | jq .auth.token_expiry
```

3. **Time sync**: Ensure system time synchronized (within 5 min of backend)

For SSO users:
- Verify IdP certificate is valid
- Check identity provider logs
- Ensure redirect URI exactly matches configuration

### Q35: Models not loading or "CUDA out of memory"

**A**:
```bash
# Check model in models directory
ls -lh ./models/*.gguf

# Verify model format
file ./models/my-model.gguf

# Test model loading
python -c "from llama_cpp import Llama; Llama('./models/my-model.gguf')"

# If out of memory, use smaller model or CPU inference
export GPU=false
```

---

## Advanced Features

### Q36: Can I use a custom model?

**A**: Yes! Prepare GGUF-format model:
```bash
# Copy model
cp ./my-model.gguf ./models/

# Configure
# In agent/config.yaml:
model_backend: gpt4all
model_name: my-model.gguf

# Restart backend
```

See [Custom Model Guide](docs/USE_CASES.md#use-case-6-custom-model-integration).

### Q37: How do I deploy to Kubernetes?

**A**: Use provided Kubernetes manifests:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

For enterprise deployment with SSO, see [Kubernetes Guide](docs/CONFIGURATION_API.md#kubernetes-deployment).

### Q38: Can I use Redis for distributed caching?

**A**: Yes! Configure Redis:
```yaml
cache:
    backend: redis
    redis_url: "redis://redis-server:6379"
    ttl_seconds: 3600
```

This enables cache sharing across multiple backend instances.

### Q39: How do I integrate with external systems?

**A**: Use enterprise integration endpoints:
```bash
POST /api/enterprise/integrations/register
```

Supported integrations:
- Slack notifications
- JIRA ticket creation
- Salesforce CRM sync
- Custom webhooks

Contact enterprise support for custom integrations.

### Q40: How do I export the entire vector database?

**A**:
```bash
# Export to JSON
curl -X POST http://localhost:8000/api/vector_db/export \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -o vector_db_backup.json

# Restore from backup
curl -X POST http://localhost:8000/api/vector_db/import \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@vector_db_backup.json"
```

---

## Still Need Help?

- 📖 **Full Documentation**: See [docs/](docs/) directory
- 🚀 **Use Cases**: Check [docs/USE_CASES.md](docs/USE_CASES.md)
- ⚙️ **Configuration**: See [docs/CONFIGURATION_API.md](docs/CONFIGURATION_API.md)
- 🐛 **Debugging**: Review [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- 📞 **Support**: Contact support@obsidian-ai.com (enterprise)

---

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
