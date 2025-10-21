# OpenSpec Change: Reorganize Models Directory

## Executive Summary

**Change ID**: reorganize-models-directory  
**Status**: Ready for Review  
**Scope**: Move AI models from `agent/models/` to top-level `models/` directory  
**Impact**: Medium (30-50 files affected)  
**Effort**: 6-8 hours  
**Timeline**: 4 phases over 1 day  

---

## What's Changing

### Before
```
agent/
├── models/          # Model metadata and references
├── app.py
├── config.yaml
└── ... (other code)
```

### After
```
agent/               # Code only (no models/)
├── app.py
├── config.yaml
└── ... (other code)

models/              # Dedicated model directory (NEW)
├── README.md
├── models-manifest.json
├── gpt4all/
├── embeddings/
├── vosk/
├── whisper/
└── scripts/
```

---

## Why This Change?

### Problems Solved
1. ✅ **Organization**: Models clearly separated from code
2. ✅ **Clarity**: First-time contributors know where to find models
3. ✅ **Scalability**: Easy to add new model types without cluttering agent/
4. ✅ **Dependencies**: Correct dependency direction (agent depends on models, not vice versa)
5. ✅ **Deployment**: Simplified containerization with separate model volume

### Benefits
- Cleaner project structure
- Easier to understand architecture
- Better for team onboarding
- Supports future cloud storage integration
- Enables model versioning and management

---

## Implementation Timeline

| Phase | Duration | Tasks | Key Activities |
|-------|----------|-------|-----------------|
| Phase 1 | 1-2h | 5 | Create directories, manifests, scripts |
| Phase 2 | 2-3h | 5 | Migrate files, update configs, update code |
| Phase 3 | 1-2h | 5 | Verify paths, test loading, run tests |
| Phase 4 | 1h | 5 | Cleanup, update docs, team communication |
| **Total** | **6-8h** | **20** | **Complete reorganization** |

---

## Files Included in This Change

### Governance Documents

| File | Lines | Purpose |
|------|-------|---------|
| `proposal.md` | 280 | Executive proposal with problem/solution |
| `tasks.md` | 400+ | 20 detailed implementation tasks |

### Technical Specifications

| File | Lines | Purpose |
|------|-------|---------|
| `specs/models-structure/spec.md` | 350+ | Master capability specification |

---

## Key Specifications

### Directory Structure (MUST)
```
models/
├── README.md                 # Documentation
├── models-manifest.json      # Model registry
├── gpt4all/                  # LLM models
│   ├── models-config.json
│   ├── checksums.json
│   └── (model files)
├── embeddings/               # Embedding models
│   └── sentence-transformers/
├── vosk/                      # Vosk STT
├── whisper/                   # Whisper STT
└── scripts/                   # Management scripts
```

### Configuration Updates (MUST)
```yaml
# OLD
models_dir: ./agent/models
embed_model: ./agent/models/embeddings/...

# NEW
models_dir: ./models
embed_model: ./models/embeddings/sentence-transformers/...
```

### Code Changes (MUST)
- Update ~30-50 files with path references
- Update all configuration files
- Update all setup scripts
- Update all documentation

---

## Testing Requirements

### Coverage (MUST)
- ✅ Path reference tests
- ✅ Model loading tests (all types)
- ✅ Integration tests
- ✅ Setup script validation
- ✅ Full regression test suite

### Success Criteria
- ✅ All tests passing (100%)
- ✅ No broken references
- ✅ Models load correctly
- ✅ Performance unchanged

---

## Files to Update (~30-50 total)

### Configuration Files (5 files)
- `agent/config.yaml` - Model paths
- `.env.example` - Environment variables
- Docker config if exists

### Python Code (25-35 files)
- `agent/modelmanager.py` - Core model logic
- `agent/embeddings.py` - Embedding paths
- `agent/voice.py` - Voice model paths
- `agent/settings.py` - Default paths
- All test files with model paths
- Service files using models

### Scripts (8-10 files)
- `setup.ps1` - Setup script
- `setup.sh` - Bash setup
- `setup-plugin.ps1` - Plugin setup
- `Makefile` - Build tasks
- Docker scripts if exists

### Documentation (5-8 files)
- `README.md` - Project readme
- `docs/SETUP_README.md` - Setup guide
- `docs/CONFIGURATION_API.md` - Config docs
- `.github/copilot-instructions.md` - Instructions
- Other deployment guides

---

## Backward Compatibility

✅ **100% Backward Compatible**
- All APIs work identically
- All functionality preserved
- All tests pass
- No breaking changes

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Broken references | Low | Medium | Comprehensive search/replace, testing |
| Performance impact | Very Low | Low | Path resolution at startup only |
| Migration confusion | Low | Low | Clear documentation and guides |
| Deployment issues | Low | Medium | Test setup scripts end-to-end |

---

## Success Metrics

- ✅ **Functional**: 100% of models work from new location
- ✅ **Quality**: 100% test pass rate
- ✅ **Performance**: <5% variance in model load time
- ✅ **Documentation**: All references updated
- ✅ **Deployment**: Setup scripts validated

---

## Team Review Checklist

### Before Approval
- [ ] Change scope understood
- [ ] Directory structure makes sense
- [ ] Configuration updates clear
- [ ] Performance requirements acceptable
- [ ] Timeline realistic
- [ ] Risk mitigations adequate

### After Approval
- [ ] Assigned to developer
- [ ] Feature branch created
- [ ] Phase 1 started
- [ ] Progress tracking established

---

## Next Steps

1. **This Week**:
   - Review this change package
   - Provide feedback or approval
   - Discuss any concerns

2. **Next Week (if approved)**:
   - Create feature branch
   - Execute Phase 1 (directory setup)
   - Execute Phase 2 (file migration)
   - Execute Phase 3 (verification)
   - Execute Phase 4 (cleanup/docs)
   - Merge to main

3. **After Completion**:
   - Train team on new structure
   - Update team documentation
   - Monitor for any issues

---

## Contact

For questions about this change:
1. Review `proposal.md` for detailed rationale
2. Check `tasks.md` for implementation details
3. Read `specs/models-structure/spec.md` for technical specs

---

**Status**: Ready for Review  
**Version**: 1.0  
**Created**: October 21, 2025  
**OpenSpec Governance**: ✅ Compliant
