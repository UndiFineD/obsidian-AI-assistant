# OpenSpec Change Tasks: Reorganize Models Directory

## Task Breakdown

### Phase 1: Preparation (1-2 hours)

#### 1.1 Create Models Directory Structure
- **Task**: Create `models/` directory with subdirectories
- **Subtasks**:
  1. Create `models/` root directory
  2. Create `models/gpt4all/` subdirectory
  3. Create `models/embeddings/` subdirectory
  4. Create `models/embeddings/sentence-transformers/` subdirectory
  5. Create `models/vosk/` subdirectory
  6. Create `models/whisper/` subdirectory
  7. Create `models/scripts/` subdirectory
- **Acceptance Criteria**:
  - All directories exist with proper structure
  - Permissions correct for file access

#### 1.2 Create Models Manifest
- **Task**: Create comprehensive models registry
- **File**: `models/models-manifest.json`
- **Content**:
  ```json
  {
    "manifest_version": "1.0",
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
        "models": {}
      },
      "voice": {
        "vosk": {
          "type": "stt",
          "provider": "Vosk",
          "status": "optional"
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
- **Acceptance Criteria**:
  - JSON valid and parseable
  - All model types documented
  - Manifest accessible from config

#### 1.3 Create Models README
- **Task**: Document models directory structure
- **File**: `models/README.md`
- **Sections**:
  1. Overview of models directory
  2. Directory structure explanation
  3. Model download instructions
  4. Model verification procedures
  5. Troubleshooting guide
  6. Contributing new models
- **Acceptance Criteria**:
  - Comprehensive documentation
  - All model types covered
  - Setup instructions clear
  - New contributors can understand structure

#### 1.4 Create Setup/Management Scripts
- **Task**: Create model management scripts
- **Scripts**:
  1. `models/scripts/download-models.ps1` (PowerShell)
  2. `models/scripts/download-models.sh` (Bash)
  3. `models/scripts/verify-models.ps1` (PowerShell)
  4. `models/scripts/verify-models.sh` (Bash)
  5. `models/scripts/cleanup-models.ps1` (PowerShell)
  6. `models/scripts/cleanup-models.sh` (Bash)
- **Acceptance Criteria**:
  - Scripts executable
  - Error handling working
  - Downloads functional
  - Verification accurate

#### 1.5 Document Path Changes
- **Task**: Create comprehensive reference of all path changes
- **File**: `openspec/changes/reorganize-models-directory/PATH_CHANGES.md`
- **Content**:
  - Before/after path mappings
  - All 30-50 files affected
  - Configuration key changes
  - Environment variable changes
- **Acceptance Criteria**:
  - All paths documented
  - Easy to reference during migration
  - Complete coverage

---

### Phase 2: Migration (2-3 hours)

#### 2.1 Copy/Move Model Files
- **Task**: Move model metadata from `agent/models/` to `models/`
- **Files to move**:
  1. `.last_model_check` → `models/.last_model_check`
  2. Any model metadata files
  3. Any configuration files
  4. Any cached model information
- **Acceptance Criteria**:
  - All files successfully moved
  - No files lost or corrupted
  - Permissions preserved

#### 2.2 Update Configuration Files
- **Task**: Update all configuration references to model paths
- **Files to update**:
  1. `agent/config.yaml` - `models_dir`, embedding paths
  2. `.env.example` - Model directory references
  3. Any deployment config files
  4. Docker configuration if exists
- **Changes**:
  - `models_dir: ./agent/models` → `models_dir: ./models`
  - `embed_model: ./agent/models/...` → `embed_model: ./models/embeddings/...`
  - `vosk_model_path: ./agent/models/...` → `vosk_model_path: ./models/vosk/...`
- **Acceptance Criteria**:
  - All paths updated
  - Paths verified valid
  - No broken references

#### 2.3 Update Python Code
- **Task**: Update all Python file references to model paths
- **Files to update** (~30-50 files):
  1. `agent/modelmanager.py` - Core model loading logic
  2. `agent/embeddings.py` - Embedding model paths
  3. `agent/voice.py` - Voice model paths
  4. `agent/settings.py` - Default paths
  5. `agent/llm_router.py` - Model routing
  6. `backend/settings.py` if exists
  7. All service files using models
  8. All test files with hardcoded paths
- **Pattern Changes**:
  - Search: `agent/models/`, Replace: `models/`
  - Search: `agent\.models`, Replace: `.models` config
  - Update path construction logic if needed
- **Acceptance Criteria**:
  - All references updated
  - Code verified syntactically correct
  - No hardcoded agent/models/ paths remain

#### 2.4 Update Setup & Deployment Scripts
- **Task**: Update model path references in scripts
- **Files to update**:
  1. `setup.ps1` - PowerShell setup script
  2. `setup.sh` - Bash setup script
  3. `setup-plugin.ps1` - Plugin setup
  4. `Makefile` - Make tasks
  5. Any Docker scripts
  6. Any CI/CD configuration
- **Changes**:
  - Update model download paths
  - Update model verification paths
  - Update cleanup paths
  - Update documentation paths
- **Acceptance Criteria**:
  - Scripts updated and tested
  - Model downloads work correctly
  - Setup process successful

#### 2.5 Update Documentation
- **Task**: Update all documentation files
- **Files to update**:
  1. `README.md` - Main project readme
  2. `docs/SETUP_README.md` - Setup guide
  3. `docs/CONFIGURATION_API.md` - Configuration docs
  4. `docs/DEPENDENCY_MANAGEMENT.md` - Dependency docs
  5. `docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md` - Architecture
  6. `.github/copilot-instructions.md` - Instructions
  7. Any contributor guides
  8. Any deployment guides
- **Changes**:
  - Update path references
  - Update setup instructions
  - Update directory structure diagrams
  - Update examples
- **Acceptance Criteria**:
  - All documentation updated
  - Examples correct and tested
  - Setup instructions accurate

---

### Phase 3: Verification (1-2 hours)

#### 3.1 Path Reference Verification
- **Task**: Verify no broken path references remain
- **Tests**:
  1. Search entire codebase for `agent/models/` - should find 0
  2. Verify all `models/` paths are valid
  3. Check all configuration values
  4. Verify symlinks if used
- **Acceptance Criteria**:
  - Zero remaining `agent/models/` references
  - All `models/` paths valid and accessible
  - Configuration consistent

#### 3.2 Model Loading Tests
- **Task**: Test model loading with new paths
- **Test cases**:
  1. Load GPT4All models
  2. Load embedding models
  3. Load Vosk model
  4. Load Whisper model
  5. Model caching works
  6. Model fallbacks work
- **Acceptance Criteria**:
  - All models load successfully
  - Performance unchanged
  - Caching functional

#### 3.3 Integration Tests
- **Task**: Run full integration test suite
- **Tests**:
  1. Start agent with new paths
  2. Health check endpoint
  3. Ask endpoint with models
  4. Search endpoint
  5. Indexing with embeddings
  6. Voice transcription
- **Acceptance Criteria**:
  - All endpoints functional
  - All models accessible
  - No errors or warnings

#### 3.4 Setup Script Validation
- **Task**: Test setup scripts end-to-end
- **Scenarios**:
  1. Fresh installation on Windows (PowerShell)
  2. Fresh installation on Linux (Bash)
  3. Plugin-only installation
  4. Backend-only installation
  5. Model download and verification
- **Acceptance Criteria**:
  - All scenarios work correctly
  - Models properly downloaded
  - Verification passes

#### 3.5 Regression Testing
- **Task**: Run full existing test suite
- **Coverage**:
  1. All existing unit tests
  2. All integration tests
  3. All API tests
  4. All model tests
- **Acceptance Criteria**:
  - 100% test pass rate
  - No new failures introduced
  - No performance degradation

---

### Phase 4: Cleanup & Documentation (1 hour)

#### 4.1 Remove Old Directory
- **Task**: Remove `agent/models/` directory
- **Steps**:
  1. Backup `agent/models/` directory
  2. Verify all content migrated
  3. Delete `agent/models/`
  4. Verify deletion successful
- **Acceptance Criteria**:
  - `agent/models/` no longer exists
  - No data loss
  - Agent directory clean

#### 4.2 Update .gitignore
- **Task**: Update .gitignore for new structure
- **Changes**:
  1. Add `models/**/*.gguf` (if not present)
  2. Add `models/**/*.pth` (if not present)
  3. Add `models/**/.cache/` (if not present)
  4. Remove `agent/models/` entries
- **Acceptance Criteria**:
  - .gitignore properly updated
  - Model files not tracked (unless intended)
  - Agent models directory not mentioned

#### 4.3 Create Migration Guide
- **Task**: Document migration process for team
- **File**: `docs/MIGRATION_GUIDE_MODELS_V1_0.md`
- **Sections**:
  1. Change overview
  2. What changed and why
  3. Step-by-step for developers
  4. FAQ and troubleshooting
  5. Rollback procedures if needed
- **Acceptance Criteria**:
  - Comprehensive guide
  - New developers can understand
  - FAQ covers common issues
  - Rollback documented

#### 4.4 Update Project Documentation
- **Task**: Final documentation updates
- **Updates**:
  1. Update CHANGELOG.md
  2. Update VERSION or release notes
  3. Update contributor guide
  4. Update architecture documentation
  5. Create summary document
- **Acceptance Criteria**:
  - All documentation current
  - Changes clearly documented
  - Contributors informed

#### 4.5 Team Communication
- **Task**: Communicate changes to team
- **Actions**:
  1. Create summary document
  2. Highlight key changes
  3. Provide migration guide
  4. Offer training/Q&A
  5. Document FAQs based on questions
- **Acceptance Criteria**:
  - Team understands change
  - Team can work with new structure
  - No confusion or errors

---

## Cross-Phase Activities

### Continuous Code Review
- **When**: Throughout all phases
- **Reviewer**: Peer developer
- **Focus**: Path correctness, test coverage
- **Frequency**: After each phase

### Documentation Updates
- **When**: As changes are made
- **Owner**: Technical writer
- **Focus**: Keep docs in sync with code
- **Frequency**: Ongoing

### Testing
- **When**: After each file change
- **Scope**: Unit + integration tests
- **Coverage**: 95%+ for model-related code
- **Frequency**: Continuous

### Performance Monitoring
- **When**: After Phase 3 completion
- **Metrics**: Model load time, startup time
- **Target**: No degradation vs baseline
- **Frequency**: Pre/post migration

---

## Acceptance Criteria by Phase

### Phase 1 Complete When
- ✅ All directories created and organized
- ✅ Models manifest complete and valid
- ✅ README comprehensive
- ✅ Scripts functional and tested
- ✅ Path change documentation complete

### Phase 2 Complete When
- ✅ All model files moved successfully
- ✅ All configuration files updated
- ✅ All Python code updated (~30-50 files)
- ✅ All setup scripts updated
- ✅ All documentation updated

### Phase 3 Complete When
- ✅ No broken path references found
- ✅ All models load successfully
- ✅ All integration tests pass
- ✅ Setup scripts validated end-to-end
- ✅ Full test suite passes (100%)

### Phase 4 Complete When
- ✅ Old `agent/models/` directory removed
- ✅ .gitignore updated correctly
- ✅ Migration guide created and comprehensive
- ✅ All documentation updated
- ✅ Team trained and ready

---

## Success Metrics

- **Functional**: 100% models work from new location
- **Quality**: 100% test pass rate
- **Performance**: <5% variance in model load time
- **Documentation**: 100% of references updated
- **Deployment**: Setup scripts work end-to-end

---

**Task Status**: Ready for Implementation  
**Created**: October 21, 2025  
**Version**: 1.0
