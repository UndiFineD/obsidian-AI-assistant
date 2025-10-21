# OpenSpec Change Specification: Reorganize Models Directory

**Change ID**: reorganize-models-directory  
**Document Type**: Technical Specification  
**Version**: 1.0  
**Status**: Ready for Implementation  

---

## Executive Summary

This specification defines the technical requirements for reorganizing the project's model storage structure. Currently, model metadata and references are scattered in `agent/models/`, but the actual model artifacts are stored separately. This change creates a coherent top-level `models/` directory that serves as the single source of truth for all AI model storage, configuration, and management.

---

## Functional Requirements

### MUST Requirements

1. **Directory Structure MUST be created**
   - `models/` as top-level directory alongside `agent/`, `tests/`, `docs/`
   - Subdirectories: `gpt4all/`, `embeddings/`, `vosk/`, `whisper/`, `scripts/`
   - Each subdirectory properly organized by model type

2. **Configuration MUST be updated**
   - All `agent/config.yaml` model paths MUST reference `./models/`
   - Environment variable defaults MUST point to new location
   - Backward compatibility adapter MAY support old paths

3. **Python Code MUST be updated**
   - All model path references MUST be changed from `agent/models/` to `models/`
   - Model loading code MUST work with new paths
   - Model caching MUST continue to function
   - No breaking changes to public APIs

4. **Tests MUST pass**
   - 100% of existing tests MUST pass with new paths
   - Model loading tests MUST verify new location
   - Integration tests MUST validate end-to-end functionality
   - Zero performance degradation

5. **Setup scripts MUST work**
   - `setup.ps1` MUST successfully download models to new location
   - `setup.sh` MUST successfully download models to new location
   - Plugin installation MUST not be affected
   - Model verification MUST work correctly

### SHOULD Requirements

- Models directory SHOULD have comprehensive README
- Models manifest JSON SHOULD document all models
- Migration guide SHOULD be created for the team
- Download/verification scripts SHOULD be provided

### MAY Requirements

- Symlinks MAY be created to old paths for compatibility
- Model download manager MAY be enhanced
- Model versioning system MAY be added
- Analytics MAY be tracked

---

## Acceptance Criteria

### Directory Structure Acceptance

```
✓ models/ directory exists at project root
✓ models/README.md documents the structure
✓ models/models-manifest.json is valid JSON
✓ models/gpt4all/ exists and is empty/populated
✓ models/embeddings/sentence-transformers/ exists
✓ models/vosk/ exists for voice models
✓ models/whisper/ exists for speech models
✓ models/scripts/ contains management scripts
✓ All directories have correct permissions
```

### Configuration Acceptance

```
✓ agent/config.yaml models_dir = "./models"
✓ agent/config.yaml embed_model points to ./models/
✓ agent/config.yaml vosk_model_path points to ./models/
✓ All model-related config keys updated
✓ Default values in code reference new paths
✓ No broken configuration references
```

### Code Acceptance

```
✓ Zero references to "agent/models/" in Python code
✓ All model loading works with new paths
✓ All model caching works correctly
✓ All embeddings load from new location
✓ Voice models load from new location
✓ No syntax errors in modified code
✓ Type hints are correct
✓ All imports resolve correctly
```

### Testing Acceptance

```
✓ 100% of unit tests pass
✓ 100% of integration tests pass
✓ Model loading tests pass
✓ Setup script tests pass
✓ Regression tests show no failures
✓ Performance tests show no degradation
✓ Code coverage maintained >85%
```

### Documentation Acceptance

```
✓ README.md updated with new structure
✓ Setup guide updated
✓ Configuration docs updated
✓ Architecture docs updated
✓ Migration guide created
✓ Team documentation complete
✓ Examples in docs are accurate
```

---

## Implementation Design

### Phase 1: Preparation

**Objective**: Create infrastructure for models directory

**Activities**:
1. Create directory structure (7 directories)
2. Create models/README.md (comprehensive guide)
3. Create models-manifest.json (model registry)
4. Create PowerShell and Bash scripts
5. Document PATH_CHANGES.md reference

**Outputs**:
- Complete models/ directory structure
- Management scripts
- Documentation
- Migration reference

**Validation**: Directory verification, script testing

### Phase 2: Migration

**Objective**: Update all references and move files

**Activities**:
1. Copy model metadata from agent/models/ to models/
2. Update agent/config.yaml (8+ references)
3. Update Python code (30-50 files)
4. Update setup scripts (setup.ps1, setup.sh, Makefile)
5. Update project documentation (5+ files)

**Scope**:
- Configuration files: 3-5 files
- Python code: 30-50 files
- Setup/deployment: 4-6 files
- Documentation: 5+ files

**Coverage**:
- 100% of model path references
- All configuration values
- All setup procedures
- All documentation

**Validation**: Syntax checking, reference verification

### Phase 3: Verification

**Objective**: Validate implementation correctness

**Activities**:
1. Path reference verification (grep for old paths)
2. Model loading tests (all 4+ model types)
3. Integration tests (full workflow)
4. Setup script tests (end-to-end)
5. Regression testing (full suite)

**Testing Coverage**:
- Unit tests: ✅ All passing
- Integration tests: ✅ All passing
- Model tests: ✅ All model types
- Setup tests: ✅ Both Windows/Linux
- Regression tests: ✅ 100% pass rate

**Quality Gates**:
- Zero broken references
- Zero syntax errors
- 100% test pass rate
- No performance degradation
- All models accessible

### Phase 4: Cleanup & Documentation

**Objective**: Finalize change and document for team

**Activities**:
1. Remove agent/models/ directory
2. Update .gitignore
3. Create migration guide
4. Update CHANGELOG.md
5. Communicate to team

