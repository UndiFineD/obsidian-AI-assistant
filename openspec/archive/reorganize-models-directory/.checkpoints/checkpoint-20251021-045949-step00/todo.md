# OpenSpec Change TODO: Reorganize Models Directory

**Change ID**: reorganize-models-directory  
**Owner**: @Development Team  
**Created**: October 21, 2025  
**Status**: Ready for Implementation  

---

## Project Overview

Move AI model storage from `agent/models/` to dedicated top-level `models/` directory. This improves project organization by separating application code from model artifacts.

**Expected Duration**: 6-8 hours (4 phases over 1-2 days)  
**Complexity**: Low  
**Risk**: Low  

---

## Workflow Checklist

### Step 0: Create TODOs ✅
- [x] **0. Create TODOs** - This document

### Step 1: Version Increment ⏳
- [ ] **1. Increment Release Version**
  - Detect current version from package.json/CHANGELOG.md
  - Increment patch version (X.Y.Z → X.Y.Z+1)
  - Create release branch: `release-X.Y.Z+1`
  - Update package.json, CHANGELOG.md, README.md

### Step 2: Proposal Review ✅
- [x] **2. Proposal Review** - Completed
  - [x] proposal.md created and comprehensive
  - [x] Problem statement clear
  - [x] Solution detailed with before/after examples
  - [x] Risk assessment included
  - [x] Success criteria defined

### Step 3: Specification ⏳
- [ ] **3. Create Specification**
  - [ ] Create spec.md with technical details
  - [ ] Define acceptance criteria
  - [ ] Detail implementation approach
  - [ ] Document data models and changes
  - [ ] Add architecture diagrams if needed

### Step 4: Task Breakdown ✅
- [x] **4. Task Breakdown** - Completed
  - [x] tasks.md created with 4 phases
  - [x] 20+ detailed tasks defined
  - [x] Phase descriptions complete
  - [x] Acceptance criteria for each phase
  - [x] Timeline and effort estimates provided

### Step 5: Test Definition ⏳
- [ ] **5. Create Test Definition**
  - [ ] Create test_plan.md
  - [ ] Define unit test cases
  - [ ] Define integration test cases
  - [ ] Define regression test cases
  - [ ] Define acceptance test criteria

### Step 6: Script & Tooling ⏳
- [ ] **6. Script & Tooling**
  - [ ] Analyze documentation for requirements
  - [ ] Generate test script (test_script.ps1)
  - [ ] Generate implementation script (implement.ps1)
  - [ ] Validate script syntax
  - [ ] Execute automated tests

### Step 7: Implementation ⏳
- [ ] **7. Implementation**
  - [ ] Run implement.ps1 script
  - [ ] Monitor task execution
  - [ ] Handle any errors or blockers
  - [ ] Verify all changes applied

### Step 8: Testing ⏳
- [ ] **8. Test Run & Validation**
  - [ ] Run full test suite
  - [ ] Verify model paths working
  - [ ] Check configuration accuracy
  - [ ] Validate setup scripts
  - [ ] Performance baseline check

### Step 9: Documentation ⏳
- [ ] **9. Generate Documentation**
  - [ ] Create or update README
  - [ ] Create migration guide
  - [ ] Update CHANGELOG
  - [ ] Update architecture docs
  - [ ] Create release notes

### Step 10: Git Operations ⏳
- [ ] **10. Git Operations**
  - [ ] Stage all changes: `git add -A`
  - [ ] Create commit with clear message
  - [ ] Push to release branch
  - [ ] Verify remote branch created

### Step 11: Archive Management ⏳
- [ ] **11. Archive Management**
  - [ ] Archive old configs if applicable
  - [ ] Move completed tasks
  - [ ] Archive background docs
  - [ ] Prepare for PR submission

### Step 12: Pull Request ⏳
- [ ] **12. Create Pull Request**
  - [ ] Create PR from release branch to main
  - [ ] Fill PR template
  - [ ] Link to proposal.md and tasks.md
  - [ ] Request reviewers
  - [ ] Monitor CI/CD checks

---

## Phase Breakdown

### Phase 1: Preparation (1-2 hours)
- [ ] Create models/ directory structure
- [ ] Create models/README.md
- [ ] Create models-manifest.json
- [ ] Create management scripts
- [ ] Document all path changes

