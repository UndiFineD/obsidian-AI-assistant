# OpenSpec Documentation Governance
[![OpenSpec Validation](https://github.com/kdejonge/obsidian-llm-assistant/actions/workflows/openspec-pr-validate.yml/badge.svg)](https://github.com/kdejonge/obsidian-llm-assistant/actions/workflows/openspec-pr-validate.yml)

## 📊 Governance Metrics Dashboard

| Metric                      | Value                |
|----------------------------|----------------------|
| **Total Specs**            | 1 (project-documentation) |
| **Active Changes**         | 54                   |
| **Validation Status**      | ✅ 55/55 passed (100%)|
| **Last Validation**        | 2025-10-16           |
| **Contributor Onboarding** | < 1 hour             |
| **Change Review Time**     | < 24 hours           |
| **Validation Pass Rate**   | > 95%                |
| **Governed Docs Consistency** | 100%               |

Welcome to the OpenSpec documentation governance system for the Obsidian AI Assistant project. This directory contains all governed specifications, change proposals, and governance documentation.

## 🎯 Quick Start

### For Contributors

1. **Read the governance guide**: Start with [`AGENTS.md`](./AGENTS.md) for AI agent instructions and governance workflows
2. **Review existing specs**: Check [`specs/`](./specs/) for baseline capability specifications
3. **Browse changes**: See [`changes/`](./changes/) for active change proposals
4. **Validate your work**: Run `openspec validate --strict` before submitting

### For Reviewers

1. **Review change proposals**: Check [`changes/*/proposal.md`](./changes/) for pending changes
2. **Validate changes**: Run `openspec validate --strict --changes` to validate all proposals
3. **Check tasks**: Review [`changes/*/tasks.md`](./changes/) for implementation checklists
4. **Apply approved changes**: Use `openspec apply <change-id>` to merge approved changes

## 📁 Directory Structure

```
openspec/
├── README.md              # This file - entry point and overview
├── AGENTS.md              # AI agent instructions and governance workflows
├── project.md             # Project context and OpenSpec configuration
├── specs/                 # Baseline capability specifications
│   ├── project-documentation/
│   │   └── spec.md        # Documentation governance capability spec
│   └── project-documentation.md  # Capability overview
├── changes/               # Active change proposals (pending/in-progress)
│   ├── update-doc-readme/
│   │   ├── proposal.md    # Change justification and impact
│   │   ├── tasks.md       # Implementation checklist
│   │   └── MODIFIED.md    # Delta spec for modified requirements
│   └── ...
├── archive/               # Archived/completed changes (historical record)
│   └── YYYY-MM-DD/        # Changes archived by date
└── docs/                  # Governance documentation (planned)

    ├── contributor-guide.md
    ├── change-patterns.md
    └── troubleshooting.md
```

## 🔄 Change Workflow

### Creating a Change Proposal

```bash
# 1. Create change directory
mkdir openspec/changes/update-doc-<filename>

# 2. Create proposal
# Document: Why, What Changes, Impact, Tasks
openspec/changes/update-doc-<filename>/proposal.md

# 3. Create task list
openspec/changes/update-doc-<filename>/tasks.md

# 4. Create delta spec (ADDED, MODIFIED, or REMOVED)
openspec/changes/update-doc-<filename>/MODIFIED.md

# 5. Validate
openspec validate --strict update-doc-<filename>
```

### Change Proposal Requirements

Every change **MUST** include:

1. **`proposal.md`**: Justification, scope, and impact analysis
2. **`tasks.md`**: Implementation checklist with validation steps
3. **Delta spec**: One or more of `ADDED.md`, `MODIFIED.md`, `REMOVED.md`

### Delta Spec Types

- **`ADDED.md`**: New requirements or scenarios (not in baseline)
- **`MODIFIED.md`**: Changed requirements (reference baseline requirement)
- **`REMOVED.md`**: Deprecated/removed requirements (reference baseline)

## ✅ Validation

### Validate All

```bash
# Validate everything (specs + changes)
openspec validate --strict

# JSON output for automation
openspec validate --strict --json
```

### Validate Specific Items

```bash
# Validate all changes only
openspec validate --strict --changes

# Validate all specs only
openspec validate --strict --specs

# Validate specific change
openspec validate --strict update-doc-readme
```

### Validation Requirements

**Strict mode checks:**
- ✅ All requirements contain SHALL or MUST keyword
- ✅ All scenarios use WHEN/THEN format
- ✅ Delta specs reference baseline requirements (for MODIFIED)
- ✅ All proposal.md files have required sections
- ✅ All tasks.md files have validation steps
- ✅ Markdown formatting (via markdownlint)

## 📋 Governed Documentation

The following documentation is governed by OpenSpec change proposals:

### Core Documentation

- **README.md**: Project overview and getting started
- **AGENTS.md**: AI agent instructions
- **CLAUDE.md**: Claude-specific AI integration

### Specifications (docs/)

- **SYSTEM_ARCHITECTURE_SPECIFICATION.md**: System design
- **SECURITY_SPECIFICATION.md**: Security requirements
- **TESTING_STANDARDS_SPECIFICATION.md**: Test requirements
- **PERFORMANCE_REQUIREMENTS_SPECIFICATION.md**: Performance SLAs
- **ENTERPRISE_FEATURES_SPECIFICATION.md**: Enterprise capabilities
- **DEPLOYMENT_SPECIFICATION.md**: Deployment procedures
- **PLUGIN_INTEGRATION_SPECIFICATION.md**: Plugin architecture
- **DATA_MODELS_SPECIFICATION.md**: API and data models
- **COMPREHENSIVE_SPECIFICATION.md**: Complete system spec

### Plugin Documentation

- **.obsidian/plugins/obsidian-ai-assistant/SETUP.md**
- **.obsidian/plugins/obsidian-ai-assistant/SETUP_COMPLETE.md**

### GitHub Integration

- **.github/copilot-instructions.md**: GitHub Copilot guidelines

### OpenSpec Governance

- **openspec/project.md**: OpenSpec project configuration
- **openspec/AGENTS.md**: OpenSpec governance instructions

See [`specs/project-documentation/spec.md`](./specs/project-documentation/spec.md) for the complete list and governance requirements.

## 🎓 Learning Resources

### For New Contributors

1. **Start here**: [`docs/contributor-guide.md`](./docs/contributor-guide.md) _(planned)_
2. **Change patterns**: [`docs/change-patterns.md`](./docs/change-patterns.md) _(planned)_
3. **Troubleshooting**: [`docs/troubleshooting.md`](./docs/troubleshooting.md) _(planned)_
4. **Governance workflow**: [`AGENTS.md`](./AGENTS.md)

### For AI Agents

- **Primary instructions**: [`AGENTS.md`](./AGENTS.md)
- **Project context**: [`project.md`](./project.md)
- **Capability specs**: [`specs/`](./specs/)

## 🔧 Common Tasks

### Review Pending Changes

```bash
# List all changes
ls openspec/changes/

# Validate all pending changes
openspec validate --strict --changes

# Review specific change
cat openspec/changes/update-doc-readme/proposal.md
```

### Apply Approved Changes

```bash
# Apply a specific change
openspec apply update-doc-readme

# Apply with dry-run (preview only)
openspec apply update-doc-readme --dry-run
```

### Archive Completed Changes

```bash
# Archive a completed change
openspec archive update-doc-readme

# Archive with date
openspec archive update-doc-readme --date 2025-10-16
```

## 📊 Governance Metrics

### Success Criteria

- ✅ **Contributor onboarding**: < 1 hour to first successful change proposal
- ✅ **Validation pass rate**: > 95% for submitted changes
- ✅ **Documentation consistency**: 100% governed docs follow spec requirements
- ✅ **Change review time**: < 24 hours for typical documentation changes

### Current Status

- **Total specs**: 1 (project-documentation)
- **Active changes**: 54 (all validated successfully)
- **Validation status**: ✅ 55/55 passed (100%)
- **Last validation**: 2025-10-16

## 🤝 Contributing

### Before You Start

1. Read the [contributor guide](./docs/contributor-guide.md) _(planned)_
2. Review existing [change proposals](./changes/)
3. Check [baseline specifications](./specs/)
4. Run `openspec validate --strict` to ensure your environment is set up

### Submitting Changes

1. Create change directory with `proposal.md`, `tasks.md`, and delta spec(s)
2. Validate with `openspec validate --strict <change-id>`
3. Fix any validation errors
4. Submit for review (PR or issue)
5. Address review feedback
6. Apply with `openspec apply <change-id>` after approval

### Getting Help

- **Validation errors**: See [troubleshooting guide](./docs/troubleshooting.md) _(planned)_
- **Change patterns**: Review [change patterns documentation](./docs/change-patterns.md) _(planned)_
- **AI agents**: Consult [AGENTS.md](./AGENTS.md)
- **Questions**: Open a GitHub issue

## 📜 Governance Philosophy

OpenSpec governance ensures:

1. **Consistency**: All documentation follows the same standards
2. **Traceability**: Every change is documented, reviewed, and tracked
3. **Quality**: Validation enforces completeness and formatting
4. **Collaboration**: Review processes encourage knowledge sharing
5. **Evolution**: Documentation grows with the project

## 🔗 Related Documentation

- **Main README**: [`../README.md`](../README.md) - Project overview
- **System Architecture**: [`../docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md`](../docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md)
- **Testing Guide**: [`../docs/TESTING_GUIDE.md`](../docs/TESTING_GUIDE.md)
- **Copilot Instructions**: [`../.github/copilot-instructions.md`](../.github/copilot-instructions.md)

---

**Last Updated**: October 16, 2025  
**Governance Version**: 1.0  
**OpenSpec Compliance**: ✅ Strict validation passing
