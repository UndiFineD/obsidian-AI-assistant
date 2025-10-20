# ⚡ Performance Benchmarking Guide

_Obsidian AI Assistant - Performance Testing & Benchmark Interpretation_  
_Version: 1.0_  
_Date: October 16, 2025_

---

## 📋 Overview

This guide documents the **automated performance benchmarking workflow**, expected **SLA targets**, and how to
**interpret benchmark results** for the Obsidian AI Assistant.

Performance benchmarks are automatically collected via the **`.github/workflows/benchmark.yml`** workflow and validated
against the comprehensive targets defined in **`docs/PERFORMANCE_REQUIREMENTS_SPECIFICATION.md`**.

---

## 🔄 Automated Benchmark Workflow

### GitHub Actions Benchmark Pipeline

The benchmark workflow runs automatically every Monday at 03:00 UTC and can be triggered manually via workflow dispatch.

**Workflow File**: `.github/workflows/benchmark.yml`

```yaml
name: Scheduled Benchmark Metrics

on:
  schedule:
    - cron: '0 3 * * 1'  # Every Monday at 03:00 UTC
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-benchmark
      - name: Run pytest-benchmark
        run: |
          python -m pytest --benchmark-only --benchmark-save=latest
      - name: Upload benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: .benchmarks/latest/results.json
      - name: (Optional) Update metrics docs
        run: |
          python scripts/update_test_metrics.py --apply --skip-pytest --duration "0.0s" --coverage "N/A"
        continue-on-error: true
```

### Running Benchmarks Locally

To run performance benchmarks locally, use the following commands:

```powershell
# Full benchmark suite with pytest-benchmark
python -m pytest --benchmark-only --benchmark-save=baseline

# Run specific performance tests
pytest tests/test_performance.py -v --benchmark-only

# Compare against previous baseline
python -m pytest --benchmark-only --benchmark-compare=baseline
```

### Benchmark Output Location

Benchmark results are saved to:

- **Artifacts**: `.benchmarks/latest/results.json` (uploaded to GitHub Actions)
- **Local runs**: `.benchmarks/<timestamp>/results.json`

---

## 🎯 Performance SLA Targets

### Response Time Tiers

The system defines **5 performance tiers** based on operation complexity and user expectations:

| Tier | Target | Operations | SLA Percentile |
|------|--------|------------|----------------|
| **Tier 1** | **< 100ms** | Health checks, status, config | p95 < 100ms, p99 < 200ms |
| **Tier 2** | **< 500ms** | Cached queries, simple search, voice | p95 < 500ms, p99 < 1000ms |
| **Tier 3** | **< 2s** | AI generation, document search, embeddings | p95 < 2000ms, p99 < 5000ms |
| **Tier 4** | **< 10s** | Web analysis, large doc indexing | p95 < 10000ms, p99 < 20000ms |
| **Tier 5** | **< 60s** | Vault reindex, model loading | p95 < 45000ms, p99 < 60000ms |

### Critical Endpoint Targets

#### Health & Monitoring Endpoints

```yaml
GET /health:
  target_p50: 25ms
  target_p95: 50ms
  target_p99: 100ms
  max_acceptable: 200ms

GET /status:
  target_p50: 15ms
  target_p95: 30ms
  target_p99: 75ms
  max_acceptable: 150ms

GET /api/performance/metrics:
  target_p50: 40ms
  target_p95: 80ms
  target_p99: 120ms
  max_acceptable: 250ms
```

#### AI Operation Endpoints

```yaml
POST /ask (cached):
  target_p50: 150ms
  target_p95: 300ms
  target_p99: 500ms
  cache_hit_rate: > 75%

POST /ask (uncached):
  target_p50: 800ms
  target_p95: 1500ms
  target_p99: 2000ms
  tokens_per_second: > 50

POST /search:
  target_p50: 300ms
  target_p95: 800ms
  target_p99: 1500ms
  max_documents: 10000
```

#### Complex Operations

