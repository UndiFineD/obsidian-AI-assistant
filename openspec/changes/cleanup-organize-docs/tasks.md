# Cleanup & Organize Docs - Tasks

**Change ID**: cleanup-organize-docs  
**Total Tasks**: 8  
**Total Subtasks**: 45  
**Estimated Effort**: 3-5 hours  
**Timeline**: 1 day  

---

## 📋 Task List

### TASK 1: Inventory & Categorize Files (1 hour)
**Subtasks**:
- [ ] List all markdown files in root directory
- [ ] Categorize as: KEEP, MOVE, or DELETE
- [ ] Create categorization spreadsheet
- [ ] Identify duplicates and consolidation candidates
- [ ] Check if any "DELETE" files contain critical info
- [ ] Document rationale for each file's category
- [ ] Get stakeholder review on categorization
- [ ] Finalize categorization list

**Success Criteria**:
- All files categorized
- No questions about categorization
- Ready to proceed with structure creation

---

### TASK 2: Design & Create Directory Structure (0.5 hours)
**Subtasks**:
- [ ] Create `docs/` directory
- [ ] Create `docs/getting-started/` subdirectory
- [ ] Create `docs/phase-1/` subdirectory
- [ ] Create `docs/phase-2/` subdirectory
- [ ] Create `docs/guides/` subdirectory
- [ ] Create `docs/architecture/` subdirectory
- [ ] Create `docs/production/` subdirectory
- [ ] Create `docs/reference/` subdirectory
- [ ] Create `docs/README.md` (navigation guide)

**Success Criteria**:
- All directories created
- Clear, logical hierarchy
- Ready for file moves

---

### TASK 3: Consolidate & Move Documentation Files (1 hour)
**Subtasks**:
- [ ] Consolidate Phase 1 docs into single PHASE_1_SUMMARY.md
- [ ] Move consolidated Phase 1 to docs/phase-1/
- [ ] Move Phase 2 planning docs to docs/phase-2/
  - [ ] PHASE_2_STARTER.md → OVERVIEW.md
  - [ ] PHASE_2_OPTIONS.md → OPTIONS.md
  - [ ] PHASE_2_PLAN.md → PLAN.md
  - [ ] PHASE2_READY_FOR_DECISION.md → DECISION_FRAMEWORK.md
  - [ ] FINAL_SESSION_SUMMARY_PROPOSALS.md → SUMMARY.md
- [ ] Move Git guides to docs/guides/
  - [ ] GIT_BRANCHES_STATUS.md
  - [ ] GIT_PULL_REQUEST.md
  - [ ] GIT_WORKFLOW_REFERENCE.md
- [ ] Move architecture docs to docs/architecture/
  - [ ] Architecture overview
  - [ ] Design documents
- [ ] Move production docs to docs/production/
  - [ ] PRODUCTION_READINESS_V0.1.35.md
- [ ] Move 00_START_HERE.md to docs/getting-started/
- [ ] Move other project guides to docs/guides/

**Success Criteria**:
- All files moved
- Directory structure follows plan
- No files missed

---

### TASK 4: Delete Redundant & Celebration Files (0.5 hours)
**Subtasks**:
- [ ] Delete 🎉_FINAL_CELEBRATION_100_PERCENT_COMPLETE.md
- [ ] Delete 🎉_SESSION_COMPLETE_FINAL_SUMMARY.md
- [ ] Delete all COMPLETION_CERTIFICATE_*.md files
- [ ] Delete all FINAL_*.md files (status/celebration)
- [ ] Delete all SESSION_*.md files (except if critical)
- [ ] Delete all DELIVERABLES_*.md files
- [ ] Delete all EXECUTIVE_SUMMARY_*.md files (keep strategy docs)
- [ ] Delete DOCUMENTATION_*.md duplicates
- [ ] Delete PROJECT_COMPLETE_LIVE.md
- [ ] Delete READY_FOR_COMMIT.md
- [ ] Delete READY_TO_DEPLOY.md
- [ ] Delete other celebration/status files
- [ ] Verify git history preserves all deleted content
- [ ] Confirm no critical info lost

**Success Criteria**:
- All redundant files deleted
- Root is clean
- No critical info lost (all in git history)

---

