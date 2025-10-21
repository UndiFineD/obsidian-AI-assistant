# Real-World Use Case Examples

**Version**: 1.0  
**Last Updated**: October 21, 2025  
**Status**: ✅ PRODUCTION-READY

This document provides complete end-to-end workflow examples for common Obsidian AI Assistant scenarios.

---

## Use Case 1: Knowledge Worker - Semantic Search Workflow

### Scenario
Product manager at SaaS company searches across 2 years of product documentation to find Q1 roadmap priorities.

### Requirements
- Obsidian 1.4.0+
- Plugin installed
- 500+ markdown documents in vault
- Backend running locally or remote
- 10+ minutes for indexing

### Step-by-Step Implementation

**Step 1: Enable Plugin**

1. Copy plugin files to `.obsidian/plugins/obsidian-ai-assistant/`
2. Enable plugin in Obsidian settings
3. Configure backend URL (default: `http://localhost:8000`)

**Step 2: Index Your Vault**

```javascript
// In plugin main.js startup:
async function initializePlugin() {
    const plugin = new ObsidianAIAssistant();
    await plugin.indexVault();
    console.log("Vault indexed successfully");
}
```

Manually trigger indexing:
```bash
curl -X POST http://localhost:8000/api/reindex \
  -H "Content-Type: application/json" \
  -d '{"vault_path": "/path/to/vault"}'
```

**Step 3: Execute Search Query**

In Obsidian, open the AI panel and type:
```
What are our Q1 2024 roadmap priorities?
```

The system:
1. Generates query embedding
2. Searches vector database
3. Returns top 5 relevant documents
4. Displays results with relevance scores

**Step 4: Review and Export**

- View results in Obsidian
- Click document titles to open
- Export as PDF or markdown
- Copy relevant sections to clipboard

### Expected Output

```json
{
  "query": "What are our Q1 2024 roadmap priorities?",
  "results": [
    {
      "title": "Q1 2024 Product Roadmap.md",
      "relevance": 0.89,
      "excerpt": "Q1 2024 focuses on: 1) API v2 launch, 2) Dashboard redesign, 3) Performance optimization",
      "file_path": "planning/roadmap/2024-q1.md"
    },
    {
      "title": "Product Meeting 2024-01-15.md",
      "relevance": 0.82,
      "excerpt": "Priorities discussed: API stability, user onboarding, analytics improvements",
      "file_path": "meetings/2024-01-15.md"
    }
  ]
}
```

### Performance Metrics
- Index time: ~10 minutes for 500 documents
- Query time: 200-300ms (cached)
- Memory usage: ~200MB
- Storage: ~50MB for embeddings

### Troubleshooting

**Problem**: Search returns no results
- **Solution**: Verify vault is indexed with `GET /status`
- **Check**: Ensure documents contain relevant keywords
- **Try**: Use simpler search terms

**Problem**: Queries take >1 second
- **Solution**: Enable caching with `POST /api/cache/optimize`
- **Check**: Monitor system resources (`GET /api/performance/metrics`)
- **Scale**: Add GPU acceleration if available

---

## Use Case 2: Voice Query Workflow

### Scenario
Engineer at standing desk verbally queries API documentation without hands.

### Requirements
- Obsidian with plugin
- Microphone
- Vosk model downloaded (`vosk-model-small-en-us-0.15`)
- Backend with voice endpoint enabled
- 500MB disk for model

### Step-by-Step Implementation

**Step 1: Download Vosk Model**

```bash
# Models stored in ./models/vosk/
mkdir -p ./models/vosk/
cd ./models/vosk/
# Download from https://alphacephei.com/vosk/models
unzip vosk-model-small-en-us-0.15.zip
```

**Step 2: Enable Voice in Plugin**

