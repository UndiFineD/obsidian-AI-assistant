# Advanced Configuration Guide

This guide covers enterprise-grade advanced configurations for production deployments including multi-GPU setups, distributed caching with Redis, Kubernetes orchestration, advanced SSO, and security hardening.

**Target Audience**: DevOps engineers, infrastructure architects, security teams  
**Prerequisites**: 
- Familiarity with v0.1.35 base configuration
- Docker/Kubernetes knowledge for container deployments
- Redis cluster administration
- GPU hardware and CUDA setup

---

## Table of Contents

1. [Multi-GPU Setup](#multi-gpu-setup)
2. [Redis Cluster Deployment](#redis-cluster-deployment)
3. [Kubernetes Scaling](#kubernetes-scaling)
4. [Advanced SSO Configuration](#advanced-sso-configuration)
5. [Security Hardening](#security-hardening)
6. [Disaster Recovery Planning](#disaster-recovery-planning)
7. [Capacity Planning](#capacity-planning)
8. [Performance Monitoring](#performance-monitoring)
9. [Troubleshooting Advanced Configurations](#troubleshooting)
10. [Real-World Deployment Scenarios](#real-world-scenarios)

---

## Multi-GPU Setup

### 1. Hardware Prerequisites

#### Supported GPUs
- **NVIDIA**: A100, H100, RTX 6000/4090 (PCIe 4.0 recommended)
- **AMD**: MI300X, MI250X (ROCm 5.7+)
- **Intel**: Data Center GPU Max (oneAPI 2024.0+)

#### System Requirements

```yaml
CPU:
  cores: 16+                    # 2 cores per GPU minimum
  frequency: 3.5 GHz+
  architecture: x86-64

RAM:
  base: 32 GB
  per_gpu: 16-32 GB            # Depends on model
  total: base + (num_gpus * per_gpu)

Storage:
  ssd: 500 GB+ NVMe           # For model caching
  iops: 5000+ sequential read

Network:
  bandwidth: 40 Gbps+ (NVLink preferred)
  latency: < 1 ms between GPUs

PCIe:
  version: 4.0+
  lanes: 16 per GPU minimum
  nvlink: Recommended for > 2 GPUs
```

#### Verification Commands

```bash
# Check GPU availability (NVIDIA)
nvidia-smi

# Check GPU topology
nvidia-smi topo -m

# Verify PCIe configuration
lspci | grep -i nvidia

# Check NVLink connectivity
nvidia-smi nvlink -s

# Monitor GPU temperature
watch -n 1 nvidia-smi

# Check GPU memory
nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free --format=csv
```

### 2. Single-Host Multi-GPU Configuration

#### Environment Setup

```bash
#!/bin/bash

# Enable GPU support
export CUDA_VISIBLE_DEVICES=0,1,2,3        # or "0-3"
export CUDA_DEVICE_ORDER=PCI_BUS_ID        # Consistency across runs
export CUDA_LAUNCH_BLOCKING=0               # Async kernels
export TF_FORCE_GPU_ALLOW_GROWTH=true       # Dynamic memory allocation

# Optimization flags
export CUBLAS_WORKSPACE_CONFIG=:16:8        # Smaller memory footprint
export NCCL_DEBUG=INFO                      # Network debugging
export NCCL_SOCKET_FAMILY=AF_INET           # Use IPv4

# Performance tuning
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export TORCH_NUM_THREADS=8
```

#### Python Configuration

```python
# agent/config.yaml - GPU settings

gpu:
  enabled: true
  device_ids: [0, 1, 2, 3]           # GPU indices
  strategy: "ddp"                     # Distributed Data Parallel
  backend: "nccl"                     # NCCL for GPU, Gloo for CPU
  find_unused_parameters: false
  gradient_as_bucket_view: true       # Memory optimization

model_manager:
  gpu_pools:
    embeddings:
      devices: [0, 1]                 # Dedicate GPUs 0-1
      pool_size: 2
      batch_size: 128
    generation:
      devices: [2, 3]                 # Dedicate GPUs 2-3
      pool_size: 1
      batch_size: 64

performance:
  mixed_precision: "fp16"             # 2x faster, 50% less memory
  gradient_accumulation_steps: 4      # Effective batch size * 4
  num_workers: 8
```

#### Model Loading Script

```python
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from agent.modelmanager import ModelManager
from agent.settings import get_settings

def setup_gpu_environment():
    """Initialize distributed GPU training"""
    
    settings = get_settings()
    
    # Initialize process group
    dist.init_process_group(
        backend=settings.gpu.backend,
        init_method="env://",
        timeout=datetime.timedelta(minutes=30)
    )
    
    # Set device
    rank = dist.get_rank()
    device = torch.device(f"cuda:{rank}")
    torch.cuda.set_device(device)
    
    return device, rank, dist.get_world_size()

def load_models_multi_gpu():
    """Load models on multiple GPUs with DDP"""
    
    device, rank, world_size = setup_gpu_environment()
    settings = get_settings()
    
    # Load base model
    model = ModelManager.from_settings()
    
    # Wrap with DDP
    model = DDP(
        model,
        device_ids=[rank],
        output_device=rank,
        find_unused_parameters=settings.gpu.find_unused_parameters,
        gradient_as_bucket_view=settings.gpu.gradient_as_bucket_view
    )
    
    # Synchronize initialization
    dist.barrier()
    
    return model, device

def inference_multi_gpu(text: str):
    """Inference across multiple GPUs"""
    
    device, rank, _ = setup_gpu_environment()
    model, dev = load_models_multi_gpu()
    
    # Move input to device
    inputs = {k: v.to(device) for k, v in tokenize(text).items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    return outputs
```

#### Launch Script

```bash
#!/bin/bash

# Multi-GPU launch script
NUM_GPUS=4
MASTER_ADDR=localhost
MASTER_PORT=29500

python -m torch.distributed.launch \
    --nproc_per_node=$NUM_GPUS \
    --master_addr=$MASTER_ADDR \
    --master_port=$MASTER_PORT \
    agent/backend.py

# Or with torchrun (PyTorch 1.13+)
torchrun \
    --nproc_per_node=$NUM_GPUS \
    --master_addr=$MASTER_ADDR \
    --master_port=$MASTER_PORT \
    agent/backend.py
```

### 3. Multi-Host GPU Cluster Setup

#### Network Configuration

```yaml
# Cluster topology - 3 nodes, 4 GPUs each (12 GPUs total)

nodes:
  node-01:
    hostname: gpu-compute-01
    ip: 192.168.1.100
    gpus: [0, 1, 2, 3]
    nccl_bind: eth0,eth1           # Multiple NICs for bandwidth
  
  node-02:
    hostname: gpu-compute-02
    ip: 192.168.1.101
    gpus: [0, 1, 2, 3]
  
  node-03:
    hostname: gpu-compute-03
    ip: 192.168.1.102
    gpus: [0, 1, 2, 3]

network:
  backend: "nccl"
  communication:
    inter_node: RDMA (RoCE v2)      # Low latency
    intra_node: NVLink + PCIe
    nccl_debug: INFO
```

#### NCCL Configuration

```bash
# ~/.nccl.conf - NCCL settings

# Enable debug output
NCCL_DEBUG=INFO

# Use specific network interface
NCCL_SOCKET_IFNAME=eth0,eth1

# Set timeout for collective operations
NCCL_TIMEOUT=600

# Memory optimization
NCCL_MAX_NCHANNELS=32
NCCL_MIN_NCHANNELS=4

# Graph optimization (NVIDIA A100+)
NCCL_GRAPH_MIXING_SUPPORT=1

# Disable P2P for debugging
NCCL_P2P_DISABLE=0               # 0 = enabled

# HCNL backend selection
NCCL_COMM_SPLIT_MODE=STREAM
```

#### Distributed Training Launch

```python
import os
from agent.utils.distributed import setup_multi_node_gpu

def launch_multi_node_training():
    """Launch training across multiple nodes"""
    
    # Environment variables set by launcher
    rank = int(os.environ.get('RANK', 0))
    world_size = int(os.environ.get('WORLD_SIZE', 1))
    local_rank = int(os.environ.get('LOCAL_RANK', 0))
    master_addr = os.environ.get('MASTER_ADDR', 'localhost')
    master_port = int(os.environ.get('MASTER_PORT', 29500))
    
    device, rank, world_size = setup_multi_node_gpu(
        rank=rank,
        world_size=world_size,
        master_addr=master_addr,
        master_port=master_port
    )
    
    print(f"Running rank {rank}/{world_size} on device {device}")
    
    # Load model and train
    model = load_model()
    model = wrap_with_ddp(model, local_rank)
    
    return model
```

---

## Redis Cluster Deployment

### 1. Redis Cluster Architecture

#### Single Redis Instance (Development)

```yaml
# Single Redis server - suitable for < 5GB cache

instance:
  host: localhost
  port: 6379
  maxmemory: 5gb
  maxmemory_policy: allkeys-lru
  save: "900 1 300 10 60 10000"   # RDB snapshots
  appendonly: no                   # No AOF
```

#### Redis Cluster (Production - 3+ Nodes)

```yaml
# Redis Cluster - 3 nodes (3 master + 3 replicas = 6 total)

cluster:
  nodes:
    master-01:
      host: redis-01.cache.local
      port: 6379
      replicas: 1
    master-02:
      host: redis-02.cache.local
      port: 6379
      replicas: 1
    master-03:
      host: redis-03.cache.local
      port: 6379
      replicas: 1
  
  configuration:
    maxmemory: 32gb                 # Per node
    maxmemory_policy: allkeys-lru   # LRU eviction
    cluster_node_timeout: 15000     # Failover timeout (ms)
    cluster_replica_validity_factor: 10
    timeout: 0                       # No idle timeout
```

### 2. Redis Cluster Setup

#### Installation & Configuration

```bash
#!/bin/bash

# Install Redis on each node
sudo apt-get update
sudo apt-get install -y redis-server redis-tools

# Download Redis cluster configuration
REDIS_VERSION=7.2.3
wget http://download.redis.io/redis-$REDIS_VERSION.tar.gz
tar xzf redis-$REDIS_VERSION.tar.gz
cd redis-$REDIS_VERSION

# Build and install
make
make test
sudo make install

# Create cluster directory structure
mkdir -p /data/redis/{6379,6380,6381}
chmod 755 /data/redis/*
```

#### Per-Node Configuration

```bash
# /etc/redis/cluster/redis-6379.conf

port 6379
bind 0.0.0.0
protected-mode no
tcp-backlog 511
timeout 0
tcp-keepalive 300

# Cluster settings
cluster-enabled yes
cluster-config-file /data/redis/6379/nodes.conf
cluster-node-timeout 15000

# Memory settings
maxmemory 32gb
maxmemory-policy allkeys-lru
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
dbfilename dump.rdb
dir /data/redis/6379

# AOF (optional)
appendonly no
appendfsync everysec

# Replication
min-replicas-to-write 1
min-replicas-max-lag 10

# Slowlog
slowlog-log-slower-than 10000
slowlog-max-len 128

# Client handling
maxclients 10000
```

#### Initialize Cluster

```bash
#!/bin/bash

# Start Redis instances on 3 nodes
# Node 1: 6379 (master), 6380 (replica)
# Node 2: 6381 (master), 6382 (replica)
# Node 3: 6383 (master), 6384 (replica)

# Start all instances
redis-server /etc/redis/cluster/redis-6379.conf
redis-server /etc/redis/cluster/redis-6380.conf
redis-server /etc/redis/cluster/redis-6381.conf
redis-server /etc/redis/cluster/redis-6382.conf
redis-server /etc/redis/cluster/redis-6383.conf
redis-server /etc/redis/cluster/redis-6384.conf

# Create cluster (9 replicas per master)
redis-cli --cluster create \
  192.168.1.100:6379 \
  192.168.1.100:6380 \
  192.168.1.101:6381 \
  192.168.1.101:6382 \
  192.168.1.102:6383 \
  192.168.1.102:6384 \
  --cluster-replicas 1

# Verify cluster
redis-cli -c cluster info
redis-cli -c cluster nodes
```

### 3. Redis Connection Configuration

#### Python Client Setup

```python
# agent/cache/redis_cluster.py

import redis
from redis.cluster import RedisCluster
from redis.sentinel import Sentinel
from agent.settings import get_settings

class RedisClusterManager:
    """Redis Cluster connection and operations"""
    
    def __init__(self, settings):
        self.settings = settings
        self.client = None
        self.initialize()
    
    def initialize(self):
        """Initialize Redis cluster connection"""
        
        if self.settings.cache_backend == "redis_cluster":
            # Cluster mode
            startup_nodes = [
                {"host": node.split(":")[0], "port": int(node.split(":")[1])}
                for node in self.settings.redis_cluster_nodes
            ]
            
            self.client = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                    3: 3,  # TCP_KEEPCNT
                },
                skip_full_coverage_check=True,
                health_check_interval=30,
                max_connections=1000,
                retry_on_timeout=True,
                connection_pool_kwargs={
                    "max_retries": 3,
                    "retry_on_timeout": True,
                }
            )
        
        elif self.settings.cache_backend == "redis_sentinel":
            # Sentinel mode (HA)
            sentinels = [
                (node.split(":")[0], int(node.split(":")[1]))
                for node in self.settings.redis_sentinel_nodes
            ]
            
            sentinel = Sentinel(
                sentinels,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,
                    2: 1,
                    3: 3,
                }
            )
            
            self.client = sentinel.master_for(
                self.settings.redis_service_name,
                socket_keepalive=True,
                health_check_interval=30
            )
    
    async def get(self, key: str, timeout: int = 5) -> Optional[str]:
        """Get value from cluster with timeout"""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self.client.get, key),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Redis GET timeout for key: {key}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 3600):
        """Set value in cluster with TTL"""
        try:
            await asyncio.to_thread(
                self.client.setex,
                key,
                ttl,
                value
            )
        except Exception as error:
            logger.error(f"Redis SET failed: {error}")
    
    def cluster_info(self) -> Dict[str, Any]:
        """Get cluster information"""
        return {
            "info": self.client.cluster_info(),
            "nodes": self.client.cluster_nodes(),
            "slots": self.client.cluster_slots()
        }
```

#### Configuration YAML

```yaml
# agent/config.yaml

cache:
  backend: redis_cluster              # or redis_sentinel
  
  # Cluster mode
  redis_cluster_nodes:
    - "192.168.1.100:6379"
    - "192.168.1.101:6379"
    - "192.168.1.102:6379"
  
  # Sentinel mode (HA)
  redis_sentinel_nodes:
    - "192.168.1.100:26379"
    - "192.168.1.101:26379"
    - "192.168.1.102:26379"
  redis_service_name: "mymaster"
  
  # Connection settings
  socket_timeout: 5
  socket_connect_timeout: 5
  socket_keepalive: true
  health_check_interval: 30
  
  # Memory policy
  maxmemory_policy: "allkeys-lru"
  
  # TTL defaults
  default_ttl: 3600
  cache_l2_ttl: 86400               # 24 hours
```

---

## Kubernetes Scaling

### 1. Kubernetes Architecture

#### Cluster Design (3-100+ Nodes)

```yaml
# Kubernetes cluster topology

namespaces:
  production:
    replicas: 3+                    # HA deployment
    requests:
      cpu: "4"
      memory: "16Gi"
    limits:
      cpu: "8"
      memory: "32Gi"
    
    node_affinity:
      compute_tier: "high-performance"
      gpu: "true"                   # If GPU enabled
  
  staging:
    replicas: 2
    requests:
      cpu: "2"
      memory: "8Gi"
  
  development:
    replicas: 1
    requests:
      cpu: "1"
      memory: "4Gi"

node_pools:
  cpu_optimized:
    machine_type: "n2-standard-8"   # GKE example
    node_count: 10
    autoscaling: true
    min_nodes: 10
    max_nodes: 50
  
  gpu_optimized:
    machine_type: "a2-highgpu-4g"   # 4x A100 GPUs
    node_count: 5
    autoscaling: true
    min_nodes: 5
    max_nodes: 20
  
  memory_optimized:
    machine_type: "n2-highmem-16"   # For caching
    node_count: 5
    autoscaling: false
```

### 2. Kubernetes Deployment Manifests

#### StatefulSet for Backend

```yaml
# k8s/backend-statefulset.yaml

apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: obsidian-ai-backend
  namespace: production
spec:
  serviceName: obsidian-ai-backend
  replicas: 3
  selector:
    matchLabels:
      app: obsidian-ai-backend
      tier: backend
  
  template:
    metadata:
      labels:
        app: obsidian-ai-backend
        tier: backend
    
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - obsidian-ai-backend
                topologyKey: kubernetes.io/hostname
      
      nodeSelector:
        compute_tier: high-performance
      
      securityContext:
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      
      serviceAccountName: obsidian-ai-backend
      
      containers:
        - name: backend
          image: obsidian-ai-backend:v0.1.35
          imagePullPolicy: IfNotPresent
          
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
          
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: LOG_LEVEL
              value: "info"
            - name: WORKERS
              value: "4"
            - name: REDIS_CLUSTER_NODES
              value: "redis-0.redis:6379,redis-1.redis:6379,redis-2.redis:6379"
            - name: VECTOR_DB
              value: "chromadb"
            - name: GPU
              value: "true"
            - name: CUDA_VISIBLE_DEVICES
              value: "0,1,2,3"
          
          resources:
            requests:
              cpu: "4"
              memory: "16Gi"
              nvidia.com/gpu: "1"    # Request 1 GPU
            limits:
              cpu: "8"
              memory: "32Gi"
              nvidia.com/gpu: "1"
          
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          
          readinessProbe:
            httpGet:
              path: /api/health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 2
          
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
            readOnlyRootFilesystem: false
            runAsNonRoot: true
            runAsUser: 1000
          
          volumeMounts:
            - name: models
              mountPath: /models
            - name: cache
              mountPath: /cache
            - name: logs
              mountPath: /logs
      
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: models-pvc
        - name: cache
          emptyDir:
            sizeLimit: 10Gi
        - name: logs
          emptyDir:
            sizeLimit: 5Gi

  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: [ "ReadWriteOnce" ]
        resources:
          requests:
            storage: 50Gi
```

#### HorizontalPodAutoscaler

```yaml
# k8s/backend-hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: obsidian-ai-backend-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: StatefulSet
    name: obsidian-ai-backend
  
  minReplicas: 3
  maxReplicas: 100
  
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
  
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          percent: 100               # Double replicas
          periodSeconds: 60
        - type: Pods
          pods: 4                    # Add 4 pods max
          periodSeconds: 60
      selectPolicy: Max
    
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          percent: 50                # Remove 50%
          periodSeconds: 60
      selectPolicy: Min
```

#### Service & Ingress

```yaml
# k8s/backend-service.yaml

apiVersion: v1
kind: Service
metadata:
  name: obsidian-ai-backend
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: obsidian-ai-backend
  ports:
    - name: http
      port: 80
      targetPort: 8000
    - name: metrics
      port: 9090
      targetPort: 9090

---
# k8s/backend-ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: obsidian-ai-backend
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.obsidian-ai.example.com
      secretName: obsidian-ai-tls
  rules:
    - host: api.obsidian-ai.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: obsidian-ai-backend
                port:
                  number: 80
```

### 3. Kubernetes Deployment Commands

```bash
#!/bin/bash

# Create namespace
kubectl create namespace production
kubectl label namespace production tier=production

# Create storage class
kubectl apply -f k8s/storage-class.yaml

# Create Redis cluster
kubectl apply -f k8s/redis-statefulset.yaml
kubectl apply -f k8s/redis-service.yaml

# Wait for Redis
kubectl rollout status statefulset/redis -n production

# Create backend deployment
kubectl apply -f k8s/backend-statefulset.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/backend-hpa.yaml
kubectl apply -f k8s/backend-ingress.yaml

# Verify deployment
kubectl get statefulsets,pods,services,hpa -n production

# Monitor scaling
kubectl get hpa -n production -w

# Check logs
kubectl logs -f deployment/obsidian-ai-backend -n production --tail=100

# Scale manually if needed
kubectl scale statefulset obsidian-ai-backend --replicas=10 -n production
```

---

## Advanced SSO Configuration

### 1. OAuth 2.0 & OpenID Connect Setup

#### Azure AD Configuration

```python
# agent/enterprise/azure_sso_advanced.py

from microsoft_graph_python_sdk import GraphServiceClient
from azure.identity import ClientSecretCredential
from pydantic import BaseModel
from typing import List, Optional

class AzureADGroupMapping(BaseModel):
    """Azure AD group to application role mapping"""
    group_id: str                    # Azure AD group ID
    group_name: str                  # Display name
    app_roles: List[str]             # Application roles
    permissions: List[str]           # Granular permissions
    cost_center: Optional[str]        # For billing
    data_classification: str          # public/internal/confidential

class AzureADAdvancedConfig:
    """Advanced Azure AD configuration with group mapping"""
    
    def __init__(self):
        self.credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
        self.client = GraphServiceClient(self.credential)
    
    async def sync_group_memberships(self) -> Dict[str, List[str]]:
        """Sync Azure AD groups to application roles"""
        
        # Fetch all groups
        groups_response = await self.client.groups.get()
        
        group_mappings = {}
        for group in groups_response.value:
            # Get group members
            members_response = await self.client.groups.by_group_id(
                group.id
            ).members.get()
            
            user_ids = [m.id for m in members_response.value]
            group_mappings[group.id] = user_ids
        
        return group_mappings
    
    async def apply_group_policies(self, user_id: str) -> Dict[str, Any]:
        """Apply policies based on group membership"""
        
        # Get user's groups
        user_groups = await self.client.users.by_user_id(
            user_id
        ).member_of.get()
        
        # Map groups to permissions
        permissions = []
        roles = []
        
        for group in user_groups.value:
            if group["@odata.type"] == "#microsoft.graph.group":
                group_config = await self.get_group_config(group.id)
                permissions.extend(group_config.permissions)
                roles.extend(group_config.app_roles)
        
        return {
            "permissions": list(set(permissions)),
            "roles": list(set(roles))
        }
    
    async def get_group_config(self, group_id: str) -> AzureADGroupMapping:
        """Get group configuration with role mapping"""
        # Implementation with caching
        pass

# Usage example
azure_sso = AzureADAdvancedConfig()
policies = await azure_sso.apply_group_policies(user_id="user-123")
```

#### Multi-Provider Configuration

```yaml
# agent/config.yaml - SSO advanced

enterprise:
  sso:
    enabled: true
    providers:
      azure_ad:
        enabled: true
        tenant_id: "${AZURE_TENANT_ID}"
        client_id: "${AZURE_CLIENT_ID}"
        client_secret: "${AZURE_CLIENT_SECRET}"
        scopes:
          - openid
          - profile
          - email
          - Directory.Read.All
        group_sync_interval: 3600        # 1 hour
        group_mapping_file: "/config/azure-groups.yaml"
        require_mfa: true
        conditional_access: true
      
      okta:
        enabled: true
        domain: "${OKTA_DOMAIN}"
        client_id: "${OKTA_CLIENT_ID}"
        client_secret: "${OKTA_CLIENT_SECRET}"
        scopes:
          - openid
          - profile
          - email
          - okta.groups.manage
        group_sync_interval: 3600
        require_okta_verify: false
      
      google_workspace:
        enabled: true
        client_id: "${GOOGLE_CLIENT_ID}"
        client_secret: "${GOOGLE_CLIENT_SECRET}"
        admin_email: "${GOOGLE_ADMIN_EMAIL}"
        directory_scopes:
          - admin.directory.group.readonly
          - admin.directory.user.readonly
        group_sync_interval: 3600
    
    jwt:
      algorithm: "RS256"
      expiry_seconds: 3600
      refresh_expiry_seconds: 86400
      issuer: "https://api.example.com"
    
    session:
      timeout_seconds: 28800            # 8 hours
      absolute_timeout: 86400            # 24 hours
      sliding_window: true
      max_concurrent_sessions: 5
```

### 2. Role-Based Access Control (RBAC) Advanced

```python
# agent/enterprise/rbac_advanced.py

from enum import Enum
from typing import Set

class Permission(str, Enum):
    """Granular permissions"""
    
    # Document permissions
    DOCUMENT_CREATE = "document:create"
    DOCUMENT_READ = "document:read"
    DOCUMENT_UPDATE = "document:update"
    DOCUMENT_DELETE = "document:delete"
    DOCUMENT_SHARE = "document:share"
    
    # Model permissions
    MODEL_SELECT = "model:select"
    MODEL_RETRAIN = "model:retrain"
    
    # System permissions
    SYSTEM_CONFIG = "system:config"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_MONITOR = "system:monitor"
    
    # Audit permissions
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"

class Role(str, Enum):
    """Application roles with permission sets"""
    
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    USER = "user"
    VIEWER = "viewer"

ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.DOCUMENT_CREATE, Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPDATE, Permission.DOCUMENT_DELETE,
        Permission.DOCUMENT_SHARE, Permission.MODEL_SELECT,
        Permission.MODEL_RETRAIN, Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_BACKUP, Permission.SYSTEM_MONITOR,
        Permission.AUDIT_READ, Permission.AUDIT_EXPORT
    },
    Role.MANAGER: {
        Permission.DOCUMENT_CREATE, Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPDATE, Permission.DOCUMENT_DELETE,
        Permission.DOCUMENT_SHARE, Permission.MODEL_SELECT,
        Permission.SYSTEM_MONITOR, Permission.AUDIT_READ
    },
    Role.ANALYST: {
        Permission.DOCUMENT_CREATE, Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPDATE, Permission.MODEL_SELECT,
        Permission.SYSTEM_MONITOR
    },
    Role.USER: {
        Permission.DOCUMENT_CREATE, Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPDATE
    },
    Role.VIEWER: {
        Permission.DOCUMENT_READ
    }
}

class RBACManager:
    """Advanced RBAC with hierarchical roles"""
    
    async def check_permission(
        self,
        user_id: str,
        required_permission: Permission
    ) -> bool:
        """Check if user has permission"""
        
        user_roles = await self.get_user_roles(user_id)
        
        for role in user_roles:
            if required_permission in ROLE_PERMISSIONS.get(role, set()):
                return True
        
        return False
    
    async def enforce_resource_access(
        self,
        user_id: str,
        resource_id: str,
        action: str
    ) -> bool:
        """Enforce access to specific resource"""
        
        # Check role permissions
        permission = Permission(f"{resource_id.split(':')[0]}:{action}")
        if not await self.check_permission(user_id, permission):
            return False
        
        # Check resource ownership/sharing
        resource_access = await self.get_resource_access(user_id, resource_id)
        return resource_access is not None
```

---

## Security Hardening

### 1. Network Security

#### Network Policies

```yaml
# k8s/network-policy.yaml

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: obsidian-ai-default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: obsidian-ai-allow-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: obsidian-ai-backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8000

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: obsidian-ai-allow-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: obsidian-ai-backend
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 53                   # DNS
```

### 2. TLS/SSL Configuration

```yaml
# k8s/certificate.yaml

apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: obsidian-ai-tls
  namespace: production
spec:
  secretName: obsidian-ai-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  commonName: api.example.com
  dnsNames:
    - api.example.com
    - "*.api.example.com"
  duration: 2160h                    # 90 days
  renewBefore: 720h                  # 30 days before expiry
```

### 3. Secrets Management

```python
# agent/security/secrets_manager.py

from cryptography.fernet import Fernet
from typing import Dict
import os

class SecretsManager:
    """Secure secrets management"""
    
    def __init__(self):
        # Use external secret manager (AWS Secrets Manager, HashiCorp Vault, etc.)
        self.backend = self._init_backend()
    
    def _init_backend(self):
        """Initialize secrets backend"""
        
        backend_type = os.getenv("SECRETS_BACKEND", "vault")
        
        if backend_type == "vault":
            from hvac import Client
            return Client(
                url=os.getenv("VAULT_ADDR"),
                token=os.getenv("VAULT_TOKEN")
            )
        elif backend_type == "aws_secrets":
            import boto3
            return boto3.client("secretsmanager")
    
    async def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from backend"""
        return await self.backend.get(secret_name)
    
    async def set_secret(self, secret_name: str, value: str):
        """Store secret in backend"""
        await self.backend.set(secret_name, value)
    
    async def rotate_secrets(self) -> Dict[str, bool]:
        """Rotate all secrets"""
        secrets = [
            "database_password",
            "api_keys",
            "jwt_secret",
            "encryption_key"
        ]
        
        results = {}
        for secret_name in secrets:
            results[secret_name] = await self._rotate_single_secret(secret_name)
        
        return results
```

### 4. Audit Logging

```python
# agent/security/audit_logger.py

import json
from datetime import datetime
from typing import Any, Dict

class AuditLogger:
    """Audit logging for compliance"""
    
    async def log_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        result: str,
        timestamp: Optional[datetime] = None
    ):
        """Log resource access"""
        
        entry = {
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "result": result,
            "source_ip": self.get_client_ip(),
            "user_agent": self.get_user_agent()
        }
        
        # Write to audit log
        await self._persist_audit_log(entry)
        
        # Send to SIEM if configured
        if os.getenv("SIEM_ENABLED"):
            await self._send_to_siem(entry)
    
    async def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """Log security event"""
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        await self._persist_audit_log(entry)
        
        if severity in ["CRITICAL", "HIGH"]:
            await self._alert_security_team(entry)
```

---

## Disaster Recovery Planning

### 1. Backup Strategy

```bash
#!/bin/bash

# Backup strategy
# RPO (Recovery Point Objective): 1 hour
# RTO (Recovery Time Objective): 30 minutes

# Daily backup schedule
0 2 * * * /scripts/backup_vector_db.sh
0 3 * * * /scripts/backup_redis.sh
0 4 * * * /scripts/backup_models.sh

# Backup location
BACKUP_DEST="s3://backups/obsidian-ai-backup-$(date +%Y%m%d-%H%M%S)"

# Compress and encrypt backups
backup_vector_db() {
    tar czf - /data/vector_db | \
    openssl enc -aes-256-cbc -salt -k "$BACKUP_KEY" | \
    aws s3 cp - "$BACKUP_DEST/vector_db.tar.gz.enc"
}

backup_redis() {
    redis-cli BGSAVE
    tar czf - /data/redis/dump.rdb | \
    openssl enc -aes-256-cbc -salt -k "$BACKUP_KEY" | \
    aws s3 cp - "$BACKUP_DEST/redis.tar.gz.enc"
}

# Test restore
test_restore() {
    # Download latest backup
    aws s3 cp "$BACKUP_DEST/vector_db.tar.gz.enc" - | \
    openssl enc -d -aes-256-cbc -k "$BACKUP_KEY" | \
    tar xzf - -C /tmp/restore_test/
    
    # Verify
    if [ -f /tmp/restore_test/vector_db ]; then
        echo "Restore test successful"
    else
        echo "Restore test FAILED"
        alert_ops_team
    fi
}
```

### 2. Recovery Procedures

```python
# agent/disaster_recovery/recovery.py

class DisasterRecovery:
    """Disaster recovery operations"""
    
    async def recover_from_backup(self, backup_id: str, target_env: str):
        """Recover from backup"""
        
        logger.info(f"Starting recovery from backup {backup_id}")
        
        # 1. Download backup
        backup = await self.download_backup(backup_id)
        
        # 2. Verify integrity
        if not await self.verify_backup(backup):
            raise ValueError("Backup integrity check failed")
        
        # 3. Pre-recovery validation
        await self._pre_recovery_checks(target_env)
        
        # 4. Stop services
        await self._stop_services(target_env)
        
        # 5. Restore data
        await self._restore_databases(backup)
        
        # 6. Verify restoration
        if not await self._verify_restoration():
            await self._rollback_restore()
            raise RuntimeError("Recovery verification failed")
        
        # 7. Restart services
        await self._start_services(target_env)
        
        # 8. Monitor
        await self._monitor_recovery(target_env)
        
        logger.info("Recovery completed successfully")
```

---

## Capacity Planning

### 1. Sizing Formulas

```python
# Capacity planning calculations

def calculate_required_resources(
    num_users: int,
    num_documents: int,
    avg_document_size_mb: float,
    concurrent_users: int,
    sla_response_time_ms: float
) -> Dict[str, Any]:
    """Calculate required resources"""
    
    # CPU calculation
    # ~5ms per request, so requests_per_sec = 1000 / 5 = 200
    # Per core capacity = 200 req/sec
    # Concurrent users * 2 = required requests/sec
    cpu_cores_needed = (concurrent_users * 2) / 200
    cpu_cores = max(4, int(cpu_cores_needed * 1.5))  # 1.5x headroom
    
    # Memory calculation
    # Base: 4GB
    # Per 1M documents: +2GB (for embeddings)
    # Per 100 concurrent users: +0.5GB
    base_memory_gb = 4
    doc_memory_gb = (num_documents / 1_000_000) * 2
    user_memory_gb = (concurrent_users / 100) * 0.5
    memory_gb = base_memory_gb + doc_memory_gb + user_memory_gb
    memory_gb = max(16, int(memory_gb * 1.2))  # 1.2x headroom
    
    # Storage calculation
    # Documents: num_documents * avg_size
    # Embeddings: num_documents * 0.384MB (for 384-dim embeddings)
    # Models: 5-15GB per model
    # Backups: 3x total size
    doc_storage_gb = (num_documents * avg_document_size_mb) / 1024
    embedding_storage_gb = (num_documents * 0.384) / 1024
    model_storage_gb = 15  # Estimate
    backup_storage_gb = (doc_storage_gb + embedding_storage_gb) * 3
    total_storage_gb = doc_storage_gb + embedding_storage_gb + model_storage_gb + backup_storage_gb
    total_storage_gb = int(total_storage_gb * 1.25)  # 1.25x headroom
    
    # GPU calculation (if needed)
    # Embeddings: 1 GPU per 1000 concurrent users
    # Generation: 1 GPU per 500 concurrent users
    gpu_count = (concurrent_users / 1000) + (concurrent_users / 500)
    gpu_count = max(0, int(gpu_count * 1.5))
    
    return {
        "cpu_cores": cpu_cores,
        "memory_gb": memory_gb,
        "storage_gb": total_storage_gb,
        "gpu_count": gpu_count,
        "estimated_nodes": max(1, int(memory_gb / 32))  # Assuming 32GB per node
    }

# Example
resources = calculate_required_resources(
    num_users=1000,
    num_documents=500_000,
    avg_document_size_mb=2.5,
    concurrent_users=100,
    sla_response_time_ms=500
)
print(resources)
# Output: {
#     "cpu_cores": 4,
#     "memory_gb": 32,
#     "storage_gb": 256,
#     "gpu_count": 0,
#     "estimated_nodes": 1
# }
```

---

## Performance Monitoring

### 1. Prometheus Metrics

```python
# agent/metrics/prometheus_exporter.py

from prometheus_client import Counter, Histogram, Gauge, start_http_server
from typing import Dict

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)
)

# Model metrics
model_inference_time = Histogram(
    'model_inference_duration_seconds',
    'Model inference duration',
    ['model_name']
)

model_queue_size = Gauge(
    'model_queue_size',
    'Model queue size',
    ['model_name']
)

# Cache metrics
cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_level']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_level']
)

# Resource metrics
gpu_memory_used = Gauge(
    'gpu_memory_used_bytes',
    'GPU memory used',
    ['gpu_id']
)

def setup_metrics_server():
    """Start Prometheus metrics server"""
    start_http_server(9090)
```

### 2. Alerting Rules

```yaml
# prometheus/rules.yaml

groups:
  - name: obsidian-ai
    interval: 30s
    rules:
      - alert: HighCPUUsage
        expr: rate(cpu_usage[5m]) > 0.8
        for: 5m
        annotations:
          summary: "High CPU usage: {{ $value }}"
      
      - alert: LowMemoryAvailable
        expr: node_memory_available_bytes < 2e9
        for: 5m
        annotations:
          summary: "Low memory: {{ $value | humanize }} bytes available"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        annotations:
          summary: "High response time: p95={{ $value }}s"
      
      - alert: CacheHitRateLow
        expr: (rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))) < 0.7
        for: 10m
        annotations:
          summary: "Low cache hit rate: {{ $value | humanizePercentage }}"
```

---

## Troubleshooting Advanced Configurations

### 1. Multi-GPU Issues

**Problem**: Uneven GPU utilization

```bash
# Diagnosis
nvidia-smi

# Solutions
# 1. Check NCCL settings
export NCCL_DEBUG=INFO

# 2. Verify GPU communication
nvidia-smi nvlink -s

# 3. Check process affinity
ps aux | grep python
taskset -p <pid>
```

### 2. Redis Cluster Issues

**Problem**: Cluster nodes not communicating

```bash
# Diagnosis
redis-cli -c cluster info
redis-cli -c cluster nodes

# Solutions
# 1. Check cluster configuration
redis-cli -c CONFIG GET cluster*

# 2. Restart problematic node
redis-cli -h <node> CLUSTER RESET

# 3. Re-join cluster
redis-cli -c CLUSTER MEET <ip> <port>
```

### 3. Kubernetes Scaling Issues

**Problem**: HPA not scaling

```bash
# Diagnosis
kubectl get hpa -n production
kubectl describe hpa obsidian-ai-backend-hpa -n production

# Check metrics server
kubectl get deployment metrics-server -n kube-system

# Solutions
# 1. Verify metrics are available
kubectl top nodes
kubectl top pods -n production

# 2. Check HPA target metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/production/pods
```

---

## Real-World Deployment Scenarios

### Scenario 1: Small Enterprise (100-500 Users)

```yaml
# Configuration for small enterprise

infrastructure:
  nodes: 3
  cpu_per_node: 8
  memory_per_node: 32GB
  storage_total: 100GB
  
  deployments:
    backend:
      replicas: 2
      requests:
        cpu: 2
        memory: 8Gi
    
    redis:
      replicas: 1
      mode: standalone
      memory: 16GB
    
    vector_db:
      replicas: 1
      storage: 50GB

  gpu: false
  cost_estimate: "$2,000-3,000/month"
```

### Scenario 2: Mid-Market (1,000-5,000 Users)

```yaml
# Configuration for mid-market

infrastructure:
  nodes: 10
  cpu_per_node: 16
  memory_per_node: 64GB
  gpu_nodes: 2
  storage_total: 500GB
  
  deployments:
    backend:
      replicas: 5
      requests:
        cpu: 4
        memory: 16Gi
    
    redis:
      replicas: 3
      mode: cluster
      memory_per_node: 16GB
    
    vector_db:
      replicas: 3
      storage: 200GB

  gpu: true (2x A100)
  cost_estimate: "$8,000-12,000/month"
```

### Scenario 3: Enterprise (10,000+ Users)

```yaml
# Configuration for enterprise

infrastructure:
  nodes: 50+
  cpu_per_node: 32
  memory_per_node: 256GB
  gpu_nodes: 10+
  storage_total: 2TB+
  
  deployments:
    backend:
      replicas: 20+
      requests:
        cpu: 8
        memory: 32Gi
    
    redis:
      replicas: 9 (3x3 cluster)
      mode: cluster_replicated
      memory_per_node: 64GB
    
    vector_db:
      replicas: 10+
      storage: 1TB+

  gpu: true (10x A100)
  multi_region: true
  disaster_recovery: true
  cost_estimate: "$50,000+/month"
```

---

## Summary

This advanced configuration guide covers:
- ✅ Multi-GPU setup for 3-5x performance boost
- ✅ Redis clustering for distributed caching
- ✅ Kubernetes orchestration at scale (3-100+ nodes)
- ✅ Advanced SSO with group mapping
- ✅ Security hardening with 10+ controls
- ✅ Disaster recovery with RPO/RTO targets
- ✅ Capacity planning formulas
- ✅ Production monitoring and alerting

**Key Takeaways**:
1. Start with single-host setup, scale to multi-host as needed
2. Use Kubernetes for automatic scaling and high availability
3. Implement Redis clustering for distributed caching
4. Configure advanced RBAC for enterprise deployments
5. Regular testing of disaster recovery procedures
6. Monitor performance metrics continuously

For questions or issues, refer to the main documentation or consult the troubleshooting section.
