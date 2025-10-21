# Specification: Reorganize Models Directory

## Requirements

### Functional Requirements
1. All AI models must be accessible from `models/` directory at project root
2. Backend must correctly load models from new location without errors
3. Plugin must function correctly with relocated models
4. All existing model functionality must be preserved

### Non-Functional Requirements
1. No performance degradation from model loading
2. Path changes must be transparent to end users
3. Backward compatibility not required (breaking change OK)

## Acceptance Criteria

### Directory Structure
- `models/` directory exists at project root
- All model files successfully moved from `backend/models/`
- Directory structure matches the original layout

### Code Changes
- All import paths updated to reference new location
- No hardcoded old paths remain in codebase
- Configuration files reflect new model path
- CI/CD scripts updated for new location

### Testing
- Unit tests for model loading pass (100%)
- Backend health checks pass
- Plugin integration tests pass
- No regression in existing functionality

## Technical Details

### Current Structure
```
backend/
  models/
    - gpt4all-model.gguf
    - embeddings-model.gguf
    - vosk-model/
```

### New Structure
```
models/
  - gpt4all-model.gguf
  - embeddings-model.gguf
  - vosk-model/
```

### Files to Update
1. `backend/settings.py` - MODELS_DIR configuration
2. `backend/modelmanager.py` - Model loading paths
3. `backend/embeddings.py` - Embedding model paths
4. `backend/voice.py` - Voice model paths
5. `plugin/backendClient.js` - Model endpoint references
6. `.github/workflows/*.yml` - CI/CD paths
7. Setup scripts - `setup.ps1`, `setup.sh`
8. Documentation files

### Risk Assessment
- **Low Risk**: Simple path updates, no logic changes required
- **Validation**: Unit tests ensure functionality preserved