```javascript
// plugin/main.js
async function setupVoiceCapture() {
    const recorder = new AudioRecorder();
    const voiceButton = document.getElementById("voice-btn");
    
    voiceButton.addEventListener("click", async () => {
        const audio = await recorder.startRecording();
        const transcript = await this.backendClient.transcribe(audio);
        this.executeQuery(transcript);
    });
}
```

**Step 3: Record and Transcribe**

1. Click voice button in Obsidian
2. Speak question: "What's the authentication flow?"
3. Release button when done
4. Wait 1-2 seconds for transcription

**Step 4: Results Displayed**

Same as Use Case 1, but triggered by voice input.

### Example Voice Queries

- "Show me the API documentation"
- "What's the authentication flow?"
- "How do we handle rate limiting?"
- "Find examples of error handling"

### Expected Output

```json
{
  "audio_duration_seconds": 3.2,
  "transcript": "What's the authentication flow?",
  "confidence": 0.94,
  "search_results": [
    {
      "title": "Authentication Flow - API v2.md",
      "relevance": 0.91
    }
  ]
}
```

### Performance Metrics
- Transcription time: 1-2 seconds
- Search time: 0.3 seconds
- Total latency: 1.5-2.5 seconds
- Model memory: ~50MB

### Troubleshooting

**Problem**: Microphone not recognized
- **Solution**: Check browser microphone permissions
- **Check**: Test with `navigator.mediaDevices.enumerateDevices()`

**Problem**: Transcript is garbled
- **Solution**: Speak clearly, close background noise
- **Try**: Use Vosk medium model for better accuracy

---

## Use Case 3: Small Team Setup - Multi-User

### Scenario
5-person engineering team shares Obsidian AI knowledge base.

### Requirements
- Ubuntu 20.04+ server
- Docker and Docker Compose
- 8GB RAM, 50GB disk
- Public or private network access
- SSL certificate (recommended)

### Step-by-Step Implementation

**Step 1: Deploy with Docker**

```yaml
# docker-compose.yml
version: '3'
services:
  backend:
    image: obsidian-ai-agent:latest
    ports:
      - "8000:8000"
    environment:
      - ENTERPRISE_ENABLED=false
      - API_PORT=8000
      - VAULT_PATH=/shared_vault
      - MODELS_DIR=/models
    volumes:
      - ./shared_vault:/shared_vault
      - ./models:/models
      - ./agent/cache:/app/agent/cache
      - ./agent/vector_db:/app/agent/vector_db
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - backend
    restart: always
```

**Step 2: Configure for Team Access**

```bash
# Create shared vault directory
mkdir -p /shared_vault
chmod 755 /shared_vault

# Add team documents
cp -r /path/to/team/docs /shared_vault/

# Start stack
docker-compose up -d

# Index vault
curl -X POST http://localhost:8000/api/reindex
```

**Step 3: Create User Accounts**

```bash
# Create 5 users with basic role
for i in {1..5}; do
  USER="engineer$i@company.com"
  curl -X POST http://localhost:8000/api/users \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d "{\"email\": \"$USER\", \"role\": \"user\"}"
done
```

**Step 4: Team Connects**

Each team member:
1. Installs plugin in their Obsidian vault
2. Sets backend URL: `http://team-server.company.com`
3. Logs in with credentials
4. Searches shared documents

### Expected Setup

- 5 concurrent users
- Shared 500+ documents
- All search same indexed content
- Queries complete in <500ms

### Performance Metrics
- Backend memory: ~300MB for 5 users
- Search latency: 200-400ms p95
- Concurrent capacity: 20+ users on 8GB
- Uptime: 99%+

---

## Use Case 4: Enterprise Deployment - Multi-Tenant with SSO

### Scenario
Enterprise with Sales and Engineering teams needs isolated knowledge bases with SSO.

### Requirements
- Kubernetes cluster (3+ nodes)
- Azure AD tenant
- 32GB RAM minimum
- HTTPS certificate
- Enterprise license

### Step-by-Step Implementation