**Status**: Ready to Start  
**Owner**: Development Team  
**Estimated Completion**: After Step 6

### Phase 2: Migration (2-3 hours)
- [ ] Copy/move model files
- [ ] Update configuration files
- [ ] Update Python code (~30-50 files)
- [ ] Update setup/deployment scripts
- [ ] Update documentation

**Status**: Blocked on Phase 1  
**Owner**: Development Team  
**Estimated Completion**: After Phase 1 + 3 hours

### Phase 3: Verification (1-2 hours)
- [ ] Verify path references
- [ ] Test model loading
- [ ] Run integration tests
- [ ] Validate setup scripts
- [ ] Run full regression suite

**Status**: Blocked on Phase 2  
**Owner**: QA Team  
**Estimated Completion**: After Phase 2 + 2 hours

### Phase 4: Cleanup & Documentation (1 hour)
- [ ] Remove old agent/models/ directory
- [ ] Update .gitignore
- [ ] Create migration guide
- [ ] Update project documentation
- [ ] Communicate to team

**Status**: Blocked on Phase 3  
**Owner**: Development Team  
**Estimated Completion**: After Phase 3 + 1 hour

---

## Files to Modify

### Critical Configuration Files
- [ ] `agent/config.yaml` - Update 8+ path references
- [ ] `.env.example` - Update model directory references
- [ ] `Makefile` - Update model-related tasks

### Python Code (30-50 files estimated)
- [ ] `agent/modelmanager.py` - Update model path logic
- [ ] `agent/embeddings.py` - Update embedding paths
- [ ] `agent/voice.py` - Update Vosk/Whisper paths
- [ ] `agent/settings.py` - Update defaults
- [ ] `agent/llm_router.py` - Update routing
- [ ] All test files with hardcoded paths
- [ ] Other service files

### Setup & Deployment Scripts
- [ ] `setup.ps1` - Update Windows setup
- [ ] `setup.sh` - Update Linux setup
- [ ] `setup-plugin.ps1` - Update plugin setup
- [ ] CI/CD workflow files if applicable

### Documentation Files
- [ ] `README.md` - Update instructions
- [ ] `docs/SETUP_README.md` - Update setup guide
- [ ] `docs/CONFIGURATION_API.md` - Update config docs
- [ ] `docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md` - Update architecture
- [ ] `.github/copilot-instructions.md` - Update guidelines

### New Files to Create
- [ ] `models/` - New top-level directory
- [ ] `models/README.md` - Models directory guide
- [ ] `models/models-manifest.json` - Model registry
- [ ] `models/scripts/download-models.ps1` - Download script
- [ ] `models/scripts/download-models.sh` - Download script
- [ ] Migration guide document

---

## Success Criteria

### Must Complete Before Next Step
- ✅ proposal.md comprehensive and approved
- ⏳ spec.md defined and complete
- ⏳ test_plan.md with all test cases
- ⏳ All 4 phases have clear tasks
- ⏳ All path changes documented

### Quality Gates
- [ ] All configuration files updated
- [ ] All Python code verified
- [ ] 100% test pass rate
- [ ] Zero broken path references
- [ ] Setup scripts functional
- [ ] Documentation current

### Team Readiness
- [ ] All tasks assigned
- [ ] Team trained on changes
- [ ] Migration guide available
- [ ] FAQ documented
- [ ] Rollback plan ready

---

## Notes & Comments

### Current Progress
- proposal.md: ✅ Complete (280+ lines)
- tasks.md: ✅ Complete (400+ lines)
- todo.md: ✅ Creating now
- spec.md: ⏳ Needed
- test_plan.md: ⏳ Needed

### Open Questions
- Should we keep symlinks to old agent/models/ for backward compat?
- Should this be done before or after modularize-agent change?
- Do we need data migration for existing model caches?

### Dependencies
- Complements `modularize-agent` OpenSpec change
- Should coordinate with `modular-api-structure` change
- May impact setup.ps1 and setup.sh scripts

### Related Documentation
- See proposal.md for full problem statement
- See tasks.md for detailed task breakdown
- See specs/ directory for technical specifications

---

**Last Updated**: October 21, 2025  
**Updated By**: Obsidian AI Agent  
**Next Action**: Create spec.md and test_plan.md, then run Step 3 and Step 5
