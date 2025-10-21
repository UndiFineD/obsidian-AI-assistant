# Performance Tuning Guide

**Version**: 1.0  
**Last Updated**: October 21, 2025  
**Status**: ✅ Production Ready  
**Target Audience**: DevOps, System Administrators, Performance Engineers

---

## Quick Navigation

- [Performance Tiers & SLAs](#performance-tiers--slas)
- [Caching Strategies](#caching-strategies)
- [Model Selection & Tuning](#model-selection--tuning)
- [System Optimization](#system-optimization)
- [Monitoring & Metrics](#monitoring--metrics)
- [Real-World Tuning Scenarios](#real-world-tuning-scenarios)
- [Troubleshooting Performance](#troubleshooting-performance)

---

## Performance Tiers & SLAs

### Service Level Agreements (SLAs)

The system targets different response times based on operation complexity:

| Tier | Operation Type | SLA Target | Notes |
|------|----------------|-----------|-------|
| **Tier 1** | Health checks, status | <100ms | Immediate response, minimal I/O |
| **Tier 2** | Cached operations, voice | <500ms | Memory lookup, simple processing |
| **Tier 3** | AI generation, search | <2s | Model inference, vector search |
| **Tier 4** | Complex ops, indexing | <10s | Multiple steps, I/O intensive |
| **Tier 5** | Batch ops, reindexing | <60s | Full vault operations |

### Availability Targets

| Environment | Uptime | SLA % | Downtime/Year |
|------------|--------|-------|----------------|
| Development | 95% | 95% | ~18 days |
| Production | 99% | 99% | ~87 hours |
| Enterprise | 99.9% | 99.9% | ~8.7 hours |

### Sample Response Times (Production)

```
Health Check (/health):           45ms ✅
Cached Search (hit):              250ms ✅
New Search (miss):                1.8s ✅
AI Question (cached model):       800ms ✅
Voice Transcription:              400ms ✅
Vault Reindex (10K docs):         25s ✅
PDF Indexing (100 pages):         8s ✅
```

---

## Caching Strategies

### Cache Architecture (L1-L4 Hierarchy)

The system implements 4 levels of caching for maximum performance:

```
┌─────────────────────────────────────────────────┐
│         User Request / API Call                 │
└────────────────┬────────────────────────────────┘
                 │
       ┌─────────▼─────────┐
       │   L1: Memory Cache│  ← Fastest (μs)
       │  (Current process)│  ← 100-500MB size
       │   TTL: 5 min      │
       └────────┬──────────┘
                 │ (miss)
       ┌─────────▼─────────┐
       │   L2: Local Disk  │  ← Fast (ms)
       │  (SQLite/LevelDB) │  ← 1-10GB size
       │   TTL: 1 hour     │
       └────────┬──────────┘
                 │ (miss)
       ┌─────────▼─────────┐
       │  L3: Redis Cluster│  ← Medium (10ms)
       │ (Multi-instance)  │  ← 10-100GB size
       │   TTL: 24 hours   │
       └────────┬──────────┘
                 │ (miss)
       ┌─────────▼─────────┐
       │  L4: Source/DB    │  ← Slowest (100ms+)
       │ (Vector DB/Files) │  ← Unlimited size
       │  No TTL (fresh)   │
       └───────────────────┘
```

### Caching Configuration

#### L1: In-Memory Cache

**Best for**: Single-instance deployments, high concurrency

```yaml
cache:
    backend: memory
    max_size_mb: 500
    ttl_seconds: 300
    eviction_policy: lru  # Least Recently Used
```

**When to use**:
- Development environments
- Single-server deployments
- <50 concurrent users
- Dedicated machine (not shared)

**Pros**: Ultra-fast (<1ms access time), no network overhead  
**Cons**: Lost on restart, not shared across instances

#### L2: Disk Cache

**Best for**: Persistent caching, single-server production

```yaml
cache:
    backend: disk
    cache_dir: ./agent/cache
    max_size_gb: 10
    ttl_seconds: 3600
    eviction_policy: lru
```

**When to use**:
- Single-server production
- Medium query load (<100 QPS)
- Persistent cache needed
- Limited RAM

**Pros**: Persistent between restarts, larger size than memory  
**Cons**: Slower than memory (1-10ms), single-machine only

#### L3: Redis Cluster

**Best for**: Multi-instance deployments, enterprise scale

```yaml
cache:
    backend: redis
    redis_url: "redis://redis-cluster:6379"
    redis_cluster: true
    max_connections: 100
    ttl_seconds: 86400
    eviction_policy: allkeys-lru
```

**When to use**:
- Multi-server deployments
- Load balancing across nodes
- High concurrency (>100 users)
- Enterprise environments

**Pros**: Shared across all instances, fast (5-15ms), persistent  
**Cons**: Additional infrastructure, network overhead

#### Redis Cluster Setup

```bash
# Quick setup with Docker
docker run -d --name redis-cache \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --maxmemory 50gb \
               --maxmemory-policy allkeys-lru

# For cluster (3+ nodes)
docker run -d --name redis-node-1 \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --cluster-enabled yes \
               --cluster-node-timeout 5000 \
               --appendonly yes
```

### Cache Warming Strategy

Pre-populate cache with frequent queries:

```python
import asyncio
from agent.cache import CacheManager

async def warm_cache():
    cache = CacheManager.from_settings()
    
    # Pre-load frequently accessed documents
    popular_queries = [
        "API authentication",
        "getting started",
        "installation guide"
    ]
    
    for query in popular_queries:
        # Trigger embeddings and search
        embeddings = await embeddings_manager.embed_text(query)
        results = await vector_db.search(embeddings, top_k=5)
        
        # Cache the results
        await cache.set(
            f"search:{query}",
            results,
            ttl=86400
        )
    
    print("Cache warmed successfully")

# Run during backend startup
asyncio.run(warm_cache())
```

### Cache Invalidation Patterns

**Pattern 1: TTL-Based** (Automatic expiration)
```yaml
cache:
    default_ttl: 3600  # 1 hour
    
    # Per-operation TTLs
    ttls:
        search_results: 1800      # 30 min
        model_inference: 300      # 5 min
        document_index: 86400     # 24 hours
```

**Pattern 2: Event-Based** (Invalidate on update)
```python
async def update_document(doc_id, content):
    # Update source
    await db.update_document(doc_id, content)
    
    # Invalidate related cache entries
    await cache.invalidate(f"doc:{doc_id}")
    await cache.invalidate(f"search:*")  # Wildcard invalidation
    
    # Re-index for vector search
    await embeddings_manager.reindex_document(doc_id)
```

**Pattern 3: Manual Cache Clear**
```bash
# Clear all cache
curl -X POST http://localhost:8000/api/cache/clear \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Clear specific pattern
curl -X POST http://localhost:8000/api/cache/clear \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"pattern": "search:*"}'
```

---

## Model Selection & Tuning

### Model Performance Characteristics

| Model | Speed | Accuracy | Memory | GPU | Use Case |
|-------|-------|----------|--------|-----|----------|
| **GPT4All-J** | ⚡⚡ Fast | ✅ Good | 4GB | Optional | Default, all-purpose |
| **Llama 2-7B** | ⚡⚡ Fast | ✅✅ Better | 8GB | Recommended | Accuracy over speed |
| **Llama 2-13B** | ⚡ Medium | ✅✅✅ Excellent | 16GB | Required | Best accuracy |
| **Mistral-7B** | ⚡⚡⚡ Fastest | ✅ Good | 4GB | Optional | Speed priority |
| **Orca 2-7B** | ⚡⚡ Fast | ✅✅ Better | 8GB | Optional | Reasoning tasks |

### Model Selection Strategy

**Decision Tree**:

```
START
  │
  ├─ Speed Critical? (< 500ms needed)
  │  └─ YES → Mistral-7B (50ms inference)
  │  └─ NO → Continue
  │
  ├─ Accuracy Critical? (complex questions)
  │  └─ YES → Llama 2-13B (best quality)
  │  └─ NO → Continue
  │
  ├─ Limited Resources? (< 8GB RAM)
  │  └─ YES → GPT4All-J (4GB, balanced)
  │  └─ NO → Continue
  │
  └─ Default → GPT4All-J (best balance)
```

### Configuration for Different Scenarios

**Scenario 1: Single User (Desktop)**
```yaml
model_backend: gpt4all
model_name: ggml-gpt4all-j
gpu: false
model_max_batch_size: 1
embeddings_batch_size: 1
```

**Scenario 2: Team Server (5-10 users)**
```yaml
model_backend: gpt4all
model_name: ggml-gpt4all-j
gpu: true  # Strongly recommended
model_max_batch_size: 8
embeddings_batch_size: 32
```

**Scenario 3: Enterprise (100+ users)**
```yaml
model_backend: llama_cpp
model_name: llama-2-13b.gguf
gpu: true
model_max_batch_size: 32
embeddings_batch_size: 256
num_workers: 4
```

### Model Pool Configuration

Multiple model instances for concurrent requests:

```yaml
performance:
    model_pool_size: 2        # 2-3 instances
    embeddings_pool_size: 3
    db_connection_pool: 10
```

**Resource Allocation** (per instance):
- Model pool size 2: 16 CPU threads, 16GB RAM
- Model pool size 3: 32 CPU threads, 32GB RAM
- Embeddings pool size 3: 8 CPU threads, 8GB RAM

### Quantization Levels

Reduce model size for faster inference:

| Quantization | Size | Speed | Accuracy Loss |
|-------------|------|-------|----------------|
| F32 (none) | 100% | Baseline | 0% |
| F16 | 50% | 1.5x | <1% |
| Q8 | 25% | 2x | <2% |
| Q6 | 18% | 2.5x | 1-2% |
| Q5 | 16% | 3x | 2-3% |
| Q4 | 12% | 4x | 3-5% |

**Configuration**:
```yaml
model:
    quantization: Q5  # Good balance
    # or: Q6 (higher accuracy)
    # or: Q4 (faster, lower accuracy)
```

---

## System Optimization

### Hardware Configuration

#### CPU Optimization

**Number of Workers**:
```bash
# Calculate optimal workers
# Formula: (CPU_cores - 2) for CPU-bound tasks
# Example: 16 cores → 14 workers

export WORKERS=14
```

Configuration:
```yaml
workers: 14
worker_timeout: 120
```

**CPU Affinity** (Linux/macOS):
```bash
# Pin workers to specific CPU cores for cache locality
# Configure in environment setup script
export CPUAFFINITY=true
```

#### Memory Optimization

**Base Memory Requirements**:
```
Backend process:           100MB (base)
Model instance:            4-16GB (depends on model)
Vector DB (ChromaDB):      500MB + data size
Cache (L1/L2):             500MB-5GB
OS overhead:               1-2GB

Total: 6-26GB (single instance)
```

**Memory Tuning**:
```yaml
memory:
    max_model_size: 13000  # MB (13GB)
    model_mmap: true       # Use memory-mapping
    gc_interval: 300       # Run GC every 5 min
    gc_threshold: 700      # Threshold in MB
```

#### GPU Acceleration

**GPU Configuration**:
```yaml
gpu: true
gpu_memory_fraction: 0.8   # Use 80% of GPU VRAM
cuda_device: 0              # GPU device ID
```

**Expected Performance Gains**:
- Embeddings: 3-5x faster
- Model inference: 2-4x faster
- Overall throughput: 2-3x improvement

**Multi-GPU Setup**:
```yaml
gpu: true
cuda_devices: [0, 1, 2, 3]  # Use GPUs 0-3
model_pool_per_gpu: 1
```

### Network Optimization

**Connection Pooling**:
```yaml
performance:
    db_connection_pool: 20
    redis_connection_pool: 50
    http_connection_pool: 100
```

**Compression**:
```yaml
api:
    compression: true
    compression_level: 6  # 1-9 (9=best)
```

### Disk I/O Optimization

**Vector DB Configuration**:
```yaml
vector_db:
    # Use NVMe SSD for best performance
    storage_path: /mnt/nvme0/vector_db
    
    # HNSW index tuning
    hnsw_m: 16          # Connectivity degree
    hnsw_ef: 200        # Search parameter
    batch_size: 1000    # Indexing batch
```

**Chunk Size Tuning**:
```yaml
vector_db:
    chunk_size: 1000        # Size of text chunks
    chunk_overlap: 200      # Overlap between chunks
    # Smaller chunks: More accurate, slower search
    # Larger chunks: Faster search, less accurate
```

---

## Monitoring & Metrics

### Real-Time Metrics Endpoint

```bash
curl http://localhost:8000/api/performance/metrics | jq

# Response:
{
    "timestamp": 1697904000,
    "cache": {
        "l1_hits": 1250,
        "l1_misses": 50,
        "l1_hit_rate": 0.96,
        "l2_hits": 40,
        "l2_misses": 10,
        "l2_hit_rate": 0.80,
        "size_mb": 250
    },
    "model": {
        "active_instances": 2,
        "busy_instances": 1,
        "queue_length": 3,
        "avg_inference_time_ms": 150
    },
    "embeddings": {
        "active_instances": 2,
        "busy_instances": 0,
        "queue_length": 0,
        "avg_embedding_time_ms": 45
    },
    "db": {
        "connections": 15,
        "connection_pool_size": 20,
        "queries_per_second": 12.5
    },
    "system": {
        "cpu_percent": 45,
        "memory_percent": 62,
        "disk_percent": 35
    }
}
```

### Health Check with Details

```bash
curl http://localhost:8000/api/health/detailed

# Response includes:
# - Service status (HEALTHY/DEGRADED/UNHEALTHY)
# - Component health (model manager, embeddings, cache)
# - System metrics (CPU, memory, disk)
# - Alert summary
```

### Key Performance Indicators (KPIs)

Track these metrics for optimal performance:

| KPI | Target | Warning | Critical |
|-----|--------|---------|----------|
| Cache Hit Rate | >80% | <75% | <60% |
| API Response Time (p95) | <1s | <2s | >3s |
| Model Queue Length | <2 | <5 | >10 |
| CPU Utilization | 60-75% | >80% | >90% |
| Memory Usage | 60-70% | >80% | >90% |
| Disk I/O Wait | <5% | <10% | >15% |

### Prometheus Metrics Export

For integration with monitoring systems:

```yaml
metrics:
    enabled: true
    export_format: prometheus
    endpoint: /metrics
```

```bash
# Scrape metrics in Prometheus format
curl http://localhost:8000/metrics

# Output:
# TYPE cache_hits_total counter
cache_hits_total{cache_level="l1"} 1250
cache_hits_total{cache_level="l2"} 40
# ...
```

---

## Real-World Tuning Scenarios

### Scenario 1: Slow Search (>2 seconds)

**Diagnosis**:
```bash
# Check cache hit rate
curl http://localhost:8000/api/performance/metrics | jq '.cache.l1_hit_rate'

# Check model queue
curl http://localhost:8000/api/performance/metrics | jq '.model.queue_length'

# Check vector DB stats
curl http://localhost:8000/api/vector_db/stats
```

**Solution**:
```yaml
# Option 1: Increase cache TTL
cache:
    ttl_seconds: 7200  # 2 hours instead of 1

# Option 2: Reduce chunk size for faster search
vector_db:
    chunk_size: 500    # 500 instead of 1000
    top_k: 3           # Get fewer results

# Option 3: Enable GPU
gpu: true

# Option 4: Add model instances
performance:
    model_pool_size: 3  # Add pool instances
```

### Scenario 2: High CPU Usage (>90%)

**Diagnosis**:
```bash
# Check worker saturation
curl http://localhost:8000/api/health | jq '.system.cpu_percent'

# Check queue lengths
curl http://localhost:8000/api/performance/metrics | jq '.model, .embeddings'
```

**Solution**:
```yaml
# Option 1: Increase workers
workers: 16  # More workers for more cores

# Option 2: Add GPU acceleration
gpu: true

# Option 3: Reduce batch sizes
model_max_batch_size: 16  # Smaller batches

# Option 4: Add more instances (horizontal scale)
# Deploy additional backend instances
```

### Scenario 3: Memory Pressure (>85%)

**Diagnosis**:
```bash
curl http://localhost:8000/api/health | jq '.system.memory_percent'
curl http://localhost:8000/api/performance/metrics | jq '.cache.size_mb'
```

**Solution**:
```yaml
# Option 1: Reduce cache size
cache:
    backend: disk      # Switch to disk
    max_size_mb: 200   # Reduce memory cache

# Option 2: Use model quantization
model:
    quantization: Q5   # Reduce model size

# Option 3: Reduce model pool
performance:
    model_pool_size: 1  # Single instance

# Option 4: Increase chunk size
vector_db:
    chunk_size: 2000   # Larger chunks
```

### Scenario 4: High Latency with Low CPU (Network Bottleneck)

**Diagnosis**:
```bash
# Check if disk I/O is bottleneck
curl http://localhost:8000/api/performance/metrics | jq '.system'

# Check network stats
netstat -s | grep -E "TCP|UDP"
```

**Solution**:
```yaml
# Option 1: Enable response compression
api:
    compression: true
    compression_level: 6

# Option 2: Optimize connection pools
performance:
    http_connection_pool: 200
    redis_connection_pool: 100

# Option 3: Use disk cache instead of Redis
cache:
    backend: disk      # Local faster than network

# Option 4: Move vector DB to NVMe
vector_db:
    storage_path: /mnt/nvme0/vector_db
```

### Scenario 5: Inconsistent Performance

**Diagnosis**:
```bash
# Monitor over time
watch -n 5 'curl -s http://localhost:8000/api/performance/metrics | jq .'

# Check for garbage collection pauses
curl http://localhost:8000/api/health/detailed
```

**Solution**:
```yaml
# Option 1: Tune garbage collection
memory:
    gc_interval: 60      # More frequent GC
    gc_threshold: 500    # Lower threshold

# Option 2: Pre-warm cache
# Run cache warming script on startup

# Option 3: Enable request prioritization
api:
    priority_queue: true
    high_priority_timeout: 500
    default_priority_timeout: 2000

# Option 4: Distribute load
# Use load balancer with multiple instances
```

---

## Optimization Checklist

### Development Environment
- [ ] Enable caching (memory backend)
- [ ] Set chunk_size to 1000
- [ ] Use default model (GPT4All-J)
- [ ] Single worker process
- [ ] Monitor with `/api/health`

### Staging Environment
- [ ] Disk-based cache with 1-hour TTL
- [ ] Redis setup for multi-instance
- [ ] GPU acceleration enabled
- [ ] Model pool size: 2
- [ ] Implement comprehensive monitoring

### Production Environment
- [ ] Redis cluster for caching
- [ ] GPU acceleration mandatory
- [ ] Model pool size: 3-4
- [ ] CPU affinity enabled
- [ ] Real-time metrics collection
- [ ] Alerts configured (CPU, memory, cache)
- [ ] Load balancing across 3+ instances
- [ ] Backup vector DB daily

### Performance Validation

```bash
#!/bin/bash
# Run performance baseline

echo "Testing Tier 1 (Health)..."
time curl http://localhost:8000/health > /dev/null

echo "Testing Tier 2 (Cached Search)..."
time curl -X POST http://localhost:8000/api/ask \
  -d '{"prompt": "test"}' > /dev/null

echo "Testing Tier 3 (AI Generation)..."
time curl -X POST http://localhost:8000/api/ask \
  -d '{"prompt": "complicated question"}' > /dev/null

echo "Performance validation complete!"
```

---

## Conclusion

Performance tuning is an iterative process:

1. **Measure**: Use `/api/performance/metrics` to identify bottlenecks
2. **Analyze**: Determine if issue is CPU, memory, disk, or network
3. **Optimize**: Apply targeted tuning from this guide
4. **Validate**: Measure again and confirm improvement
5. **Monitor**: Set up alerts to catch regressions

**Key Takeaway**: For most deployments, enabling GPU acceleration and Redis caching provides the best performance improvement with minimal effort.

---

**Version**: 1.0  
**Last Updated**: October 21, 2025  
**Status**: ✅ Production Ready
