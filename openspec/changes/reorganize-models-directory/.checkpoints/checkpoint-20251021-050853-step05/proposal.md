# OpenSpec Change Proposal: Reorganize Models Directory Structure

## Executive Summary

This proposal addresses the organizational inefficiency of keeping AI model files
and metadata within the `agent/models/` directory while hosting the actual model
artifacts in a separate location. The change moves model storage from `agent/models/`
to a dedicated top-level `models/` directory, improving project organization
and enabling better separation of concerns between the agent codebase and model artifacts.

**Change ID**: reorganize-models-directory  
**Status**: Ready for Review  
**Impact Level**: Medium  
**Complexity**: Low  

---

## Why

The current project organization mixes AI model artifacts and metadata with the
agent application code under `agent/models/`. That coupling creates confusion for
contributors, complicates setup and deployment, and makes it harder to share and
version models across services. Moving model artifacts to a top-level
`models/` directory separates concerns, simplifies onboarding and deployment,
and enables a single source-of-truth for model management and verification.

## Problem Statement

### Current State

The project currently has:
- `agent/models/` directory (contains metadata, model tracking files)
- Model artifacts stored separately (GPT4All `.gguf` files, embeddings, etc.)
- Mixed responsibility: agent code and model storage in same namespace
- Inconsistent organization: agent depends on models but doesn't own them

### Issues

1. **Organizational Confusion**: Models aren't truly "agent models"—they're shared artifacts
2. **Directory Clutter**: `agent/` directory contains both code and model references
3. **Dependency Inversion**: Agent code depends on models, but they're nested under agent
4. **Project Clarity**: First-time contributors unclear where to find/store models
5. **Scaling**: Adding new model types clutters the agent directory

---

## Proposed Solution

### New Directory Structure

Move models to top-level with clear organization:

```
workspace/
├── agent/              # Agent application code only
│   ├── app.py
│   ├── config.py
│   ├── models/         # REMOVED (references moved to models/)
│   ├── embeddings/
│   ├── vector_db/
│   ├── api/
│   ├── services/
│   └── ...
├── models/             # NEW: Shared model artifacts and metadata
│   ├── README.md
│   ├── models-manifest.json
│   ├── gpt4all/
│   │   ├── models-config.json
│   │   ├── *.gguf
│   │   └── checksums.json
│   ├── embeddings/
│   │   ├── sentence-transformers/
│   │   │   ├── all-MiniLM-L6-v2/
│   │   │   └── metadata.json
│   │   └── manifests/
│   ├── vosk/
│   │   ├── vosk-model-small-en-us-0.15/
│   │   └── metadata.json
│   ├── whisper/
│   │   ├── model-configs/
│   │   └── metadata.json
│   └── scripts/
│       ├── download-models.ps1
│       ├── verify-models.ps1
│       └── cleanup-models.ps1
├── tests/
└── docs/
```

### Key Changes

#### 1. Configuration Updates (MUST)

**Before**:
```yaml
# agent/config.yaml
models_dir: ./agent/models
embed_model: ./agent/models/embeddings/all-MiniLM-L6-v2
vosk_model_path: ./agent/models/vosk-model-small-en-us-0.15
```

**After**:
```yaml
# agent/config.yaml
models_dir: ./models
embed_model: ./models/embeddings/sentence-transformers/all-MiniLM-L6-v2
vosk_model_path: ./models/vosk/vosk-model-small-en-us-0.15
```

#### 2. Code Updates (MUST)

All references to model paths MUST be updated:

```python
# Before
from agent import modelmanager
model_path = "agent/models/gpt4all/..."

# After
from agent import modelmanager
model_path = "models/gpt4all/..."
```

#### 3. Directory Removal (MUST)

- `agent/models/` directory MUST be removed
- All metadata files MUST be moved to `models/`
- `.last_model_check` MUST be relocated

#### 4. New Models Directory Structure (MUST)