**Step 1: Deploy to Kubernetes**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: obsidian-ai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: obsidian-ai
  template:
    metadata:
      labels:
        app: obsidian-ai
    spec:
      containers:
      - name: backend
        image: obsidian-ai-agent:v0.1.35
        ports:
        - containerPort: 8000
        env:
        - name: ENTERPRISE_ENABLED
          value: "true"
        - name: SSO_PROVIDER
          value: "azure_ad"
        - name: AZURE_TENANT_ID
          valueFrom:
            secretKeyRef:
              name: azure-secrets
              key: tenant-id
        - name: AZURE_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: azure-secrets
              key: client-id
        - name: AZURE_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: azure-secrets
              key: client-secret
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
```

**Step 2: Configure Azure AD Integration**

```bash
# Create 2 tenants in database
curl -X POST http://backend:8000/api/enterprise/tenants \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Sales Team",
    "admin_email": "sales-admin@company.com",
    "tier": "professional"
  }'

curl -X POST http://backend:8000/api/enterprise/tenants \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Engineering",
    "admin_email": "eng-admin@company.com",
    "tier": "enterprise"
  }'
```

**Step 3: Assign Users via Azure AD**

In Azure AD:
1. Create "Sales Team" group
2. Create "Engineering" group
3. Add users to respective groups
4. Backend automatically provisions users to correct tenant

**Step 4: Verify Isolation**

```bash
# Sales user sees only sales documents
curl -X POST http://backend:8000/api/ask \
  -H "Authorization: Bearer $SALES_TOKEN" \
  -d '{"prompt": "What is our sales strategy?"}'
# Returns: sales docs + conversations

# Engineering user sees only engineering docs
curl -X POST http://backend:8000/api/ask \
  -H "Authorization: Bearer $ENG_TOKEN" \
  -d '{"prompt": "What is our system architecture?"}'
# Returns: engineering docs + conversations (different from sales)
```

### Expected Results

- Sales Team: 50 users, 10K documents, professional features
- Engineering: 30 users, 20K documents, enterprise features
- Query latency: <300ms p95
- Availability: 99.9% SLA

### Performance Metrics
- Nodes: 3 (1 primary, 2 replicas)
- Memory: 32GB total
- Queries/sec: 1000+
- Concurrent users: 200+

---

## Use Case 5: Compliance - GDPR Data Subject Request

### Scenario
European user requests data export (GDPR Article 15).

### Requirements
- Enterprise mode enabled
- GDPR module active
- User database configured
- Email service configured

### Step-by-Step Implementation

**Step 1: User Submits Request**

Via Obsidian UI or API:
```bash
curl -X POST http://backend:8000/api/enterprise/compliance/gdpr/requests \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{
    "request_type": "access",
    "user_id": "user@company.com"
  }'
```

**Step 2: System Processes Request**

Backend automatically:
1. Identifies all user data
2. Exports documents in JSON
3. Exports metadata (created, modified, accessed dates)
4. Exports access logs
5. Compresses and encrypts with AES-256
6. Generates secure download link

**Step 3: User Downloads Data**

```bash
# Email sent to user with download link
# Link valid for 7 days
# Example: https://backend/api/enterprise/gdpr/download/request-id-xxx

curl -X GET https://backend/api/enterprise/gdpr/download/request-id-xxx \
  -H "Authorization: Bearer $USER_TOKEN" > user_data.zip.enc

