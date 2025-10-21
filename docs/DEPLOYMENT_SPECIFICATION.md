# 🚀 DEPLOYMENT SPECIFICATION

_Obsidian AI Agent - Production Deployment Guide_
_Version: 0.1.35_
_Date: October 21, 2025_

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Local Deployment](#local-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [Environment Configuration](#environment-configuration)
8. [Scaling & Performance](#scaling--performance)
9. [Health Checks & Monitoring](#health-checks--monitoring)
10. [Troubleshooting](#troubleshooting)
11. [Backup & Recovery](#backup--recovery)

---

## 🎯 Quick Start

### Windows (PowerShell)

```powershell
# Clone repository
git clone https://github.com/UndiFineD/obsidian-AI-assistant.git
cd obsidian-AI-assistant

# Run setup script (handles venv, dependencies, models)
./setup.ps1

# Start backend
cd agent
python -m uvicorn backend:app --host 0.0.0.0 --port 8000

# In separate terminal, install plugin
cd ..
./setup-plugin.ps1 -VaultPath "C:\Users\<user>\Documents\ObsidianVault"
```

### Linux/macOS

```bash
# Clone repository
git clone https://github.com/UndiFineD/obsidian-AI-assistant.git
cd obsidian-AI-assistant

# Run setup script
./setup.sh

# Start backend
cd agent
python -m uvicorn backend:app --host 0.0.0.0 --port 8000

# In separate terminal, install plugin
cd ..
./setup-plugin.sh /path/to/ObsidianVault
```

### Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/health/detailed

# Test API call
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

---

## 💻 System Requirements

### Minimum Requirements (Development)

| Component | Requirement |
|-----------|------------|
| **CPU** | 2 cores, 2.0 GHz minimum |
| **RAM** | 4GB minimum (8GB recommended) |
| **Storage** | 5GB SSD (models take 2-3GB) |
| **Network** | Internet for initial setup |
| **OS** | Windows 10+, macOS 10.15+, Ubuntu 18.04+ |
| **Python** | 3.11+ |

### Production Requirements (Single Server)

| Component | Requirement |
|-----------|------------|
| **CPU** | 8+ cores, 3.5GHz (Intel Xeon/AMD EPYC) |
| **RAM** | 32GB+ (64GB for enterprise) |
| **Storage** | 100GB+ NVMe SSD (3000+ IOPS) |
| **Network** | Gigabit ethernet, <10ms latency |
| **GPU** | NVIDIA RTX 3090+/V100+ (optional, 3-5x faster) |
| **Uptime** | Dedicated hardware or cloud instance |
| **Python** | 3.11+ |

### Production Requirements (Kubernetes Cluster)

| Component | Requirement |
|-----------|------------|
| **Nodes** | 3+ nodes (high availability) |
| **CPU/Node** | 4+ cores |
| **RAM/Node** | 8GB+ |
| **Storage** | Persistent volumes (100GB+) |
| **Load Balancer** | Ingress controller or cloud LB |
| **Networking** | CNI plugin with service mesh (optional) |

---

## 🔧 Local Deployment

### Installation Steps

**Step 1: Environment Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Step 2: Configure Settings**
```bash
# Create config file (copy defaults)
cp agent/config.yaml.example agent/config.yaml

# Edit config (optional)
# agent/config.yaml
vault_path: ./vault
models_dir: ./models
gpu: false  # Set to true if CUDA available
```

**Step 3: Download Models**
```bash
# Models download automatically on first run
# Or manually trigger
python -c "from agent.modelmanager import ModelManager; m = ModelManager.from_settings()"

# Verify models exist
ls ./models/
# Expected: gpt4all/, embeddings/, vosk/
```

**Step 4: Start Backend**
```bash
cd agent
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

**Step 5: Install Plugin**
```bash
# Windows
cd ..
.\setup-plugin.ps1 -VaultPath "C:\path\to\vault"

# Linux/macOS
cd ..
./setup-plugin.sh /path/to/vault
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
# Multi-stage build for production
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY agent/ agent/
COPY ./models ./models
COPY ./.github ./.github

# Set PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "-m", "uvicorn", "agent.backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t obsidian-ai-agent:0.1.35 .

# Run container
docker run -d \
  --name obsidian-ai \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/agent/cache:/app/agent/cache \
  -v $(pwd)/agent/vector_db:/app/agent/vector_db \
  -e GPU=false \
  -e LOG_LEVEL=info \
  obsidian-ai-agent:0.1.35

# Check logs
docker logs -f obsidian-ai

# Stop container
docker stop obsidian-ai
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    image: obsidian-ai-agent:0.1.35
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./agent/cache:/app/agent/cache
      - ./agent/vector_db:/app/agent/vector_db
    environment:
      GPU: "false"
      LOG_LEVEL: "info"
      VAULT_PATH: "./vault"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Redis for multi-instance caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

**Deploy with Docker Compose**:
```bash
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## ☸️ Kubernetes Deployment

### Kubernetes Manifests

**Deployment (deployment.yaml)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: obsidian-ai-agent
  namespace: default
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: obsidian-ai-agent
  template:
    metadata:
      labels:
        app: obsidian-ai-agent
    spec:
      containers:
      - name: backend
        image: obsidian-ai-agent:0.1.35
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: GPU
          value: "false"
        - name: LOG_LEVEL
          value: "info"
        - name: CACHE_BACKEND
          value: "redis"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /status
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 5
        volumeMounts:
        - name: models
          mountPath: /app/models
        - name: cache
          mountPath: /app/agent/cache
        - name: vector-db
          mountPath: /app/agent/vector_db
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
      - name: cache
        persistentVolumeClaim:
          claimName: cache-pvc
      - name: vector-db
        persistentVolumeClaim:
          claimName: vector-db-pvc
```

**Service (service.yaml)**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: obsidian-ai-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: obsidian-ai-agent
```

**PersistentVolumeClaims (pvc.yaml)**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: models-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cache-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: vector-db-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

**Deploy to Kubernetes**:
```bash
# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f pvc.yaml

# Monitor deployment
kubectl get pods -w

# Check logs
kubectl logs -f deployment/obsidian-ai-agent

# Scale replicas
kubectl scale deployment/obsidian-ai-agent --replicas=5

# Get service endpoint
kubectl get svc obsidian-ai-service
```

---

## ☁️ Cloud Deployment

### AWS Elastic Container Service (ECS)

```bash
# Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag obsidian-ai-agent:0.1.35 <account>.dkr.ecr.us-east-1.amazonaws.com/obsidian-ai-agent:0.1.35
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/obsidian-ai-agent:0.1.35

# Create ECS task definition, service, and cluster via CloudFormation or AWS CLI
```

### Azure Container Instances (ACI)

```bash
# Push to Azure Container Registry
az acr build --registry <registry-name> --image obsidian-ai-agent:0.1.35 .

# Deploy container
az container create \
  --resource-group myResourceGroup \
  --name obsidian-ai \
  --image <registry-name>.azurecr.io/obsidian-ai-agent:0.1.35 \
  --ports 8000 \
  --cpu 4 --memory 8 \
  --environment-variables GPU=false LOG_LEVEL=info
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/obsidian-ai-agent:0.1.35

# Deploy to Cloud Run
gcloud run deploy obsidian-ai-agent \
  --image gcr.io/PROJECT_ID/obsidian-ai-agent:0.1.35 \
  --platform managed \
  --region us-central1 \
  --memory 8Gi \
  --cpu 4 \
  --set-env-vars GPU=false,LOG_LEVEL=info
```

---

## 🔧 Environment Configuration

### Environment Variables

**Core Settings**:
```bash
export API_PORT=8000
export DEBUG=false
export LOG_LEVEL=info
export WORKERS=4
```

**Model Settings**:
```bash
export GPU=false
export MODEL_BACKEND=gpt4all
export MODELS_DIR=./models
export EMBED_MODEL=all-MiniLM-L6-v2
```

**Storage Settings**:
```bash
export VAULT_PATH=./vault
export CACHE_DIR=./agent/cache
export VECTOR_DB_DIR=./agent/vector_db
```

**Performance Settings**:
```bash
export CACHE_BACKEND=memory  # or redis, disk
export RATE_LIMIT=100
export RATE_LIMIT_BURST=10
export MAX_CONNECTIONS=1000
```

**Security Settings**:
```bash
export CORS_ORIGINS=http://localhost:3000
export API_KEY_REQUIRED=false
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

**Enterprise Settings**:
```bash
export ENTERPRISE_ENABLED=true
export TENANT_ISOLATION=true
export COMPLIANCE_MODE=gdpr,soc2
```

---

## 📈 Scaling & Performance

### Horizontal Scaling (Multiple Instances)

**Prerequisites**:
- Shared cache (Redis)
- Shared vector database (Chroma cluster)
- Load balancer (nginx, HAProxy, cloud LB)

**Configuration**:
```yaml
# agent/config.yaml
cache_backend: redis
redis_url: redis://redis-cluster:6379
vector_db: chromadb-cluster
vector_db_url: chromadb://chroma-cluster:8000
```

**Scaling Strategy**:
```
1 Instance:   ~500 requests/minute
3 Instances:  ~1,500 requests/minute
5 Instances:  ~2,500 requests/minute
10 Instances: ~5,000 requests/minute
```

### Vertical Scaling (More Powerful Machine)

**CPU Scaling**:
```yaml
# agent/config.yaml
model_args:
  n_threads: 8  # Match CPU cores
```

**GPU Scaling** (3-5x faster):
```yaml
# agent/config.yaml
gpu: true
model_args:
  n_gpu_layers: 33  # Offload to GPU
```

**Memory Tuning**:
```yaml
# agent/config.yaml
cache:
  l1_max_size: 1024  # MB
  l2_max_size: 5120  # MB
performance:
  model_pool_size: 3
  max_db_connections: 10
```

---

## 🏥 Health Checks & Monitoring

### Liveness Check (Every 30s)

```bash
curl -f http://localhost:8000/status || exit 1
```

### Readiness Check (Every 10s)

```bash
curl -f http://localhost:8000/health || exit 1
```

### Detailed Health Monitoring

```bash
# Full service status
curl http://localhost:8000/api/health/detailed | jq '.'

# Performance metrics
curl http://localhost:8000/api/performance/metrics | jq '.cache'

# Security status
curl http://localhost:8000/api/security/status | jq '.'
```

### Monitoring Stack

**Recommended Stack**:
- **Metrics**: Prometheus
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger
- **Alerting**: AlertManager

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000

# Linux/macOS
lsof -i :8000

# Kill process
# Windows
taskkill /PID <PID> /F

# Linux/macOS
kill -9 <PID>

# Use different port
python -m uvicorn agent.backend:app --port 8001
```

### Out of Memory

```bash
# Reduce model precision
model_args:
  n_gpu_layers: 0  # Use CPU
  n_threads: 2     # Reduce threads

# Clear cache
curl -X POST http://localhost:8000/api/performance/cache/clear

# Check memory usage
# Windows
Get-Process python | Select-Object ProcessName, @{Name="MemoryMB"; Expression={[int]($_.WorkingSet/1MB)}}

# Linux/macOS
ps aux | grep python
```

### Container Won't Start

```bash
# Check Docker logs
docker logs obsidian-ai

# Check resource limits
docker stats obsidian-ai

# Increase resource allocation
docker run --memory 8g --cpus 4 ...
```

---

## 💾 Backup & Recovery

### Backup Strategy

**Daily Backups**:
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/obsidian-ai"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup vector database
cp -r ./agent/vector_db "$BACKUP_DIR/vector_db_$TIMESTAMP"

# Backup configuration
cp ./agent/config.yaml "$BACKUP_DIR/config_$TIMESTAMP.yaml"

# Backup vault data
cp -r ./vault "$BACKUP_DIR/vault_$TIMESTAMP"

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR"
```

### Recovery Procedure

```bash
# 1. Stop application
docker stop obsidian-ai

# 2. Restore vector database
rm -rf ./agent/vector_db
cp -r /backups/obsidian-ai/vector_db_<TIMESTAMP> ./agent/vector_db

# 3. Restore configuration
cp /backups/obsidian-ai/config_<TIMESTAMP>.yaml ./agent/config.yaml

# 4. Restart application
docker start obsidian-ai

# 5. Verify
curl http://localhost:8000/health
```

---

## 📊 Performance Benchmarks

**Target Response Times**:
- Health check: <100ms
- Cached search: <200ms
- Uncached search: <1s
- AI generation: <2s
- Vault reindex: <5s

**Tested on**:
- CPU: Intel i7-10700K (8 cores)
- RAM: 32GB
- SSD: Samsung 970 EVO (1TB)
- Python 3.11
- gpt4all-7b model

**Results**:
- Throughput: 200-400 requests/minute
- Average latency: 150-300ms
- Peak latency: <2s
- 99th percentile: <1.5s

---

**Last Updated**: October 21, 2025
**Version**: 0.1.35
**Maintained By**: Development Team