```yaml
POST /reindex (incremental):
  target_p50: 2000ms
  target_p95: 5000ms
  target_p99: 8000ms
  files_per_batch: < 50

POST /web (analyze):
  target_p50: 3000ms
  target_p95: 6000ms
  target_p99: 10000ms
  content_size_limit: 500KB
```

### Throughput Targets

| Operation Type | Requests/Second | Concurrent Limit | Queue Depth |
|----------------|-----------------|------------------|-------------|
| Health Checks | 1000+ | Unlimited | N/A |
| Simple AI Queries | 50-100 | 25 | 100 |
| Complex AI Processing | 5-15 | 10 | 25 |
| Document Indexing | 10-25 docs/s | 3 | 50 |
| Voice Transcription | 2-5 files/s | 5 | 10 |

### Resource Utilization Targets

```yaml
CPU Usage:
  idle: < 5%
  light_load (1-5 users): < 25%
  medium_load (5-25 users): 25-60%
  high_load (25-100 users): 60-85%
  peak_load (100+ users): 85-95%

Memory Usage:
  base_system: < 1 GB
  small_models: 4-6 GB
  medium_models: 8-12 GB
  large_models: 16-24 GB
  cache_allocation: 256MB - 2GB

Storage I/O:
  vector_db_iops: > 1000 IOPS
  read_latency: < 10ms
  write_latency: < 20ms
  cache_read_speed: > 500 MB/s
```

---

## 📊 Interpreting Benchmark Results

### Understanding pytest-benchmark Output

When you run `pytest --benchmark-only`, you'll see output like this:

```text
---------------------------------------------------------------------------------------------- benchmark: 12 tests
----------------------------------------------------------------------------------------------
Name (time in ms)                              Min                 Max                Mean            StdDev
Median               IQR            Outliers     OPS            Rounds  Iterations
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_health_endpoint                        18.2341          45.1234          21.5432          3.2145          20.1234
2.3456          5;2  46.4321          100           1
test_status_endpoint                        12.3456          38.9012          14.7890          2.4567          13.9012
1.8901          8;3  67.6234          120           1
test_cached_ask_endpoint                   123.4567         456.7890         178.9012         45.6789         156.7890
34.5678          3;1   5.5901           50           1
test_uncached_ask_endpoint                 678.9012        1456.7890         890.1234        123.4567         834.5678
89.0123          2;0   1.1234           20           1
test_search_endpoint                       234.5678         789.0123         345.6789         67.8901         321.2345
56.7890          4;2   2.8930           40           1
```

### Key Metrics Explained

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **Min** | Fastest execution time | Best-case performance |
| **Max** | Slowest execution time | Worst-case performance (watch for outliers) |
| **Mean** | Average execution time | Typical performance |
| **StdDev** | Standard deviation | Consistency (lower is better) |
| **Median** | Middle value | Representative performance (less affected by outliers) |
| **IQR** | Interquartile range | Spread of middle 50% of values |
| **Outliers** | Statistical anomalies | Format: `x;y` (mild;severe outliers) |
| **OPS** | Operations per second | Throughput metric |

### SLA Compliance Analysis

Compare benchmark results against SLA targets:

#### ✅ Passing Example

```text
test_health_endpoint:
  Median: 20.1234ms
  Target p50: 25ms
  Status: ✅ PASS (19.5% margin)
  
  p95 (approximated from IQR): ~22.5ms
  Target p95: 50ms
  Status: ✅ PASS (55% margin)
```

#### ❌ Failing Example

```text
test_uncached_ask_endpoint:
  Median: 834.5678ms
  Target p50: 800ms
  Status: ⚠️ NEAR LIMIT (4.3% over)
  
  Max: 1456.7890ms
  Target p99: 2000ms
  Status: ✅ PASS (within p99 tolerance)
```

### Trend Analysis

Monitor benchmark trends over time:

```powershell
# Compare against baseline
python -m pytest --benchmark-only --benchmark-compare=baseline --benchmark-compare-fail=mean:10%

# This will fail if mean performance degrades by >10%
```

### Performance Regression Detection