### TASK 5: Update Internal Links & References (1 hour)
**Subtasks**:
- [ ] Update README.md with docs/ structure guide
- [ ] Update links in PHASE_2_*.md files (now in docs/phase-2/)
- [ ] Update links in GIT_*.md files (now in docs/guides/)
- [ ] Update links in setup scripts if they reference docs
- [ ] Update links in Makefile if applicable
- [ ] Search for hardcoded file references in code
- [ ] Update references in openspec/ docs
- [ ] Update references in plugin/ code
- [ ] Create docs/README.md with:
  - [ ] Overview of doc structure
  - [ ] Quick links to common docs
  - [ ] Navigation guide for contributors
  - [ ] Links to openspec/
- [ ] Test all links manually

**Success Criteria**:
- No broken links
- All references updated
- Contributors can navigate easily

---

### TASK 6: Update Root README.md (0.5 hours)
**Subtasks**:
- [ ] Add section: "Documentation Structure"
- [ ] Add links to docs/README.md
- [ ] Update any outdated information in root README
- [ ] Add clear "Getting Started" link to docs/getting-started/
- [ ] Add "Governance" section linking to openspec/
- [ ] Remove outdated status information
- [ ] Keep README focused on: purpose, quick start, structure
- [ ] Remove any celebration language

**Success Criteria**:
- README is clean and focused
- Clear navigation to docs
- Professional tone

---

### TASK 7: Verify & Test (0.5 hours)
**Subtasks**:
- [ ] Run link checker on all markdown files
- [ ] Manually test critical navigation paths
- [ ] Verify openspec/ structure unchanged
- [ ] Check git diff for expected changes
- [ ] Confirm no files lost (use git log)
- [ ] Test cloning repo fresh and finding key docs
- [ ] Verify build scripts still work
- [ ] Check that plugin can still find resources

**Success Criteria**:
- No broken links
- All navigation works
- Nothing broken by reorganization

---

### TASK 8: Final Cleanup & Commit (1 hour)
**Subtasks**:
- [ ] Run code style checks
- [ ] Remove any temporary files created
- [ ] Add all changes to git: `git add -A`
- [ ] Create comprehensive commit message:
  - [ ] List deleted files
  - [ ] List moved directories
  - [ ] Explain structure
- [ ] Stage commit: `git commit -m "cleanup: organize docs into hierarchical structure"`
- [ ] Push to feature branch
- [ ] Create PR with before/after screenshots
- [ ] Gather team feedback
- [ ] Address review comments
- [ ] Merge to main

**Success Criteria**:
- All changes committed
- PR created and reviewed
- Merged to main

---

## 📊 Summary

| Task | Duration | Subtasks | Status |
|------|----------|----------|--------|
| 1. Inventory | 1h | 8 | 📋 |
| 2. Create Structure | 0.5h | 9 | 📋 |
| 3. Move Files | 1h | 12 | 📋 |
| 4. Delete Redundant | 0.5h | 14 | 📋 |
| 5. Update Links | 1h | 12 | 📋 |
| 6. Update README | 0.5h | 8 | 📋 |
| 7. Verify | 0.5h | 8 | 📋 |
| 8. Commit | 1h | 14 | 📋 |
| **TOTAL** | **5.5h** | **85** | **📋** |

---

## 🎯 Definition of Done

- [x] All files categorized and accounted for
- [x] Directory structure created
- [x] All non-OpenSpec docs moved to docs/
- [x] All redundant celebration files deleted
- [x] All internal links updated
- [x] README.md updated
- [x] All links verified
- [x] Changes committed and pushed
- [x] PR reviewed and merged

---

## ✅ Success Criteria

1. **Root directory**: Contains only ~10 essential files
2. **docs/ structure**: Clear, hierarchical, easy to navigate
3. **No broken links**: All references updated
4. **OpenSpec isolated**: Unchanged, clear governance boundary
5. **Clean history**: Git preserves all deleted content
6. **Reduced noise**: 20-30 fewer files in root
7. **Improved clarity**: Contributors know where docs are

---

## 📝 Notes

- All deleted files are preserved in git history
- No data loss - pure reorganization
- Can be reverted if needed
- Future docs should go in docs/ subdirectory
- OpenSpec changes stay isolated in openspec/

---

**Ready for Implementation** ✅