Create organized models directory with:
- Clear subdirectories by model type
- `models-manifest.json` for model registry
- README with setup instructions
- Download and verification scripts

---

## Impact

### 1. **Improved Organization**
- Clear separation between agent code and model artifacts
- Models are top-level, project-level resources
- First-time contributors immediately understand structure

### 2. **Better Scalability**
- Easy to add new model types (Ollama, local LLaMA, etc.)
- No namespace pollution in agent directory
- Cleaner agent codebase

### 3. **Clearer Dependencies**
- Agent depends on models (not the other way around)
- Models are infrastructure, not part of agent
- Easier for other tools to reference models

### 4. **Simplified Setup**
- Single `models/` directory to manage
- Consistent model download location
- Easier documentation and setup scripts

### 5. **Container & Deployment Clarity**
- Can mount `models/` as separate volume in containers
- Easy to share models across multiple services
- Clearer deployment strategy

---

## Implementation Plan

### Phase 1: Preparation (1-2 hours)

**Tasks**:
1. Create `models/` directory structure
2. Create `models/README.md` with setup guide
3. Create `models-manifest.json` registry
4. Create download/verification scripts
5. Document all path changes needed

**Deliverables**:
- ✅ Complete models/ directory
- ✅ All documentation
- ✅ Setup scripts

### Phase 2: Migration (2-3 hours)

**Tasks**:
1. Copy `agent/models/*` to `models/`
2. Update `agent/config.yaml` paths
3. Update all Python code references
4. Update setup scripts (setup.ps1, setup.sh)
5. Update documentation references

**Coverage**:
- ✅ 30-50 files with path references
- ✅ All configuration files
- ✅ All setup/deployment scripts
- ✅ All documentation files

### Phase 3: Verification (1-2 hours)

**Tasks**:
1. Run full test suite
2. Verify all model paths working
3. Test setup scripts
4. Verify backward compatibility
5. Check documentation accuracy

**Validation**:
- ✅ All tests passing
- ✅ Model loading works
- ✅ Setup scripts successful
- ✅ No broken references

### Phase 4: Cleanup & Documentation (1 hour)

**Tasks**:
1. Remove `agent/models/` directory
2. Update `.gitignore` if needed
3. Update README.md
4. Create migration guide
5. Document for new contributors

**Results**:
- ✅ Clean agent directory
- ✅ Complete documentation
- ✅ Migration guide for team

---

## Backward Compatibility (MUST)

### Compatibility Guarantees

✅ **Full Backward Compatibility**:
- All agent functionality MUST work identically
- Model loading MUST work with new paths
- API endpoints MUST be unchanged
- Configuration MUST be fully compatible
- Tests MUST pass 100%

### Migration Safety

- ✅ Old `agent/models/` can remain during transition
- ✅ Symlinks can bridge old paths if needed
- ✅ Gradual migration of references
- ✅ Old configuration values supported via adapter

---

## Testing Requirements

### Path Reference Tests (MUST)

```python
# tests/agent/test_model_paths.py
def test_model_paths_configuration():
    """Models directory paths must be correct."""
    config = get_config()
    assert config.models_dir == "./models"
    assert Path(config.models_dir).exists()

def test_model_loading():
    """Models must load from new location."""
    model = load_model("gpt4all")
    assert model is not None

def test_embedding_service():
    """Embeddings must work with new paths."""
    embeddings = EmbeddingService()
    assert embeddings.get_dimension() == 384
```

### Integration Tests (MUST)

- ✅ Full agent startup with new paths
- ✅ Model loading all types
- ✅ API endpoints with models
- ✅ Search and indexing with new model location

### Regression Tests (MUST)

- ✅ All existing tests must pass
- ✅ No performance degradation
- ✅ No memory leaks
- ✅ Model caching still works

---

## Files to Change

