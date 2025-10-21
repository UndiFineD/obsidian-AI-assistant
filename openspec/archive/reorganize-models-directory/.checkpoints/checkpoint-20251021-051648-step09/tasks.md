# OpenSpec Change Tasks: Reorganize Models Directory

## Implementation Checklist

### Phase 1: Preparation (1-2 hours)

- [ ] **1.1 Create Models Directory Structure** - Create `models/` directory with subdirectories
- [ ] **1.2 Create Models Manifest** - Create `models/models-manifest.json` with model registry
- [ ] **1.3 Create Models README** - Document models directory structure at `models/README.md`
- [ ] **1.4 Create Setup/Management Scripts** - Create 6 model management scripts (PowerShell and Bash)
- [ ] **1.5 Document Path Changes** - Create `PATH_CHANGES.md` with before/after mappings for 30-50 files

### Phase 2: Migration (2-3 hours)

- [ ] **2.1 Copy/Move Model Files** - Move model metadata from `agent/models/` to `models/`
- [ ] **2.2 Update Configuration Files** - Update `agent/config.yaml`, `.env.example`, and deployment configs
- [ ] **2.3 Update Python Code** - Update ~30-50 Python files with new model paths
- [ ] **2.4 Update Setup & Deployment Scripts** - Update `setup.ps1`, `setup.sh`, `Makefile`, etc
- [ ] **2.5 Update Documentation** - Update `README.md`, `docs/*.md`, `.github/copilot-instructions.md`

### Phase 3: Verification (1-2 hours)

- [ ] **3.1 Path Reference Verification** - Verify no `agent/models/` references remain in codebase
- [ ] **3.2 Model Loading Tests** - Test loading GPT4All, embeddings, Vosk, Whisper models
- [ ] **3.3 Integration Tests** - Run full integration test suite with new paths
- [ ] **3.4 Setup Script Validation** - Test setup scripts on Windows PowerShell and Linux Bash
- [ ] **3.5 Regression Testing** - Run full existing test suite to ensure no breakage

### Phase 4: Cleanup & Documentation (1 hour)

- [ ] **4.1 Remove Old Directory** - Backup and remove `agent/models/` directory
- [ ] **4.2 Update .gitignore** - Update `.gitignore` for new models structure
- [ ] **4.3 Create Migration Guide** - Create `docs/MIGRATION_GUIDE_MODELS_V1_0.md` for team
- [ ] **4.4 Update Project Documentation** - Update `CHANGELOG.md`, version, contributor guide
- [ ] **4.5 Team Communication** - Communicate changes to team with summary and FAQ

---

## Task Details

### Phase 1: Preparation

#### 1.1 Create Models Directory Structure
- Create `models/` root directory
- Create subdirectories:
  - `models/gpt4all/`
  - `models/embeddings/sentence-transformers/`
  - `models/vosk/`
  - `models/whisper/`
  - `models/scripts/`

#### 1.2 Create Models Manifest
- File: `models/models-manifest.json`
- Include model types: gpt4all, embeddings, vosk, whisper
- Document provider information and status
- Ensure JSON is valid and parseable

#### 1.3 Create Models README
- File: `models/README.md`
- Sections: Overview, Directory Structure, Download Instructions, Verification, Troubleshooting, Contributing
- Ensure clear setup instructions for new contributors

#### 1.4 Create Setup/Management Scripts
- `models/scripts/download-models.ps1` (PowerShell download)
- `models/scripts/download-models.sh` (Bash download)
- `models/scripts/verify-models.ps1` (PowerShell verification)
- `models/scripts/verify-models.sh` (Bash verification)
- `models/scripts/cleanup-models.ps1` (PowerShell cleanup)
- `models/scripts/cleanup-models.sh` (Bash cleanup)
- All scripts must be executable and have proper error handling

#### 1.5 Document Path Changes
- File: `openspec/changes/reorganize-models-directory/PATH_CHANGES.md`
- Document all 30-50 affected files with before/after paths
- Include configuration key changes
- Include environment variable changes
- Make easy to reference during migration

### Phase 2: Migration

#### 2.1 Copy/Move Model Files
- Move `.last_model_check` from `agent/models/` to `models/`
- Move all model metadata files
- Move configuration files
- Move cached model information
- Verify files not lost or corrupted
- Preserve permissions

