# OpenSpec Change Test Plan: Reorganize Models Directory

**Change ID**: reorganize-models-directory  
**Document Type**: Test Plan & Strategy  
**Version**: 1.0  
**Status**: Ready for Testing  

---

## Test Strategy Overview

This test plan validates that the models directory reorganization (from `agent/models/` to top-level `models/`) maintains 100% functionality while improving project organization.

**Test Objective**: Ensure all model loading, configuration, and setup functionality works identically with new directory structure.

**Test Scope**: 
- Configuration path resolution
- Model loading (all 4+ types)
- Setup script execution
- Integration workflows
- Regression testing

**Entry Criteria**: 
- All migration tasks completed
- All code updated
- All scripts ready

**Exit Criteria**: 
- 100% test pass rate
- Zero broken references
- Performance baseline maintained
- Team approval

---

## Test Types & Coverage

### 1. Unit Tests

#### 1.1 Configuration Path Tests

**Test**: `test_models_directory_configuration`
- **Purpose**: Verify config paths point to models/
- **Scenario**: Load config from agent/config.yaml
- **Assertion**: `config.models_dir == "./models"`
- **Pass Criteria**: Path is correct and directory exists

**Test**: `test_embedding_model_path`
- **Purpose**: Verify embedding model path correct
- **Scenario**: Get embedding model path from config
- **Assertion**: Path includes "models/embeddings/sentence-transformers/"
- **Pass Criteria**: Path resolves successfully

**Test**: `test_vosk_model_path`
- **Purpose**: Verify Vosk model path correct
- **Scenario**: Get voice model path from config
- **Assertion**: Path includes "models/vosk/"
- **Pass Criteria**: Path resolves successfully

**Test**: `test_whisper_model_path`
- **Purpose**: Verify Whisper model path correct
- **Scenario**: Get voice model path
- **Assertion**: Path includes "models/whisper/"
- **Pass Criteria**: Path resolves successfully

#### 1.2 Model Loading Tests

**Test**: `test_load_gpt4all_model`
- **Purpose**: Verify GPT4All model loads from new location
- **Setup**: Ensure model exists in models/gpt4all/
- **Scenario**: Load GPT4All model
- **Assertion**: Model loaded successfully
- **Pass Criteria**: Model instance returned, ready to use

**Test**: `test_load_embedding_model`
- **Purpose**: Verify embedding model loads from new location
- **Setup**: Ensure model exists in models/embeddings/
- **Scenario**: Load embedding service
- **Assertion**: Service initialized successfully
- **Pass Criteria**: Embedding dimension = 384

**Test**: `test_model_caching`
- **Purpose**: Verify model caching works with new paths
- **Scenario**: Load same model twice
- **Assertion**: Second load returns cached instance
- **Pass Criteria**: Cache hits work, no path errors

**Test**: `test_model_fallback`
- **Purpose**: Verify model fallback logic works
- **Scenario**: Attempt to load unavailable model
- **Assertion**: Falls back to alternative
- **Pass Criteria**: Fallback succeeds

#### 1.3 Code Reference Tests

**Test**: `test_no_agent_models_references`
- **Purpose**: Verify no hardcoded "agent/models/" in code
- **Scenario**: Grep entire codebase for old path
- **Assertion**: Zero matches found
- **Pass Criteria**: No old references remain

**Test**: `test_all_model_paths_updated`
- **Purpose**: Verify all paths use new location
- **Scenario**: Check config and code paths
- **Assertion**: All paths reference "models/"
- **Pass Criteria**: 100% of paths updated

### 2. Integration Tests

#### 2.1 Setup Script Tests

**Test**: `test_setup_ps1_models_download`
- **Platform**: Windows
- **Purpose**: Verify models download to new location
- **Scenario**: Run setup.ps1 with fresh install
- **Assertions**: 
  - No errors during execution
  - models/ directory created
  - Model files downloaded
  - Verification passes
- **Pass Criteria**: Setup completes successfully

**Test**: `test_setup_sh_models_download`
- **Platform**: Linux
- **Purpose**: Verify models download on Linux
- **Scenario**: Run setup.sh with fresh install
- **Assertions**:
  - No errors during execution
  - models/ directory created
  - Model files downloaded
  - Verification passes
- **Pass Criteria**: Setup completes successfully

**Test**: `test_setup_plugin_with_new_paths`
- **Purpose**: Verify plugin setup unaffected
- **Scenario**: Run setup-plugin.ps1
- **Assertion**: No path-related errors
- **Pass Criteria**: Plugin setup successful

#### 2.2 Agent Startup Tests