**Deliverables**:
- Clean agent directory
- Updated .gitignore
- Migration guide document
- Release notes
- Team communication

---

## Data Structures

### Models Manifest Structure

```json
{
    "manifest_version": "1.0",
    "created": "2025-10-21T00:00:00Z",
    "models": {
        "gpt4all": {
            "type": "language_model",
            "provider": "GPT4All",
            "status": "optional",
            "models": []
        },
        "embeddings": {
            "type": "embedding",
            "provider": "sentence-transformers",
            "status": "required",
            "models": {
                "all-MiniLM-L6-v2": {
                    "path": "embeddings/sentence-transformers/all-MiniLM-L6-v2",
                    "size": "80MB",
                    "dimensions": 384
                }
            }
        },
        "voice": {
            "vosk": {
                "type": "stt",
                "provider": "Vosk",
                "status": "optional",
                "model": "vosk-model-small-en-us-0.15"
            },
            "whisper": {
                "type": "stt",
                "provider": "OpenAI Whisper",
                "status": "optional"
            }
        }
    }
}
```

### Configuration Schema Changes

**Current** (agent/config.yaml):
```yaml
models_dir: ./agent/models
embed_model: ./agent/models/embeddings/all-MiniLM-L6-v2
vosk_model_path: ./agent/models/vosk-model-small-en-us-0.15
```

**New** (agent/config.yaml):
```yaml
models_dir: ./models
embed_model: ./models/embeddings/sentence-transformers/all-MiniLM-L6-v2
vosk_model_path: ./models/vosk/vosk-model-small-en-us-0.15
```

---

## File Change Patterns

### Python Code Changes

**Pattern 1: Import paths**
```python
# Before
from agent.models import model_path

# After
from agent import config
model_path = config.models_dir
```

**Pattern 2: Path references**
```python
# Before
model_file = os.path.join("agent", "models", "gpt4all", "model.gguf")

# After
model_file = os.path.join(config.models_dir, "gpt4all", "model.gguf")
```

**Pattern 3: Configuration**
```python
# Before
MODEL_PATH = "./agent/models/..."

# After
MODEL_PATH = "./models/..."
```

### Configuration Changes

**Pattern 1: Path values**
```yaml
# Before
models_dir: ./agent/models

# After
models_dir: ./models
```

---

## Backward Compatibility

### Guarantees

✅ **Full Backward Compatibility MUST be maintained**:
- All agent functionality MUST work identically
- All API endpoints MUST remain unchanged
- All configuration values MUST be supported
- Tests MUST pass 100%
- No breaking changes

### Compatibility Layer (Optional)

Optional compatibility adapter MAY support old paths:
```python
# Compatibility layer
if os.path.exists("./agent/models"):
    config.models_dir = "./agent/models"  # Use old location if exists
else:
    config.models_dir = "./models"  # Use new location
```

---

## Dependencies & Integration

### No External Dependencies
- No new Python packages required
- No new system requirements
- No new OS-level dependencies

### Internal Dependencies
- Depends on agent/config.yaml loading
- Depends on settings.py defaults
- Depends on modelmanager.py logic

### Related Changes
- Complements `modularize-agent` change
- Coordinates with `modular-api-structure` change
- Aligns with project organization goals

---

## Performance Impact

### Expected Impact
- **Model Load Time**: No change (paths only resolved at startup)
- **Runtime Performance**: No impact (same model loading code)
- **Startup Time**: <1% variance (path resolution overhead minimal)
- **Memory Usage**: No change
- **Disk I/O**: No change

### Verification
- Baseline model load time recorded before migration
- Post-migration load time measured
- Target: <5% variance from baseline

---

## Risk Management

### Risk 1: Broken References
**Severity**: Medium | **Likelihood**: Low | **Mitigation**: Comprehensive search and verify pattern

### Risk 2: Setup Script Failures
**Severity**: Medium | **Likelihood**: Low | **Mitigation**: End-to-end testing on both Windows/Linux

### Risk 3: Team Confusion
**Severity**: Low | **Likelihood**: Low | **Mitigation**: Clear documentation and migration guide

### Risk 4: Performance Regression
**Severity**: Low | **Likelihood**: Very Low | **Mitigation**: Performance baseline verification

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Tests Passing | 100% | Measured after Phase 3 |
| References Updated | 100% | Verified in Phase 3 |
| Documentation Complete | 100% | Verified in Phase 4 |
| Setup Scripts Functional | 100% | Tested in Phase 3 |
| Performance Variance | <5% | Baseline checked |
| Team Ready | 100% | After Phase 4 |

---

## Rollback Plan

**If Critical Issues Found**:

1. Keep backup of agent/models/ during migration
2. Restore agent/models/ from backup
3. Revert config.yaml changes
4. Revert Python code changes
5. Verify system functionality
6. Document issues and retry

**Rollback Time Estimate**: <30 minutes

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Preparation | 1-2 hours | None |
| Phase 2: Migration | 2-3 hours | Phase 1 |
| Phase 3: Verification | 1-2 hours | Phase 2 |
| Phase 4: Cleanup | 1 hour | Phase 3 |
| **Total** | **6-8 hours** | **Sequential** |

---

## Technical Considerations

### Path Resolution
- All paths resolved at application startup
- No runtime path overhead
- Configuration caching minimizes lookups

### Model Caching
- Model caching unaffected by path change
- Cache metadata may need location update
- Old cache files can be cleaned up

### Setup Automation
- setup.ps1 updated for new paths
- setup.sh updated for new paths
- Model downloads to new location
- Verification scripts updated

---

**Specification Status**: Ready for Implementation  
**Created**: October 21, 2025  
**Version**: 1.0  
**Approved**: Pending Review

## Requirements

- **R-01**: ...
- **R-02**: ...