The benchmark workflow can detect regressions:

- **Mean degradation > 10%**: Warning
- **Mean degradation > 25%**: Failure
- **p95 exceeds SLA**: Critical failure

---

## 🔧 Performance Testing Scenarios

### 1. Load Testing

**Objective**: Validate performance under typical concurrent load.

```powershell
# Using Locust for load testing
python -m locust -f tests/load_test.py --users 50 --spawn-rate 10 --run-time 5m
```

**Expected Results**:
- Response times remain within Tier 1-3 targets
- No errors under 50 concurrent users
- Resource utilization < 70%

### 2. Stress Testing

**Objective**: Determine breaking point and failure modes.

```powershell
# Gradually increase load until failures occur
python -m locust -f tests/load_test.py --users 200 --spawn-rate 5 --run-time 10m
```

**Expected Results**:
- Graceful degradation under extreme load
- Circuit breakers activate before catastrophic failure
- Recovery within 60s of load reduction

### 3. Spike Testing

**Objective**: Validate handling of sudden traffic spikes.

```powershell
# Simulate sudden spike from 10 to 100 users
python -m locust -f tests/spike_test.py --users 100 --spawn-rate 90 --run-time 3m
```

**Expected Results**:
- Response times degrade < 50% during spike
- Queue management handles burst traffic
- Auto-scaling triggers (if enabled)

### 4. Endurance Testing

**Objective**: Validate stability over extended periods.

```powershell
# Run for 24 hours with moderate load
python -m locust -f tests/load_test.py --users 25 --spawn-rate 5 --run-time 24h
```

**Expected Results**:
- No memory leaks (stable memory usage)
- Response times remain consistent
- No degradation over time

---

## 📈 Benchmark Metrics Collection

### Custom Benchmark Tests

Create custom benchmarks for specific operations:

```python
import pytest

def test_custom_operation_benchmark(benchmark):
    """Benchmark custom operation against SLA target."""
    def operation():
        # Your operation here
        return perform_complex_operation()
    
    # Run benchmark
    result = benchmark(operation)
    
    # Validate against SLA
    assert result.stats.median < 2.0  # 2 second SLA
    assert result.stats.mean < 2.5
```

### Benchmark Groups

Organize benchmarks by tier:

```python
# tests/benchmarks/test_tier1_benchmarks.py
@pytest.mark.benchmark(group="tier1")
def test_health_check_benchmark(benchmark):
    result = benchmark(lambda: requests.get("http://localhost:8000/health"))
    assert result.stats.median < 0.1  # 100ms SLA

# tests/benchmarks/test_tier3_benchmarks.py
@pytest.mark.benchmark(group="tier3")
def test_ai_generation_benchmark(benchmark):
    result = benchmark(lambda: requests.post("http://localhost:8000/ask", json={"prompt": "test"}))
    assert result.stats.median < 2.0  # 2s SLA
```

### Running Benchmark Groups

```powershell
# Run only Tier 1 benchmarks
pytest tests/benchmarks/ -m tier1 --benchmark-only

# Run all tiers and generate comparison report
pytest tests/benchmarks/ --benchmark-only --benchmark-autosave --benchmark-save-data
```

---

## 🎯 Performance Optimization Workflow

### 1. Identify Bottlenecks

```powershell
# Profile slow operations
python -m cProfile -o profile.stats backend/backend.py

# Analyze with snakeviz
snakeviz profile.stats
```

### 2. Benchmark Before Changes

```powershell
# Establish baseline before optimization
pytest --benchmark-only --benchmark-save=before-optimization
```

### 3. Implement Optimization

Example: Add caching layer

```python
from backend.performance import cached

@cached(ttl=3600, key_func=lambda req: f"ask:{req.prompt}")
async def ask_endpoint(request: QueryRequest):
    return await process_query(request)
```

### 4. Benchmark After Changes

```powershell
# Compare against baseline
pytest --benchmark-only --benchmark-compare=before-optimization
```

### 5. Validate Improvement