#### 2.2 Update Configuration Files
- `agent/config.yaml`: Update `models_dir` from `./agent/models` to `./models`
- `.env.example`: Update all model directory references
- Docker config: Update model path mappings
- Changes needed:
  - Model directory paths
  - Embedding model paths
  - Voice model paths
  - Cache paths

#### 2.3 Update Python Code
- Update ~30-50 Python files:
  - `agent/modelmanager.py` - Core model loading
  - `agent/embeddings.py` - Embedding model paths
  - `agent/voice.py` - Voice model paths
  - `agent/settings.py` - Default paths
  - `agent/llm_router.py` - Model routing
  - All test files with hardcoded paths
- Global search/replace: `agent/models/` → `models/`
- Verify all code changes are syntactically correct

#### 2.4 Update Setup & Deployment Scripts
- `setup.ps1`: Update model path references
- `setup.sh`: Update model path references
- `setup-plugin.ps1`: Update model paths
- `Makefile`: Update model tasks
- Docker scripts: Update model configuration
- CI/CD configuration: Update paths

#### 2.5 Update Documentation
- `README.md`: Update model setup instructions
- `docs/SETUP_README.md`: Update setup guide
- `docs/CONFIGURATION_API.md`: Update configuration docs
- `docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md`: Update architecture
- `.github/copilot-instructions.md`: Update instructions
- All contributor guides: Update directory structure references

### Phase 3: Verification

#### 3.1 Path Reference Verification
- Search entire codebase for `agent/models/` (should find 0 matches)
- Verify all `models/` paths are valid and accessible
- Check all configuration values are correct
- Verify symlinks if used

#### 3.2 Model Loading Tests
- Load GPT4All models from new location
- Load embedding models from new location
- Load Vosk model from new location
- Load Whisper model from new location
- Test model caching with new paths
- Test model fallbacks

#### 3.3 Integration Tests
- Start agent/backend with new model paths
- Test health check endpoint
- Test ask endpoint with models
- Test search endpoint
- Test indexing with embeddings
- Test voice transcription

#### 3.4 Setup Script Validation
- Test fresh Windows installation (PowerShell)
- Test fresh Linux installation (Bash)
- Test plugin-only installation
- Test backend-only installation
- Test model download and verification

#### 3.5 Regression Testing
- Run all existing unit tests
- Run all integration tests
- Run all API tests
- Run all model tests
- Verify 100% test pass rate
- Check for performance degradation

### Phase 4: Cleanup & Documentation

#### 4.1 Remove Old Directory
- Backup `agent/models/` directory
- Verify all content has been migrated
- Delete `agent/models/` directory
- Verify deletion was successful

#### 4.2 Update .gitignore
- Add `models/**/*.gguf` (large model files)
- Add `models/**/*.pth` (PyTorch model files)
- Add `models/**/.cache/` (cache directories)
- Remove any `agent/models/` entries

#### 4.3 Create Migration Guide
- File: `docs/MIGRATION_GUIDE_MODELS_V1_0.md`
- Sections: Overview, What Changed, Step-by-step guide, FAQ, Troubleshooting, Rollback procedures
- Ensure new developers can understand the change

#### 4.4 Update Project Documentation
- Update `CHANGELOG.md` with change summary
- Update version number or release notes
- Update contributor guide
- Update architecture documentation
- Create summary document

#### 4.5 Team Communication
- Create summary document for team
- Highlight key changes
- Provide migration guide
- Offer training/Q&A
- Document FAQs based on questions

---

## Cross-Phase Activities

### Continuous Code Review
- When: Throughout all phases
- Reviewer: Peer developer
- Focus: Path correctness, test coverage
- Frequency: After each phase

### Documentation Updates
- When: As changes are made
- Owner: Technical writer
- Focus: Keep docs in sync with code
- Frequency: Ongoing

### Testing
- When: After each file change
- Scope: Unit + integration tests
- Coverage: 95%+ for model-related code
- Frequency: Continuous

### Performance Monitoring
- When: After Phase 3 completion
- Metrics: Model load time, startup time
- Target: No degradation vs baseline
- Frequency: Pre/post migration

---

## Acceptance Criteria

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
**Last Updated**: October 21, 2025 (Added checkbox format for Step 6)