# User decrypts with provided password
```

**Step 4: System Cleanup**

- Download link expires after 7 days
- Encrypted export deleted from server
- Completion logged to audit trail

### Expected Results

- Export size: ~50MB for typical user
- Processing time: 1-5 minutes
- Delivery: Email within 1 hour
- Retention: 30 day hold before deletion

### Verification

```bash
# Check GDPR request status
curl -X GET http://backend:8000/api/enterprise/compliance/gdpr/requests \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Example response:
{
  "requests": [
    {
      "request_id": "req-123",
      "user_id": "user@company.com",
      "type": "access",
      "status": "completed",
      "submitted_at": "2025-10-21T10:00:00Z",
      "completed_at": "2025-10-21T10:15:00Z",
      "download_link": "https://backend/download/req-123",
      "expires_at": "2025-10-28T10:15:00Z"
    }
  ]
}
```

---

## Use Case 6: Custom Model Integration

### Scenario
Company wants to use fine-tuned model trained on internal documentation.

### Requirements
- GGUF-format model file
- 4GB+ VRAM (GPU optional)
- Model file in `./models/`
- Backend configuration

### Step-by-Step Implementation

**Step 1: Prepare Custom Model**

```bash
# Export your fine-tuned model to GGUF format
# (using llama.cpp or similar tool)
python export_to_gguf.py \
  --model-path ./my-model \
  --output-path ./my-model.gguf

# Verify model loads
python -c "from llama_cpp import Llama; m = Llama('./my-model.gguf')"
```

**Step 2: Add to Models Directory**

```bash
cp ./my-model.gguf ./models/
chmod 644 ./models/my-model.gguf
```

**Step 3: Configure Backend**

```yaml
# agent/config.yaml
model_backend: gpt4all
model_name: my-model.gguf  # Use custom model
model_context_window: 4096
model_temperature: 0.7
```

**Step 4: Restart Backend and Test**

```bash
# Restart backend
systemctl restart obsidian-ai-backend

# Test with custom model
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain our system architecture",
    "model": "my-model.gguf"
  }'

# Response uses custom model with company-specific knowledge
```

### Performance Metrics
- Model load time: 2-5 seconds
- Inference latency: 100-500ms per token
- Memory: Variable (model size dependent)
- Throughput: 10-20 tokens/sec

---

## Quick Decision Tree

**Choose Use Case Based On**:

```
START
  ├─ Single user searching own docs?
  │  └─ Use Case 1: Knowledge Worker ✓
  │
  ├─ Want to use voice?
  │  └─ Use Case 2: Voice Query ✓
  │
  ├─ Small team (2-10 people)?
  │  └─ Use Case 3: Multi-User Setup ✓
  │
  ├─ Enterprise with multiple departments?
  │  └─ Use Case 4: Multi-Tenant Enterprise ✓
  │
  ├─ Need GDPR compliance?
  │  └─ Use Case 5: Compliance ✓
  │
  ├─ Using custom fine-tuned model?
  │  └─ Use Case 6: Custom Model ✓
  │
  └─ Other scenario?
     └─ See documentation or reach out
```

---

## Appendix A: Environment Setup Reference

### Minimum Requirements by Use Case

| Use Case | CPU | RAM | Storage | GPU |
|----------|-----|-----|---------|-----|
| Knowledge Worker | 2 core | 4GB | 20GB | Optional |
| Voice Query | 2 core | 4GB | 20GB | Optional |
| Small Team (5) | 4 core | 8GB | 50GB | No |
| Enterprise | 16 core | 32GB | 200GB | Yes |
| Compliance | 8 core | 16GB | 100GB | No |
| Custom Model | 4 core | 8GB | 30GB | Yes |

### Quick Setup Checklist

- [ ] Backend installed and running
- [ ] Plugin installed in Obsidian
- [ ] Backend URL configured in plugin
- [ ] Vault indexed (POST /api/reindex)
- [ ] First search executed successfully
- [ ] Results displayed in plugin
- [ ] Export functionality verified

---

## Support & Troubleshooting

For issues specific to your use case:

1. **Check the troubleshooting section** in your use case above
2. **Enable debug logging**: `export LOG_LEVEL=debug`
3. **Check backend health**: `curl http://localhost:8000/health`
4. **View metrics**: `curl http://localhost:8000/api/performance/metrics`
5. **Review logs**: `tail -f /path/to/logs/`

Need more help? See `docs/TROUBLESHOOTING.md` for comprehensive debugging guide.