**Test**: `test_agent_startup_with_new_paths`
- **Purpose**: Verify agent starts with new paths
- **Scenario**: Start agent application
- **Assertions**:
  - No configuration errors
  - No path resolution errors
  - No model loading errors
  - Health check passes
- **Pass Criteria**: Agent starts and is healthy

**Test**: `test_api_health_endpoint`
- **Purpose**: Verify health endpoint works
- **Scenario**: GET /health
- **Assertion**: Returns 200 with model status
- **Pass Criteria**: Health check passes in <100ms

**Test**: `test_api_status_endpoint`
- **Purpose**: Verify status includes model info
- **Scenario**: GET /api/health/detailed
- **Assertion**: Response includes model paths and status
- **Pass Criteria**: Status shows all models ready

#### 2.3 Model Usage Tests

**Test**: `test_ask_endpoint_with_models`
- **Purpose**: Verify /ask endpoint works
- **Scenario**: POST /ask with question
- **Assertions**:
  - No path errors
  - Model loads correctly
  - Response generated
  - Response format correct
- **Pass Criteria**: Returns valid response

**Test**: `test_search_endpoint_with_embeddings`
- **Purpose**: Verify search uses embeddings from new location
- **Scenario**: POST /api/search with query
- **Assertions**:
  - Embedding model loads from models/embeddings/
  - Search executes successfully
  - Results returned
- **Pass Criteria**: Search returns relevant results

**Test**: `test_indexing_with_embeddings`
- **Purpose**: Verify document indexing works
- **Scenario**: POST /api/reindex
- **Assertions**:
  - Embeddings load from new location
  - Indexing completes
  - Vector DB updated
- **Pass Criteria**: Indexing completes successfully

**Test**: `test_voice_transcription`
- **Purpose**: Verify voice features work
- **Scenario**: POST /transcribe with audio
- **Assertions**:
  - Voice model loads from models/vosk/ or models/whisper/
  - Transcription completes
  - Text returned
- **Pass Criteria**: Returns transcription

### 3. Regression Tests

#### 3.1 Existing Test Suite

**Test Suite**: Run all existing tests
- **Purpose**: Verify no regressions introduced
- **Scope**: All unit, integration, API tests
- **Assertion**: 100% pass rate
- **Pass Criteria**: Zero new failures

**Coverage Areas**:
- Model management: ✅ All tests pass
- Embeddings: ✅ All tests pass
- Voice/transcription: ✅ All tests pass
- API endpoints: ✅ All tests pass
- Setup scripts: ✅ All tests pass
- Configuration: ✅ All tests pass

#### 3.2 Performance Tests

**Test**: `test_model_load_time_baseline`
- **Purpose**: Record baseline model load time
- **Before Migration**: Measure current performance
- **Assertion**: Load time recorded in baseline
- **Pass Criteria**: Baseline established

**Test**: `test_model_load_time_after_migration`
- **Purpose**: Verify no performance regression
- **After Migration**: Measure performance
- **Assertion**: <5% variance from baseline
- **Pass Criteria**: Performance maintained

**Test**: `test_startup_time_unchanged`
- **Purpose**: Verify agent startup not affected
- **Assertion**: Startup time within 5% of baseline
- **Pass Criteria**: No startup overhead

**Test**: `test_memory_usage_unchanged`
- **Purpose**: Verify memory usage not impacted
- **Assertion**: Memory usage within 5% of baseline
- **Pass Criteria**: No memory regression

### 4. Acceptance Tests

#### 4.1 Directory Structure

**Test**: `test_models_directory_structure`
- **Purpose**: Verify complete directory structure
- **Validations**:
  - ✅ models/ exists at project root
  - ✅ models/README.md exists and contains instructions
  - ✅ models/models-manifest.json exists and valid JSON
  - ✅ models/gpt4all/ exists
  - ✅ models/embeddings/sentence-transformers/ exists
  - ✅ models/vosk/ exists
  - ✅ models/whisper/ exists
  - ✅ models/scripts/ exists with management scripts
- **Pass Criteria**: All directories present with correct content

#### 4.2 Documentation

**Test**: `test_documentation_updated`
- **Purpose**: Verify all docs reference new paths
- **Validations**:
  - ✅ README.md updated
  - ✅ Setup guide updated
  - ✅ Configuration docs updated
  - ✅ Architecture docs updated
  - ✅ No old agent/models/ paths in docs
  - ✅ Migration guide exists
- **Pass Criteria**: All documentation current

#### 4.3 Cleanup