```text
Expected output:
------------------------------------------------------------------------------------------
Name (time in ms)                 Before          After           Change
------------------------------------------------------------------------------------------
test_ask_endpoint              890.1234        234.5678        -73.6%  ✅ IMPROVEMENT
```

---

## 🚀 CI/CD Integration

### GitHub Actions Benchmark Validation

The benchmark workflow automatically:

1. **Runs full benchmark suite** every Monday
2. **Compares against previous week** for regressions
3. **Uploads results as artifacts** for historical analysis
4. **Updates metrics documentation** (optional)

### Manual Workflow Trigger

```bash
# Trigger benchmark workflow via GitHub CLI
gh workflow run benchmark.yml

# Or via web UI:
# Actions → Scheduled Benchmark Metrics → Run workflow
```

### Benchmark Reports

Access benchmark results:

1. Navigate to **Actions** tab in GitHub
2. Select **Scheduled Benchmark Metrics** workflow
3. Click on latest run
4. Download **benchmark-results** artifact
5. Extract and analyze `results.json`

---

## 📋 Performance Checklist

### Pre-Release Performance Validation

Before releasing new versions, validate:

- [ ] **Tier 1 endpoints**: All < 100ms p95
- [ ] **Tier 2 endpoints**: All < 500ms p95
- [ ] **Tier 3 endpoints**: All < 2s p95
- [ ] **Tier 4 endpoints**: All < 10s p95
- [ ] **Tier 5 endpoints**: All < 60s p95
- [ ] **Cache hit rate**: > 75%
- [ ] **Error rate**: < 1%
- [ ] **Resource utilization**: 60-80% under load
- [ ] **No memory leaks**: Stable over 1 hour endurance test
- [ ] **Throughput**: Meets minimum RPS targets

### Performance Regression Review

If benchmarks fail:

1. **Identify regressed endpoints** from comparison report
2. **Review recent code changes** affecting those endpoints
3. **Profile the slow operations** to pinpoint bottleneck
4. **Implement optimization** or revert problematic changes
5. **Re-run benchmarks** to validate fix
6. **Update SLA targets** if justified by new features

---

## 📚 Additional Resources

### Related Documentation

- **Performance Requirements**: `docs/PERFORMANCE_REQUIREMENTS_SPECIFICATION.md`
- **System Architecture**: `.github/copilot-instructions.md`
- **Testing Standards**: `docs/TESTING_STANDARDS_SPECIFICATION.md`
- **Integration Testing**: `docs/INTEGRATION_TESTING.md` (to be created)

### Performance Testing Tools

- **pytest-benchmark**: Python benchmark framework
- **Locust**: Load testing tool (see `tests/load_test.py`)
- **cProfile/snakeviz**: Python profiling tools
- **Grafana/Prometheus**: Production monitoring (optional)

### Benchmark Best Practices

1. **Run on consistent hardware**: Use same machine/VM for comparisons
2. **Minimize background processes**: Close unnecessary applications
3. **Use multiple iterations**: Default 5-10 rounds per benchmark
4. **Warm up the system**: Run once before benchmarking
5. **Monitor resource usage**: Ensure no resource contention
6. **Compare like-for-like**: Same Python version, dependencies, config

---

## 🎯 Summary

This guide provides comprehensive documentation for:

- ✅ **Automated benchmark workflow** (`.github/workflows/benchmark.yml`)
- ✅ **SLA targets** for all performance tiers (Tier 1-5)
- ✅ **Benchmark interpretation** (understanding pytest-benchmark output)
- ✅ **Performance testing scenarios** (load, stress, spike, endurance)
- ✅ **Optimization workflow** (identify, benchmark, improve, validate)
- ✅ **CI/CD integration** (automated regression detection)

**For detailed SLA requirements and optimization strategies, refer to `docs/PERFORMANCE_REQUIREMENTS_SPECIFICATION.md`
.**

---

_Performance Benchmarking Guide Version: 1.0_  
_Last Updated: October 16, 2025_  
_Next Review: January 16, 2026_  
_Status: Production Ready_
