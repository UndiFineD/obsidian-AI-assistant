# v0.1.46 Complete API Reference

**Version**: 0.1.46  
**Release Date**: October 25, 2025  
**Status**: Production Ready  

---

## Table of Contents

1. [Custom Lanes Module](#custom-lanes-module)
2. [ML Optimizer Module](#ml-optimizer-module)
3. [Error Recovery Module](#error-recovery-module)
4. [Workflow Analytics Module](#workflow-analytics-module)
5. [Performance Profiler Module](#performance-profiler-module)

---

## Custom Lanes Module

**File**: `scripts/custom_lanes.py`  
**Purpose**: Manage custom workflow lanes and configurations  
**Status**: ✅ Production Ready (47/47 tests, 261 LOC)

### Overview

The Custom Lanes module provides a registry-based system for defining and managing custom workflow lanes. Lanes define execution paths and configurations for different workflow types.

### Public API

#### `get_registry() → LaneRegistry`

Get the global lane registry instance.

**Parameters**: None

**Returns**: 
- `LaneRegistry` - The global registry instance

**Example**:
```python
from custom_lanes import get_registry

registry = get_registry()
lanes = registry.list_all()
print(f"Available lanes: {len(lanes)}")
```

**Performance**: <10ms

---

#### `list_all_lanes() → List[Dict] | Dict`

List all configured lanes in the system.

**Parameters**: None

**Returns**:
- `List[Dict]` or `Dict` - Lane configurations

**Example**:
```python
from custom_lanes import list_all_lanes

lanes = list_all_lanes()
for lane in lanes:
    print(f"Lane: {lane['name']}, Type: {lane['type']}")
```

**Performance**: <10ms

---

#### `get_lane_by_name(name: str) → Optional[Dict]`

Retrieve a specific lane by name.

**Parameters**:
- `name` (str) - Lane identifier

**Returns**:
- `Dict` - Lane configuration if found, None otherwise

**Raises**:
- `ValueError` - If name is empty

**Example**:
```python
from custom_lanes import get_lane_by_name

lane = get_lane_by_name('processing')
if lane:
    print(f"Found lane: {lane}")
else:
    print("Lane not found")
```

**Performance**: <5ms

---

#### `validate_lane(lane_config: Dict) → bool`

Validate a lane configuration.

**Parameters**:
- `lane_config` (Dict) - Lane configuration to validate

**Returns**:
- `bool` - True if valid, False otherwise

**Raises**:
- `ValueError` - If validation fails with reason

**Example**:
```python
from custom_lanes import validate_lane

config = {
    'name': 'custom_lane',
    'type': 'processing',
    'timeout': 30
}

if validate_lane(config):
    print("Configuration is valid")
else:
    print("Invalid configuration")
```

**Performance**: <20ms

---

### Lane Configuration Schema

```yaml
lane:
  name: string          # Unique lane identifier
  type: string          # Lane type (processing, analysis, etc.)
  priority: integer     # Execution priority (higher = earlier)
  timeout: integer      # Timeout in seconds
  retry_count: integer  # Number of retries on failure
  metadata:
    key: value          # Custom metadata
```

---

## ML Optimizer Module

**File**: `scripts/stage_optimizer.py`  
**Purpose**: ML-based workflow stage prediction and optimization  
**Status**: ✅ Production Ready (34/34 tests, 400 LOC)

### Overview

The ML Optimizer module uses machine learning to predict next stages and optimize workflow execution paths based on historical data.

### Classes

#### `StagePredictor`

Machine learning based stage predictor using scikit-learn.

**Constructor**: `StagePredictor()`

**Methods**:

##### `train(training_data: List[Dict]) → None`

Train the ML model on historical workflow data.

**Parameters**:
- `training_data` (List[Dict]) - Historical workflow execution data

**Expected Data Format**:
```python
[
    {
        'current_stage': 'stage_name',
        'next_stage': 'target_stage',
        'execution_time': 123.4,
        'success': True,
        'metadata': {...}
    },
    ...
]
```

**Raises**:
- `ValueError` - If training data invalid or insufficient

**Example**:
```python
from stage_optimizer import StagePredictor

predictor = StagePredictor()
training_data = [
    {'current_stage': 'validate', 'next_stage': 'process', 'execution_time': 100},
    {'current_stage': 'process', 'next_stage': 'finalize', 'execution_time': 200},
]
predictor.train(training_data)
```

**Performance**: 100-500ms depending on data size

---

##### `predict(current_stage: str) → Optional[str]`

Predict the next stage for a given current stage.

**Parameters**:
- `current_stage` (str) - Current workflow stage

**Returns**:
- `str` - Predicted next stage
- `None` - If no prediction available

**Example**:
```python
next_stage = predictor.predict('validate')
if next_stage:
    print(f"Predicted next stage: {next_stage}")
```

**Performance**: <10ms

---

##### `get_recommendations() → List[Dict]`

Get optimization recommendations based on training data.

**Parameters**: None

**Returns**:
- `List[Dict]` - List of recommendations with details

**Example**:
```python
recommendations = predictor.get_recommendations()
for rec in recommendations:
    print(f"Stage: {rec['stage']}, Optimization: {rec['recommendation']}")
```

**Performance**: <50ms

---

##### `get_stats() → Dict`

Get predictor statistics and performance metrics.

**Parameters**: None

**Returns**:
- `Dict` - Statistics including accuracy, training samples, etc.

**Example**:
```python
stats = predictor.get_stats()
print(f"Model accuracy: {stats['accuracy']}")
print(f"Trained on {stats['training_samples']} samples")
```

**Performance**: <5ms

---

##### `is_trained() → bool`

Check if the predictor has been trained.

**Parameters**: None

**Returns**:
- `bool` - True if trained, False otherwise

**Performance**: <1ms

---

### Module Functions

#### `get_stage_predictor() → StagePredictor`

**Note**: Not available as function. Use `StagePredictor()` constructor directly.

---

### Performance Characteristics

- **Training Time**: O(n) where n = training samples (typically 100-500ms)
- **Prediction Time**: <10ms per prediction
- **Memory**: ~5-10MB per trained model
- **Accuracy**: Depends on training data quality (typically 70-85%)

---

## Error Recovery Module

**File**: `scripts/error_recovery.py`  
**Purpose**: State validation, error recovery, and checkpoint management  
**Status**: ✅ Production Ready (32/32 tests, 330 LOC)

### Overview

The Error Recovery module provides comprehensive state validation, automatic error repair, and checkpoint-based rollback capabilities.

### Classes

#### `StateValidator`

Validates workflow state and detects anomalies.

**Constructor**: `StateValidator(status_file: str)`

**Parameters**:
- `status_file` (str) - Path to status file for validation

**Example**:
```python
from error_recovery import StateValidator

validator = StateValidator('./workflow_status.json')
```

---

##### `validate(state: Dict) → bool`

Validate a workflow state.

**Parameters**:
- `state` (Dict) - Workflow state to validate

**Returns**:
- `bool` - True if valid, False otherwise

**Example**:
```python
state = {'status': 'running', 'progress': 50}
if validator.validate(state):
    print("State is valid")
else:
    print("Invalid state detected")
```

**Performance**: <20ms

---

##### `get_validation_errors() → List[str]`

Get list of validation errors from last validation.

**Parameters**: None

**Returns**:
- `List[str]` - List of error messages

**Example**:
```python
errors = validator.get_validation_errors()
for error in errors:
    print(f"Error: {error}")
```

**Performance**: <5ms

---

#### `StateRepair`

Automatically repair invalid workflow states.

**Constructor**: `StateRepair()`

---

##### `repair(broken_state: Dict) → Dict`

Repair a broken workflow state.

**Parameters**:
- `broken_state` (Dict) - Invalid state to repair

**Returns**:
- `Dict` - Repaired state

**Example**:
```python
from error_recovery import StateRepair

repairer = StateRepair()
broken_state = {'status': 'invalid_state', 'progress': 150}
fixed_state = repairer.repair(broken_state)
print(f"Repaired state: {fixed_state}")
```

**Performance**: 50-200ms

---

#### `CheckpointRollback`

Rollback workflow to previous checkpoint.

**Constructor**: `CheckpointRollback()`

---

##### `rollback(checkpoint_id: str) → bool`

Rollback to a previous checkpoint.

**Parameters**:
- `checkpoint_id` (str) - ID of checkpoint to restore

**Returns**:
- `bool` - True if rollback successful

**Example**:
```python
from error_recovery import CheckpointRollback

rollback = CheckpointRollback()
if rollback.rollback('checkpoint_001'):
    print("Successfully rolled back")
```

**Performance**: 100-500ms

---

#### `ResourceCleaner`

Clean up resources and free memory.

**Constructor**: `ResourceCleaner()`

---

##### `cleanup() → bool`

Perform cleanup operations.

**Parameters**: None

**Returns**:
- `bool` - True if cleanup successful

**Performance**: 50-100ms

---

### Module Functions

#### `validate_state(state: Dict) → bool`

Module-level state validation function.

**Parameters**:
- `state` (Dict) - State to validate

**Returns**:
- `bool` - Validation result

---

#### `repair_state(broken_state: Dict) → Dict`

Module-level state repair function.

**Parameters**:
- `broken_state` (Dict) - State to repair

**Returns**:
- `Dict` - Repaired state

---

#### `rollback_to_checkpoint(checkpoint_id: str) → bool`

Module-level checkpoint rollback function.

**Parameters**:
- `checkpoint_id` (str) - Checkpoint to restore

**Returns**:
- `bool` - Success status

---

### Error Recovery Workflow

```
Detect Error
    ↓
Validate State → Invalid → Repair State → Validate Again
                     ↓
                   Still Invalid → Rollback to Checkpoint
                     ↓
                   Cleanup Resources
```

---

## Workflow Analytics Module

**File**: `scripts/workflow_analytics.py`  
**Purpose**: Collect, analyze, and report workflow metrics  
**Status**: ✅ Production Ready (36/36 tests, 697 LOC)

### Overview

The Workflow Analytics module provides comprehensive metrics collection, trend analysis, dashboard generation, and report formatting.

### Classes

#### `MetricsAggregator`

Aggregate and manage workflow metrics.

**Constructor**: `MetricsAggregator()`

---

##### `add_metric(category: str, name: str, value: float) → None`

Add a metric to the aggregator.

**Parameters**:
- `category` (str) - Metric category
- `name` (str) - Metric name
- `value` (float) - Metric value

**Example**:
```python
from workflow_analytics import MetricsAggregator

agg = MetricsAggregator()
agg.add_metric('performance', 'execution_time', 123.4)
agg.add_metric('performance', 'memory_usage', 256)
```

**Performance**: <5ms per metric

---

##### `get_aggregated_metrics() → Dict`

Get all aggregated metrics.

**Parameters**: None

**Returns**:
- `Dict` - All metrics organized by category

**Example**:
```python
metrics = agg.get_aggregated_metrics()
for category, data in metrics.items():
    print(f"Category: {category}")
    for name, value in data.items():
        print(f"  {name}: {value}")
```

**Performance**: <10ms

---

##### `export_metrics(format: str = 'json', file_path: Optional[str] = None) → Union[str, None]`

Export metrics to file or string.

**Parameters**:
- `format` (str) - Export format ('json', 'csv')
- `file_path` (Optional[str]) - File path for export

**Returns**:
- `str` - Formatted metrics if no file_path
- `None` - If written to file

**Example**:
```python
# Export to JSON string
json_metrics = agg.export_metrics('json')

# Export to file
agg.export_metrics('json', './metrics.json')
```

**Performance**: 20-50ms

---

#### `TrendAnalyzer`

Analyze trends in workflow metrics.

**Constructor**: `TrendAnalyzer()`

---

##### `analyze_trends(metrics_history: List[Dict]) → Dict`

Analyze trends in historical metrics.

**Parameters**:
- `metrics_history` (List[Dict]) - Historical metric data

**Returns**:
- `Dict` - Trend analysis results

**Example**:
```python
from workflow_analytics import TrendAnalyzer

analyzer = TrendAnalyzer()
history = [
    {'timestamp': '2025-10-25 10:00', 'execution_time': 100},
    {'timestamp': '2025-10-25 10:15', 'execution_time': 95},
    {'timestamp': '2025-10-25 10:30', 'execution_time': 92},
]
trends = analyzer.analyze_trends(history)
print(f"Trend: {trends['direction']}")
```

**Performance**: 50-100ms

---

#### `DashboardGenerator`

Generate dashboard HTML for visualization.

**Constructor**: `DashboardGenerator()`

---

##### `generate_dashboard(metrics: Dict) → str`

Generate dashboard HTML.

**Parameters**:
- `metrics` (Dict) - Metrics to display

**Returns**:
- `str` - HTML dashboard code

**Example**:
```python
from workflow_analytics import DashboardGenerator

generator = DashboardGenerator()
metrics = agg.get_aggregated_metrics()
html = generator.generate_dashboard(metrics)
with open('dashboard.html', 'w') as f:
    f.write(html)
```

**Performance**: <100ms

---

#### `ReportFormatter`

Format metrics into reports.

**Constructor**: `ReportFormatter()`

---

##### `format_report(metrics: Dict, report_type: str = 'summary') → str`

Format metrics into a report.

**Parameters**:
- `metrics` (Dict) - Metrics to report
- `report_type` (str) - Report type ('summary', 'detailed', 'executive')

**Returns**:
- `str` - Formatted report text

**Example**:
```python
from workflow_analytics import ReportFormatter

formatter = ReportFormatter()
report = formatter.format_report(metrics, 'detailed')
print(report)
```

**Performance**: 50-200ms

---

---

## Performance Profiler Module

**File**: `scripts/performance_profiler.py`  
**Purpose**: Profile stage execution and detect bottlenecks  
**Status**: ✅ Production Ready (33/33 tests, 249 LOC)

### Overview

The Performance Profiler module provides detailed stage profiling, bottleneck detection, and optimization recommendations.

### Classes

#### `StageProfiler`

Profile workflow stage execution.

**Constructor**: `StageProfiler()`

---

##### `start_stage(stage_name: str) → None`

Start profiling a stage.

**Parameters**:
- `stage_name` (str) - Name of stage to profile

**Example**:
```python
from performance_profiler import StageProfiler

profiler = StageProfiler()
profiler.start_stage('data_validation')
# ... execute stage ...
profiler.end_stage('data_validation')
```

**Performance**: <1ms

---

##### `end_stage(stage_name: str) → None`

End profiling a stage.

**Parameters**:
- `stage_name` (str) - Name of stage

**Performance**: <1ms

---

##### `get_stage_stats(stage_name: str) → Dict`

Get profiling statistics for a stage.

**Parameters**:
- `stage_name` (str) - Stage name

**Returns**:
- `Dict` - Statistics including duration, count, average time

**Example**:
```python
stats = profiler.get_stage_stats('data_validation')
print(f"Duration: {stats['duration']}ms")
print(f"Count: {stats['count']}")
print(f"Average: {stats['avg_time']}ms")
```

**Performance**: <5ms

---

#### `BottleneckDetector`

Detect performance bottlenecks.

**Constructor**: `BottleneckDetector()`

---

##### `detect(stage_profiles: Dict) → List[Dict]`

Detect bottlenecks in stage profiles.

**Parameters**:
- `stage_profiles` (Dict) - Stage profiling data

**Returns**:
- `List[Dict]` - Detected bottlenecks with details

**Example**:
```python
from performance_profiler import BottleneckDetector

detector = BottleneckDetector()
profiles = {
    'stage1': {'duration': 50},
    'stage2': {'duration': 500},  # Bottleneck
    'stage3': {'duration': 100},
}
bottlenecks = detector.detect(profiles)
for bn in bottlenecks:
    print(f"Bottleneck: {bn['stage']} ({bn['duration']}ms)")
```

**Performance**: 20-50ms

---

#### `ProfileAnalyzer`

Analyze profiling data.

**Constructor**: `ProfileAnalyzer()`

---

##### `analyze(profiles: Dict) → Dict`

Analyze profiling data.

**Parameters**:
- `profiles` (Dict) - Profiling data

**Returns**:
- `Dict` - Analysis results

**Performance**: 30-60ms

---

#### `RecommendationEngine`

Generate optimization recommendations.

**Constructor**: `RecommendationEngine()`

---

##### `recommend(profiles: Dict) → List[Dict]`

Generate optimization recommendations.

**Parameters**:
- `profiles` (Dict) - Profiling data

**Returns**:
- `List[Dict]` - Recommendations with priority

**Example**:
```python
from performance_profiler import RecommendationEngine

engine = RecommendationEngine()
recommendations = engine.recommend(profiles)
for rec in recommendations:
    print(f"Priority {rec['priority']}: {rec['recommendation']}")
```

**Performance**: 50-100ms

---

---

## Cross-Module Integration Points

### Data Flow

```
Custom Lanes
    ↓
    └→ Select execution path
    
Stage Optimizer
    ↓
    ├→ Predicts next stages
    ├→ Optimizes execution
    └→ Provides recommendations
    
Workflow Analytics
    ↓
    ├→ Collects metrics
    ├→ Analyzes trends
    ├→ Generates reports
    └→ Visualizes dashboards
    
Performance Profiler
    ↓
    ├→ Profiles stages
    ├→ Detects bottlenecks
    ├→ Analyzes performance
    └→ Recommends optimizations
    
Error Recovery
    ├→ Validates state at each stage
    ├→ Repairs errors
    ├→ Manages checkpoints
    └→ Recovers from failures
```

---

## Performance Summary

| Module | Init | Operation | Memory |
|--------|------|-----------|--------|
| Custom Lanes | <1ms | 5-20ms | <1MB |
| ML Optimizer | 10-50ms | 10-100ms | 5-10MB |
| Error Recovery | <5ms | 20-500ms | <2MB |
| Analytics | <5ms | 5-200ms | 1-5MB |
| Profiler | <5ms | 1-100ms | 1-3MB |

---

## Error Handling

All modules implement comprehensive error handling:

- **Validation Errors**: Caught and detailed with specific messages
- **Recovery Errors**: Logged with context for debugging
- **Performance Errors**: Monitored and reported
- **Integration Errors**: Handled with fallback mechanisms

---

## Version Compatibility

**v0.1.46** compatible with:
- Python 3.8+
- Windows, macOS, Linux
- scikit-learn 1.0+
- pandas 1.0+

---

**Document Status**: COMPLETE  
**Last Updated**: October 25, 2025  
**Maintenance**: Track module changes and update as needed