**Test**: `test_agent_models_directory_removed`
- **Purpose**: Verify old directory is removed
- **Assertion**: agent/models/ does not exist
- **Pass Criteria**: Old directory cleaned up

**Test**: `test_gitignore_updated`
- **Purpose**: Verify .gitignore correct
- **Validations**:
  - ✅ models/**/*.gguf ignored
  - ✅ models/**/*.pth ignored
  - ✅ models/**/.cache/ ignored
  - ✅ agent/models/ entry removed
- **Pass Criteria**: .gitignore is correct

---

## Test Execution Plan

### Phase 1: Unit Tests (30 minutes)

**Execution**:
```powershell
pytest tests/unit/test_model_paths.py -v
pytest tests/unit/test_model_loading.py -v
pytest tests/unit/test_configuration.py -v
```

**Success Criteria**: All unit tests pass (15+ tests)

### Phase 2: Integration Tests (45 minutes)

**Execution**:
```powershell
# Setup script tests
.\tests\integration\test_setup_scripts.ps1

# Agent startup tests
pytest tests/integration/test_agent_startup.py -v

# Model usage tests
pytest tests/integration/test_model_usage.py -v
```

**Success Criteria**: All integration tests pass (20+ tests)

### Phase 3: Regression Tests (60 minutes)

**Execution**:
```powershell
# Full existing test suite
pytest tests/ -v --tb=short

# Performance baseline
pytest tests/performance/test_baselines.py -v
```

**Success Criteria**: 100% pass rate on existing suite

### Phase 4: Acceptance Tests (30 minutes)

**Execution**:
```powershell
# Structure validation
python scripts/validate_models_structure.py

# Documentation check
python scripts/validate_documentation.py

# Cleanup verification
python scripts/verify_cleanup.py
```

**Success Criteria**: All acceptance criteria met

---

## Test Data & Fixtures

### Model Fixtures

**Fixture**: Small test models for fast testing
```
test_fixtures/
├── models/
│   ├── gpt4all/test_model.gguf
│   ├── embeddings/test_embedding.bin
│   └── vosk/test_model.tgz
```

### Configuration Fixtures

**Fixture**: Test config.yaml with models/ paths
```yaml
models_dir: ./models
embed_model: ./models/embeddings/test_embedding.bin
vosk_model_path: ./models/vosk/test_model
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Unit Test Pass Rate | 100% | pytest report |
| Integration Test Pass Rate | 100% | pytest report |
| Regression Test Pass Rate | 100% | pytest report |
| Broken References | 0 | grep results |
| Documentation Coverage | 100% | documentation review |
| Performance Variance | <5% | benchmark comparison |
| Team Readiness | 100% | feedback survey |

---

## Entry & Exit Criteria

### Entry Criteria (Before Testing)
- ✅ Phase 1-2 completed (migration done)
- ✅ All code changes committed
- ✅ All documentation updated
- ✅ Test environment ready
- ✅ Test data prepared

### Exit Criteria (Before Approval)
- ✅ 100% unit test pass rate
- ✅ 100% integration test pass rate
- ✅ 100% regression test pass rate
- ✅ All acceptance criteria met
- ✅ Performance baseline maintained
- ✅ Documentation validated
- ✅ Team approved

---

## Risk Mitigation

### Risk: Tests Fail After Migration
**Impact**: Blocks approval  
**Mitigation**: Immediate code review and fixes  
**Rollback**: Revert changes and try alternative approach

### Risk: Performance Regression
**Impact**: Production impact  
**Mitigation**: Investigate root cause and optimize  
**Rollback**: Use compatibility layer if needed

### Risk: Documentation Incomplete
**Impact**: Team confusion  
**Mitigation**: Update docs before final approval  
**Rollback**: N/A (documentation-only)

---

## Test Report Template

```
OpenSpec Change Test Report
===========================

Change ID: reorganize-models-directory
Date: [Date]
Tester: [Name]

Test Results
============

Unit Tests: [X/Y] PASSED
Integration Tests: [X/Y] PASSED
Regression Tests: [X/Y] PASSED
Acceptance Tests: [X/Y] PASSED

Total: [X] PASSED, [Y] FAILED

Performance Impact
==================

Baseline Load Time: [X]ms
Post-Migration Load Time: [Y]ms
Variance: [Z]%

Issues Found
============

[List any issues and resolutions]

Approvals
=========

Tester: ___________________
Date: ___________________

Lead Reviewer: ___________________
Date: ___________________
```

---

**Test Plan Status**: Ready for Execution  
**Created**: October 21, 2025  
**Version**: 1.0  
**Next Action**: Execute Phase 1 unit tests after migration complete