### Configuration Files
- `agent/config.yaml` - Update all model paths
- `backend/config.yaml` (if exists) - Update paths
- `.env.example` - Update model directory references

### Python Files (~30-50 files)
- `agent/modelmanager.py` - Update model path logic
- `agent/embeddings.py` - Update embedding paths
- `agent/voice.py` - Update Vosk/Whisper paths
- `agent/settings.py` - Update model directory defaults
- All tests referencing model paths

### Setup & Deployment Scripts
- `setup.ps1` - Update model download paths
- `setup.sh` - Update model download paths
- `setup-plugin.ps1` - Update paths
- `Makefile` - Update model-related tasks

### Documentation
- `README.md` - Update setup instructions
- `docs/SETUP_README.md` - Update setup guide
- `docs/CONFIGURATION_API.md` - Update config docs
- `docs/DEPENDENCY_MANAGEMENT.md` - Update paths

---

## Risk Assessment

### Risk: Broken References
**Likelihood**: Low  
**Impact**: Medium  
**Mitigation**:
- Comprehensive search for all references
- Automated path replacement with verification
- Full test suite validation

### Risk: Performance Impact
**Likelihood**: Very Low  
**Impact**: Low  
**Mitigation**:
- Paths are only resolved at startup
- No runtime performance impact
- Verification tests confirm

### Risk: Migration Complexity
**Likelihood**: Low  
**Impact**: Medium  
**Mitigation**:
- Clear phase-by-phase plan
- Detailed migration guide
- Automated migration script

### Risk: Team Confusion
**Likelihood**: Low  
**Impact**: Low  
**Mitigation**:
- Clear documentation
- Updated setup guide
- Migration guide for developers

---

## Success Criteria

### Functional Success (MUST)
- ✅ `models/` directory created with proper structure
- ✅ All models successfully moved/copied
- ✅ All paths updated throughout project
- ✅ `agent/models/` directory removed
- ✅ Setup scripts working correctly

### Quality Success (MUST)
- ✅ All tests passing (100% pass rate)
- ✅ No broken references in code
- ✅ Model loading verified for all types
- ✅ Performance unchanged
- ✅ Zero regressions

### Documentation Success (MUST)
- ✅ README.md updated for new structure
- ✅ Setup guide updated
- ✅ Configuration documented
- ✅ Migration guide created
- ✅ Developer guide updated

### Deployment Success (MUST)
- ✅ Setup scripts tested end-to-end
- ✅ Model downloads working
- ✅ Deployment procedures updated
- ✅ Team trained on new structure
- ✅ Production deployment successful

---

## Effort Estimates

| Phase | Tasks | Duration | Effort |
|-------|-------|----------|--------|
| Phase 1 | Preparation | 1-2 hours | 2 hours |
| Phase 2 | Migration | 30-50 files | 2-3 hours |
| Phase 3 | Verification | Full QA | 1-2 hours |
| Phase 4 | Documentation | Cleanup | 1 hour |
| **Total** | **Complete** | **4-5 weeks** | **6-8 hours** |

---

## Future Enhancements (MAY)

- MAY: Create `models/download-manager.py` for automated downloads
- MAY: Create `models/validator.py` for model integrity verification
- MAY: Support multiple model storage backends (S3, Azure, local)
- MAY: Add model versioning system
- MAY: Create model usage analytics

---

## References

- `openspec/changes/modularize-agent/` - Related modularization change
- `docs/SETUP_README.md` - Current setup documentation
- `.github/copilot-instructions.md` - Project architecture guide
- Previous discussions on project organization

---

**Proposal Status**: Ready for Review  
**Created**: October 21, 2025  
**Version**: 1.0  
**OpenSpec Governance**: ✅ Compliant

## Context

Describe the background and motivation.

## What Changes

List the proposed changes at a high level.

## Goals

- Goal 1: ...
- Goal 2: ...

## Stakeholders

- Owner: [owner]
- Reviewers: [reviewers]
